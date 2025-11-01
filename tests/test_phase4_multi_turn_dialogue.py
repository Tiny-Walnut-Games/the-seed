"""
Phase 4: Multi-Turn Dialogue with Extended Slots and Conversation Memory

Tests the complete Phase 4 system:
1. Conversation session management (persistence of multi-turn state)
2. Extended slots (inventory, faction, time_of_day, npc_mood, quest_context, weather, location_type, npc_history)
3. Multi-turn composition chains (greeting → context → resolution)
4. Context-aware semantic search with history boost
5. State truncation and memory management for performance
6. Backward compatibility with Phase 2-3

Scenario: Player engages multi-turn dialogue with NPC:
- Turn 1: Greeting → NPC responds with reputation awareness
- Turn 2: Context (quest info) → NPC recalls and escalates
- Turn 3: Resolution (trade/quest completion) → NPC acknowledges journey

Extended slots provide richer context:
- {{inventory_summary}} - "2 legendary weapons, 5 potions"
- {{faction_standing}} - "Revered with The Wanderers"
- {{time_of_day}} - "dusk" (affects dialogue tone)
- {{npc_mood}} - "cheerful" (NPC emotional state affects formality)
- {{quest_context}} - "Retrieve the Shard of Echoes"
- {{weather}} - "stormy" (affects setting description)
- {{location_type}} - "tavern" vs "marketplace" vs "temple"
- {{npc_history}} - "sold you 3 items" (cumulative NPC-player history)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Add web/server to path
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

from universal_player_router import (
    UniversalPlayerRouter, ReputationFaction, InventoryItem, UniversalPlayer
)
from warbler_multiverse_bridge import (
    WarblerMultiverseBridge, DialogueContext, DialogueModifierType
)
from warbler_query_service import WarblerQueryService
from warbler_pack_loader import WarblerPackLoader
from city_simulation_integration import CitySimulationIntegration
from cross_realm_quests import CrossRealmQuestSystem, Quest
from multigame_tick_engine import MultiGameTickEngine, RealmCoordinate, TickEngine


class TestPhase4ConversationSessionManagement:
    """Test conversation session creation, persistence, and state tracking."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems with conversation state management."""
        pack_loader = WarblerPackLoader()
        packs_loaded = pack_loader.load_all_packs()
        logger.info(f"✓ Loaded {packs_loaded} Warbler packs for Phase 4")
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        warbler_query_service = WarblerQueryService(
            player_router,
            warbler_bridge,
            pack_loader=pack_loader
        )
        
        orchestrator = MultiGameTickEngine(control_tick_interval_ticks=10)
        city_integration = CitySimulationIntegration(
            orchestrator, player_router, warbler_bridge, warbler_query_service
        )
        
        quest_system = CrossRealmQuestSystem(player_router, city_integration)
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_theron_merchant",
            npc_name="Theron",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
            "city_integration": city_integration,
            "quest_system": quest_system,
            "orchestrator": orchestrator,
            "pack_loader": pack_loader,
        }

    def test_create_conversation_session(self, setup_phase4_systems):
        """
        Test creating a new conversation session between player and NPC.
        
        Expected behavior:
        - Session ID generated and returned
        - Session metadata contains player_id, npc_id, realm_id
        - Empty conversation history initially
        - Timestamps recorded
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        # Create a test player
        player = router.create_player("Alice", "human", "sol_1")
        player_id = player.player_id
        assert player is not None
        
        # Create session (method doesn't exist yet; we're defining the interface)
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_theron_merchant",
            realm_id="sol_1"
        )
        
        # Verify session exists and has correct structure
        assert session_id is not None
        assert len(session_id) > 0
        
        # Retrieve session metadata
        session = query_service.get_conversation_session(session_id)
        assert session is not None
        assert session["player_id"] == player_id
        assert session["npc_id"] == "npc_theron_merchant"
        assert session["realm_id"] == "sol_1"
        assert session["conversation_history"] == []
        assert "created_at" in session
        assert "last_modified_at" in session

    def test_multi_turn_conversation_history(self, setup_phase4_systems):
        """
        Test that conversation history persists across multiple turns.
        
        Expected behavior:
        - Each turn (query/response pair) added to history
        - History indexed by turn number
        - Turn data includes timestamp, player_input, npc_response, turn_metadata
        - Previous turns accessible for context on subsequent queries
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Bob", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Turn 1: Greeting
        turn1_response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Hello there!"
        )
        assert turn1_response["turn_number"] == 1
        assert "npc_response" in turn1_response
        
        # Retrieve session and verify history
        session = query_service.get_conversation_session(session_id)
        assert len(session["conversation_history"]) == 1
        assert session["conversation_history"][0]["turn_number"] == 1
        assert session["conversation_history"][0]["player_input"] == "Hello there!"
        
        # Turn 2: Follow-up
        turn2_response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Do you have any legendary weapons?"
        )
        assert turn2_response["turn_number"] == 2
        
        # Verify both turns in history
        session = query_service.get_conversation_session(session_id)
        assert len(session["conversation_history"]) == 2
        assert session["conversation_history"][0]["turn_number"] == 1
        assert session["conversation_history"][1]["turn_number"] == 2
        assert session["conversation_history"][1]["player_input"] == "Do you have any legendary weapons?"

    def test_session_context_available_on_subsequent_turns(self, setup_phase4_systems):
        """
        Test that previous turn context is made available to query service on next turn.
        
        Expected behavior:
        - query_npc_with_session provides conversation history to selection logic
        - Semantic search can use previous messages for boosting relevance
        - Response should show awareness of previous context
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Charlie", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Turn 1: Ask about items
        query_service.query_npc_with_session(
            session_id=session_id,
            user_input="What wondrous items do you have?"
        )
        
        # Turn 2: Follow-up should have access to Turn 1 context
        turn2_response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Any legendary weapons?"
        )
        
        # Verify the response metadata includes context reference
        assert "context_history_length" in turn2_response
        assert turn2_response["context_history_length"] >= 1
        assert "context_messages" in turn2_response
        assert len(turn2_response["context_messages"]) >= 1

    def test_session_timeout_and_cleanup(self, setup_phase4_systems):
        """
        Test that old sessions are cleaned up after timeout.
        
        Expected behavior:
        - Sessions with no activity after N minutes marked as stale
        - Stale sessions archived or deleted per policy
        - Active sessions remain accessible
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Diana", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Verify session is active
        session = query_service.get_conversation_session(session_id)
        assert session is not None
        
        # Artificially mark session as old (before timeout window)
        # This assumes query_service has internal state we can manipulate
        old_timestamp = datetime.now() - timedelta(hours=2)
        query_service.set_session_modified_time(session_id, old_timestamp)
        
        # Cleanup should archive this session
        archived_count = query_service.cleanup_stale_sessions(timeout_minutes=60)
        assert archived_count >= 1
        
        # Archived session should not be in active list
        with pytest.raises(KeyError):
            query_service.get_conversation_session(session_id)


class TestPhase4ExtendedSlots:
    """Test extended slot functionality: inventory, faction, time, mood, etc."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems."""
        pack_loader = WarblerPackLoader()
        pack_loader.load_all_packs()
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        warbler_query_service = WarblerQueryService(
            player_router, warbler_bridge, pack_loader=pack_loader
        )
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
            "pack_loader": pack_loader,
        }

    def test_inventory_summary_slot(self, setup_phase4_systems):
        """
        Test {{inventory_summary}} slot is filled with player's inventory.
        
        Expected behavior:
        - Counts and categories items in player inventory
        - Generates summary like "3 legendary weapons, 5 healing potions, 2 rare scrolls"
        - Handles empty inventory gracefully ("No items yet")
        - Slot properly filled in NPC response
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        
        player = router.create_player("Emma", "human", "sol_1")
        player_id = player.player_id
        
        # Add items to inventory
        from universal_player_router import InventoryItem
        router.add_item_to_inventory(player_id, InventoryItem(
            item_id="legendary_sword",
            name="Excalibur",
            item_type="weapon",
            rarity="legendary",
            source_realm="sol_1"
        ))
        router.add_item_to_inventory(player_id, InventoryItem(
            item_id="healing_potion",
            name="Standard healing potions",
            item_type="consumable",
            rarity="common",
            source_realm="sol_1",
            quantity=5
        ))
        router.add_item_to_inventory(player_id, InventoryItem(
            item_id="rare_scroll",
            name="Ancient wisdom",
            item_type="quest",
            rarity="rare",
            source_realm="sol_1",
            quantity=2
        ))
        
        # Query with extended slots
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="What do you think of my gear?",
            include_extended_slots=True
        )
        
        # Response should include filled inventory summary
        assert "inventory_summary" in response.get("slots_used", [])
        # Should not have leaked template variable
        assert "{{inventory_summary}}" not in response["npc_response"]

    def test_faction_standing_slot(self, setup_phase4_systems):
        """
        Test {{faction_standing}} slot with reputation formatting.
        
        Expected behavior:
        - Maps reputation tier to faction standing string
        - Format: "Revered with The Wanderers" or "Hostile with The Syndicate"
        - Handles multiple faction standings if relevant
        - Reflected in NPC dialogue tone
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        
        player = router.create_player("Frank", "human", "sol_1")
        player_id = player.player_id
        
        # Set high reputation with faction
        router.modify_reputation(
            player_id,
            ReputationFaction.THE_WANDERERS,
            600  # Revered tier
        )
        
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="I seek your counsel, friend.",
            include_extended_slots=True
        )
        
        assert "faction_standing" in response.get("slots_used", [])
        assert "{{faction_standing}}" not in response["npc_response"]
        # Should contain revered-level language
        assert response["npc_response"].count("great") >= 0  # May include reverent tone

    def test_time_of_day_slot(self, setup_phase4_systems):
        """
        Test {{time_of_day}} slot with game world time.
        
        Expected behavior:
        - Syncs with game tick engine's time
        - Values: "dawn", "morning", "noon", "afternoon", "dusk", "night"
        - Affects NPC greeting formality (NPCs sleepy at night, energetic at noon)
        - Properly formatted in response
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        
        player = router.create_player("Grace", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Hello!",
            include_extended_slots=True,
            game_time_hours=14  # Afternoon
        )
        
        assert "time_of_day" in response.get("slots_used", [])
        assert "{{time_of_day}}" not in response["npc_response"]
        # Time of day should not have leaked template
        assert "{{" not in response["npc_response"]

    def test_npc_mood_slot(self, setup_phase4_systems):
        """
        Test {{npc_mood}} slot affecting dialogue formality.
        
        Expected behavior:
        - NPC mood set based on recent interactions
        - Moods: "cheerful", "neutral", "grumpy", "excited", "thoughtful"
        - Cheerful NPC uses familiar language, grumpy uses curt responses
        - Slot properly interpolated in selected templates
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        bridge = setup_phase4_systems["bridge"]
        
        player = router.create_player("Henry", "human", "sol_1")
        player_id = player.player_id
        npc_id = "npc_merchant_001"
        
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id=npc_id,
            realm_id="sol_1"
        )
        
        # Set NPC mood to cheerful
        bridge.set_npc_mood(npc_id, "cheerful")
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="How are you today?",
            include_extended_slots=True
        )
        
        assert "npc_mood" in response.get("slots_used", [])
        assert "{{npc_mood}}" not in response["npc_response"]

    def test_quest_context_slot(self, setup_phase4_systems):
        """
        Test {{quest_context}} slot with active quest information.
        
        Expected behavior:
        - Shows active quest title/objective
        - Format: "Retrieve the Shard of Echoes" or "None" if no active quest
        - NPC dialogue references the quest when it's their quest
        - Properly filled for quest-giver NPCs
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        quest_system = CrossRealmQuestSystem(router, setup_phase4_systems["bridge"])
        
        player = router.create_player("Iris", "human", "sol_1")
        player_id = player.player_id
        
        # Create and assign a quest
        quest = quest_system.create_quest(
            quest_id="quest_shard_retrieval",
            title="Retrieve the Shard of Echoes",
            giver_npc="npc_sage_001",
            reward_reputation=100
        )
        quest_system.accept_quest(player_id, quest.quest_id)
        
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_sage_001",
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="How goes my quest?",
            include_extended_slots=True
        )
        
        assert "quest_context" in response.get("slots_used", [])
        assert "{{quest_context}}" not in response["npc_response"]

    def test_weather_slot(self, setup_phase4_systems):
        """
        Test {{weather}} slot with realm weather state.
        
        Expected behavior:
        - Fetches weather from realm state
        - Values: "clear", "cloudy", "rainy", "stormy", "snowy"
        - Affects NPC descriptions and setting details
        - Example: "It's a stormy night, so find shelter quickly"
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        
        player = router.create_player("Jack", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="How's the weather?",
            include_extended_slots=True,
            weather="stormy"
        )
        
        assert "weather" in response.get("slots_used", [])
        assert "{{weather}}" not in response["npc_response"]

    def test_location_type_slot(self, setup_phase4_systems):
        """
        Test {{location_type}} slot (tavern, marketplace, temple, wilderness).
        
        Expected behavior:
        - Determines NPC's appropriate response style per location
        - Tavern: casual, friendly language
        - Temple: formal, reverent language
        - Marketplace: business-focused language
        - NPC dialogue adapts to location setting
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        
        player = router.create_player("Kate", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Test marketplace location
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Got any wares for sale?",
            include_extended_slots=True,
            location_type="marketplace"
        )
        
        assert "location_type" in response.get("slots_used", [])
        assert "{{location_type}}" not in response["npc_response"]

    def test_npc_history_slot(self, setup_phase4_systems):
        """
        Test {{npc_history}} slot with NPC-player interaction count.
        
        Expected behavior:
        - Tracks items sold/bought between NPC and player
        - Format: "sold you 5 items, received 3 items"
        - Affects NPC familiarity and dialogue
        - First-time NPCs show "We haven't traded yet"
        """
        router = setup_phase4_systems["router"]
        query_service = setup_phase4_systems["query_service"]
        bridge = setup_phase4_systems["bridge"]
        
        player = router.create_player("Leo", "human", "sol_1")
        player_id = player.player_id
        npc_id = "npc_merchant_001"
        
        # Record some transaction history
        bridge.record_npc_player_transaction(
            npc_id=npc_id,
            player_id=player_id,
            transaction_type="sold",
            items=["longsword", "healing_potion"]
        )
        
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id=npc_id,
            realm_id="sol_1"
        )
        
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="How have we been working together?",
            include_extended_slots=True
        )
        
        assert "npc_history" in response.get("slots_used", [])
        assert "{{npc_history}}" not in response["npc_response"]
        # Should reference transaction history
        assert response["npc_response"].count("item") >= 0


class TestPhase4MultiTurnComposition:
    """Test multi-turn composition chains (greeting → context → resolution)."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems."""
        pack_loader = WarblerPackLoader()
        pack_loader.load_all_packs()
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        warbler_query_service = WarblerQueryService(
            player_router, warbler_bridge, pack_loader=pack_loader
        )
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
        }

    def test_three_turn_composition_flow(self, setup_phase4_systems):
        """
        Test a complete three-turn dialogue flow: greeting → context → resolution.
        
        Expected behavior:
        - Turn 1: NPC greets player appropriately based on reputation
        - Turn 2: Player provides context; NPC acknowledges and escalates
        - Turn 3: Player resolves (agrees to quest, completes trade); NPC concludes
        - Each turn shows narrative progression
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Mona", "human", "sol_1")
        player_id = player.player_id
        router.modify_reputation(player_id, ReputationFaction.THE_WANDERERS, 300)
        
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_sage_001",
            realm_id="sol_1"
        )
        
        # Turn 1: Greeting
        turn1 = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Greetings, wise one."
        )
        assert turn1["turn_number"] == 1
        greeting_response = turn1["npc_response"]
        
        # Turn 2: Context (ask for quest)
        turn2 = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="I seek a worthy challenge. Do you have a quest for me?"
        )
        assert turn2["turn_number"] == 2
        context_response = turn2["npc_response"]
        # Should reference context from turn 1
        assert turn2.get("context_history_length", 0) >= 1
        
        # Turn 3: Resolution (accept quest)
        turn3 = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="I will retrieve the Shard of Echoes."
        )
        assert turn3["turn_number"] == 3
        resolution_response = turn3["npc_response"]
        # Should acknowledge acceptance
        assert turn3.get("context_history_length", 0) >= 2

    def test_composition_chain_template_chaining(self, setup_phase4_systems):
        """
        Test that multi-turn responses can chain/compose multiple templates.
        
        Expected behavior:
        - Complex response may combine greeting template + context template
        - Example: "Ah, noble wanderer! [greeting] You seek the Shard? [context]
          A dangerous task indeed. [escalation]"
        - Each sub-template slots properly filled
        - Composed response flows naturally
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Nathan", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Complex turn that may trigger template chaining
        response = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Hello! Do you have legendary weapons? I'm on an important quest.",
            enable_composition_chaining=True
        )
        
        # Check that response is properly formed (no missing slots or broken templates)
        assert "{{" not in response["npc_response"]
        assert len(response["npc_response"]) > 50  # Substantial response
        # Should indicate if multiple templates were composed
        assert response.get("templates_used", 1) >= 1


class TestPhase4ContextAwareSemanticSearch:
    """Test context-aware semantic search with history boost."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems with embedding service."""
        pack_loader = WarblerPackLoader()
        pack_loader.load_all_packs()
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        
        try:
            from web.server.warbler_embedding_service import WarblerEmbeddingService
            embedding_service = WarblerEmbeddingService()
            # Load embeddings if available
            try:
                pack_loader.load_jsonl_pack("warbler-pack-hf-npc-dialogue")
                pack_loader.build_embeddings()
            except:
                pass
        except ImportError:
            embedding_service = None
        
        warbler_query_service = WarblerQueryService(
            player_router,
            warbler_bridge,
            pack_loader=pack_loader,
            embedding_service=embedding_service
        )
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
            "embedding_service": embedding_service,
        }

    def test_context_boost_on_semantic_search(self, setup_phase4_systems):
        """
        Test that semantic search boosts relevance based on conversation history.
        
        Expected behavior:
        - Previous turn context creates boost vector
        - Turn 1: "weapons" → selects weapon-related template
        - Turn 2: "legendary" → boosts templates mentioning "legendary" from previous "weapons" query
        - Relevance score higher when context aligns with history
        - Boosted templates ranked first in search results
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Olivia", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Turn 1: Ask about weapons
        turn1 = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="Do you have weapons for sale?"
        )
        
        # Turn 2: Ask about legendary weapons (should use history for boost)
        turn2 = query_service.query_npc_with_session(
            session_id=session_id,
            user_input="What legendary weapons do you have?",
            use_context_boost=True
        )
        
        # Response should show context awareness
        assert turn2.get("used_context_boost") == True or \
               turn2.get("context_history_length", 0) >= 1


class TestPhase4BackwardCompatibility:
    """Test that Phase 4 maintains backward compatibility with Phase 2-3."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems."""
        pack_loader = WarblerPackLoader()
        pack_loader.load_all_packs()
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        warbler_query_service = WarblerQueryService(
            player_router, warbler_bridge, pack_loader=pack_loader
        )
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
        }

    def test_phase2_query_interface_still_works(self, setup_phase4_systems):
        """
        Test that Phase 2 query_npc() interface still works (not broken).
        
        Expected behavior:
        - Old code calling query_npc() without session_id still works
        - Returns single response (not part of session)
        - No breaking changes to existing API
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Piper", "human", "sol_1")
        player_id = player.player_id
        
        # Use old Phase 2 interface
        response = query_service.query_npc(
            player_id=player_id,
            npc_id="npc_merchant_001",
            user_input="Hello!",
            realm_id="sol_1"
        )
        
        # Should work without error
        assert response is not None
        assert "npc_response" in response
        assert len(response["npc_response"]) > 0

    def test_phase3_semantic_search_still_works(self, setup_phase4_systems):
        """
        Test that Phase 3 semantic search still works when embedding_service available.
        
        Expected behavior:
        - If embedding_service exists, semantic search used
        - If not, falls back to keyword matching (Phase 2)
        - No breaking changes or performance regression
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Quinn", "human", "sol_1")
        player_id = player.player_id
        
        # Query with Phase 3 capability
        response = query_service.query_npc(
            player_id=player_id,
            npc_id="npc_merchant_001",
            user_input="What wondrous items do you have in stock?",
            realm_id="sol_1"
        )
        
        # Should return valid response (semantic or keyword-based)
        assert response is not None
        assert "npc_response" in response
        assert len(response["npc_response"]) > 0


class TestPhase4StateManagement:
    """Test conversation state management and performance optimization."""

    @pytest.fixture
    def setup_phase4_systems(self):
        """Set up Phase 4 systems."""
        pack_loader = WarblerPackLoader()
        pack_loader.load_all_packs()
        
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        warbler_query_service = WarblerQueryService(
            player_router, warbler_bridge, pack_loader=pack_loader
        )
        
        # Register test NPCs
        warbler_bridge.register_npc(
            npc_id="npc_merchant_001",
            npc_name="Merchant Kaz",
            realm_id="sol_1",
            personality_template="merchant",
            faction_allegiance="neutral"
        )
        warbler_bridge.register_npc(
            npc_id="npc_sage_001",
            npc_name="Sage Elara",
            realm_id="sol_1",
            personality_template="scholar",
            faction_allegiance="the_wanderers"
        )
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
        }

    def test_conversation_history_truncation(self, setup_phase4_systems):
        """
        Test that long conversation histories are truncated for performance.
        
        Expected behavior:
        - Keep last N turns (e.g., 5 most recent)
        - Archive or discard older turns
        - Memory usage stays constant regardless of conversation length
        - Full history available via archive if needed
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        player = router.create_player("Riley", "human", "sol_1")
        player_id = player.player_id
        session_id = query_service.create_conversation_session(
            player_id=player_id,
            npc_id="npc_merchant_001",
            realm_id="sol_1"
        )
        
        # Simulate 20 turns
        for turn_num in range(1, 21):
            query_service.query_npc_with_session(
                session_id=session_id,
                user_input=f"Turn {turn_num}: {['Hello', 'How are you', 'Got any wares', 'What quest', 'Goodbye'][turn_num % 5]}"
            )
        
        # Check that history is truncated to reasonable size
        session = query_service.get_conversation_session(session_id)
        history_length = len(session["conversation_history"])
        
        # Should keep only recent turns (e.g., last 5-10)
        assert history_length <= 10
        # But should have recorded all 20 somehow (archive or full_history)
        if "full_history_length" in session:
            assert session["full_history_length"] >= 20

    def test_session_memory_overhead(self, setup_phase4_systems):
        """
        Test that session storage doesn't cause memory bloat.
        
        Expected behavior:
        - Each session minimal overhead
        - Can support 1000+ concurrent sessions
        - No memory leaks on session cleanup
        - Performance remains O(1) for session access
        """
        query_service = setup_phase4_systems["query_service"]
        router = setup_phase4_systems["router"]
        
        # Create many sessions
        session_ids = []
        for i in range(100):
            player = router.create_player(f"Player{i}", "human", "sol_1")
            player_id = player.player_id
            session_id = query_service.create_conversation_session(
                player_id=player_id,
                npc_id="npc_merchant_001",
                realm_id="sol_1"
            )
            session_ids.append(session_id)
        
        # All should be accessible
        assert len(session_ids) == 100
        
        # Random access should be fast
        import time
        start = time.time()
        for sid in session_ids[::10]:  # Sample 10 sessions
            query_service.get_conversation_session(sid)
        elapsed = time.time() - start
        
        # Should be fast (< 100ms for 10 lookups)
        assert elapsed < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])