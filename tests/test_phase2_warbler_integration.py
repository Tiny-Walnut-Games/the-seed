"""
Phase 2 Integration Tests: Warbler, NPCs, Quests, and Cross-Realm Narrative

Tests the complete Phase 2 system:
1. Extended UniversalPlayerRouter with narrative tracking
2. Warbler Bridge Layer for NPC dialogue
3. Warbler Query Service for cross-realm NPC queries
4. City Simulation Integration for NPCs in multiverse
5. Cross-Realm Quest System

Scenario: Player travels across 3 realms, completes a multi-realm quest,
NPCs remember them, dialogue changes based on reputation.
"""

import pytest
import sys
from pathlib import Path

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


class TestPhase2Integration:
    """Main integration test suite for Phase 2."""
    
    @pytest.fixture
    def setup_systems(self):
        """Set up all Phase 2 systems with Warbler pack loading."""
        # Load Warbler packs
        pack_loader = WarblerPackLoader()
        packs_loaded = pack_loader.load_all_packs()
        print(f"✓ Loaded {packs_loaded} Warbler packs")
        print(f"  Stats: {pack_loader.get_stats()}")
        
        # Core systems
        player_router = UniversalPlayerRouter()
        warbler_bridge = WarblerMultiverseBridge(player_router)
        
        # Wire pack loader into query service
        warbler_query_service = WarblerQueryService(
            player_router, 
            warbler_bridge,
            pack_loader=pack_loader  # <-- Enable real template-based dialogue
        )
        
        # Mock city integration
        orchestrator = MultiGameTickEngine(control_tick_interval_ticks=10)
        city_integration = CitySimulationIntegration(
            orchestrator, player_router, warbler_bridge, warbler_query_service
        )
        
        # Quest system
        quest_system = CrossRealmQuestSystem(player_router, city_integration)
        
        return {
            "router": player_router,
            "bridge": warbler_bridge,
            "query_service": warbler_query_service,
            "city_integration": city_integration,
            "quest_system": quest_system,
            "orchestrator": orchestrator,
            "pack_loader": pack_loader,
        }
    
    def test_extended_player_router_narrative_events(self, setup_systems):
        """Test narrative event tracking in UniversalPlayerRouter."""
        router = setup_systems["router"]
        
        # Create player
        player = router.create_player("Alice", "human", "sol_1", "Warrior")
        
        # Emit narrative events
        event1 = router.emit_narrative_event(
            player.player_id,
            "achievement",
            "First Travel",
            "Alice traveled to a new realm"
        )
        
        assert event1["event_type"] == "achievement"
        assert event1["title"] == "First Travel"
        assert len(router.narrative_events) == 1
    
    def test_npc_memory_storage(self, setup_systems):
        """Test NPC memory storage about players."""
        router = setup_systems["router"]
        
        player = router.create_player("Bob", "elf", "sol_1", "Ranger")
        
        # Store NPC memory
        success = router.store_npc_memory(
            "npc_001",
            player.player_id,
            "encounter",
            "Met Bob in the tavern"
        )
        
        assert success
        assert "npc_001" in router.npc_memory_store
    
    def test_personality_modifiers_from_reputation(self, setup_systems):
        """Test that reputation affects NPC personality modifiers."""
        router = setup_systems["router"]
        
        player = router.create_player("Charlie", "dwarf", "sol_1", "Paladin")
        
        # Modify reputation
        router.modify_reputation(player.player_id, ReputationFaction.THE_WANDERERS, 600)
        
        # Get personality modifiers
        rep_standing = {rep.faction.value: rep.standing for rep in player.reputation}
        modifiers = router._calculate_personality_modifiers(rep_standing)
        
        # Should be "deferential" for revered standing
        assert modifiers["the_wanderers"] == "deferential"
    
    def test_warbler_dialogue_context(self, setup_systems):
        """Test enhanced Warbler dialogue context generation."""
        router = setup_systems["router"]
        
        player = router.create_player("Diana", "human", "sol_1", "Mage")
        
        # Get dialogue context
        context = router.get_warbler_dialogue_context(player.player_id)
        
        assert context["player_name"] == "Diana"
        assert context["character_class"] == "Mage"
        assert context["active_realm"] == "sol_1"
    
    def test_warbler_bridge_npc_registration(self, setup_systems):
        """Test NPC registration with Warbler bridge."""
        bridge = setup_systems["bridge"]
        
        success = bridge.register_npc(
            "npc_merchant_001",
            "Marco the Merchant",
            "sol_1",
            "merchant",
            "the_wanderers"
        )
        
        assert success
        assert "npc_merchant_001" in bridge.npc_registry
    
    def test_warbler_bridge_dialogue_context(self, setup_systems):
        """Test bridge generates proper dialogue context."""
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        
        player = router.create_player("Eve", "human", "sol_1", "Rogue")
        bridge.register_npc("npc_guard_001", "Captain Guard", "sol_1", "guard", "realm_keepers")
        
        # Make player revered by realm_keepers
        router.modify_reputation(player.player_id, ReputationFaction.REALM_KEEPERS, 600)
        
        # Get dialogue context
        context = bridge.get_dialogue_context(player.player_id, "npc_guard_001")
        
        assert context.player_name == "Eve"
        assert context.npc_name == "Captain Guard"
        # When player is "revered" by NPC's faction, NPC shows reverent behavior
        assert "reverent" in context.npc_personality.reputation_modifiers.values()
    
    def test_warbler_bridge_player_journey_narrative(self, setup_systems):
        """Test journey narrative generation."""
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        
        player = router.create_player("Frank", "dwarf", "sol_1", "Paladin")
        router.transition_player(player.player_id, "sol_1", "sol_2", "Portal")
        router.transition_player(player.player_id, "sol_2", "sol_3", "Portal")
        
        bridge.register_npc("npc_scholar_001", "Scholar", "sol_3", "scholar")
        
        context = bridge.get_dialogue_context(player.player_id, "npc_scholar_001")
        
        assert "sol_1" in context.player_journey
        assert "3 realms" in context.player_journey  # visited 3 realms
    
    def test_warbler_query_service_dialogue_generation(self, setup_systems):
        """Test query service generates NPC dialogue."""
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        query_service = setup_systems["query_service"]
        
        player = router.create_player("Grace", "elf", "sol_1", "Archer")
        bridge.register_npc("npc_merchant_002", "Elara", "sol_1", "merchant")
        
        # Query NPC
        response = query_service.query_npc(
            player.player_id,
            "npc_merchant_002",
            "Do you have any legendary items?",
            "sol_1"
        )
        
        assert response["status"] == "complete"
        assert "npc_response" in response
        assert len(response["npc_response"]) > 0
    
    def test_warbler_query_service_conversation_session(self, setup_systems):
        """Test conversation session management."""
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        query_service = setup_systems["query_service"]
        
        player = router.create_player("Henry", "human", "sol_1", "Knight")
        bridge.register_npc("npc_guard_002", "Sir Guard", "sol_1", "guard")
        
        # Start conversation
        session = query_service.start_conversation(player.player_id, "npc_guard_002", "sol_1")
        
        assert session.session_id is not None
        assert session.player_id == player.player_id
        
        # End conversation
        summary = query_service.end_conversation(session.session_id)
        
        assert summary["player_id"] == player.player_id
    
    def test_warbler_pack_templates_with_reputation_modifiers(self, setup_systems):
        """Test that real Warbler pack templates are used with reputation-aware selection."""
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        query_service = setup_systems["query_service"]
        pack_loader = setup_systems["pack_loader"]
        
        # Verify packs are loaded
        assert pack_loader.get_stats()["total_templates"] > 0, "No templates loaded!"
        print(f"\n✓ Pack loader has {pack_loader.get_stats()['total_templates']} templates")
        
        player = router.create_player("Iris", "human", "sol_1", "Cleric")
        bridge.register_npc("npc_merchant_003", "Theron", "sol_1", "merchant")
        
        # Test 1: Neutral reputation - should get neutral/professional templates
        response_neutral = query_service.query_npc(
            player.player_id,
            "npc_merchant_003",
            "Hello there!",
            "sol_1"
        )
        assert response_neutral["status"] == "complete"
        assert len(response_neutral["npc_response"]) > 0
        # Check that pack templates were used (will have slot names filled)
        assert "{{" not in response_neutral["npc_response"], "Template slots not filled!"
        
        # Track baseline template usage
        templates_used_neutral = query_service.pack_templates_used
        
        # Test 2: Revered reputation - should get formal/reverent templates
        router.modify_reputation(player.player_id, ReputationFaction.THE_WANDERERS, 600)
        response_revered = query_service.query_npc(
            player.player_id,
            "npc_merchant_003",
            "I seek wisdom and trade.",
            "sol_1"
        )
        assert response_revered["status"] == "complete"
        assert len(response_revered["npc_response"]) > 0
        assert "{{" not in response_revered["npc_response"]
        
        # Should have used pack templates
        assert query_service.pack_templates_used >= templates_used_neutral, \
            "Pack templates should be used for revered dialogue"
        
        # Test 3: Different dialogue context (help request) should select different template tags
        response_help = query_service.query_npc(
            player.player_id,
            "npc_merchant_003",
            "Can you help me find something?",
            "sol_1"
        )
        assert response_help["status"] == "complete"
        assert len(response_help["npc_response"]) > 0
        
        # All responses should be properly filled
        assert "{{" not in response_help["npc_response"]
        
        # Should have generated multiple responses from different templates
        assert query_service.pack_templates_used >= 2, \
            "Should have used multiple pack templates for different dialogue contexts"
        
        print(f"✓ Pack templates used: {query_service.pack_templates_used}")
        print(f"  Neutral response: {response_neutral['npc_response'][:60]}...")
        print(f"  Revered response: {response_revered['npc_response'][:60]}...")
        print(f"  Help response: {response_help['npc_response'][:60]}...")
    
    def test_city_simulation_integration_npc_registration(self, setup_systems):
        """Test NPC registration in city simulation."""
        city_integration = setup_systems["city_integration"]
        
        npc_ids = city_integration.register_city_simulation(
            "sol_1",
            None,  # Mock city sim
            num_npcs=20
        )
        
        assert len(npc_ids) == 20
        assert len(city_integration.npcs) == 20
        assert "sol_1" in city_integration.realm_npcs
    
    def test_city_integration_npc_tick_synchronization(self, setup_systems):
        """Test NPC synchronization during control-ticks."""
        city_integration = setup_systems["city_integration"]
        
        city_integration.register_city_simulation("sol_1", None, num_npcs=10)
        
        # Execute NPC tick
        metrics = city_integration.synchronize_npc_tick(1, 100.0)
        
        assert metrics["npcs_synchronized"] == 10
        assert metrics["control_tick_id"] == 1
    
    def test_city_integration_player_arrival_notification(self, setup_systems):
        """Test NPCs are notified of player arrival."""
        router = setup_systems["router"]
        city_integration = setup_systems["city_integration"]
        
        player = router.create_player("Iris", "human", "sol_1", "Cleric")
        city_integration.register_city_simulation("sol_2", None, num_npcs=5)
        
        # Player transitions to sol_2
        router.transition_player(player.player_id, "sol_1", "sol_2", "Portal")
        
        # Notify NPCs
        city_integration.on_player_transition(
            player.player_id,
            "sol_1",
            "sol_2",
            {"reason": "portal"}
        )
        
        # NPCs should have events in queue
        assert len(city_integration.npc_event_queue) > 0
    
    def test_cross_realm_quest_creation(self, setup_systems):
        """Test creating a cross-realm quest."""
        quest_system = setup_systems["quest_system"]
        
        quest = quest_system.create_quest(
            "test_quest_001",
            "The Lost Relic",
            "Find the lost relic scattered across realms",
            "npc_quest_giver_001",
            "sol_1",
            difficulty="hard"
        )
        
        assert quest.quest_id == "test_quest_001"
        assert quest.starting_realm == "sol_1"
    
    def test_cross_realm_quest_objectives(self, setup_systems):
        """Test adding objectives to a quest."""
        quest_system = setup_systems["quest_system"]
        
        quest = quest_system.create_quest(
            "test_quest_002",
            "Multi-Realm Challenge",
            "Complete challenges across realms",
            "npc_quest_giver_002",
            "sol_1"
        )
        
        # Add objectives
        quest_system.add_objective(quest.quest_id, {
            "objective_id": "obj_1",
            "description": "Find clue in sol_1",
            "realm": "sol_1",
            "objective_type": "fetch_item",
            "target": "ancient_clue"
        })
        
        quest_system.add_objective(quest.quest_id, {
            "objective_id": "obj_2",
            "description": "Deliver clue in sol_2",
            "realm": "sol_2",
            "objective_type": "talk_to_npc",
            "target": "npc_scholar_002"
        })
        
        assert len(quest.objectives) == 2
    
    def test_cross_realm_quest_player_acceptance(self, setup_systems):
        """Test player accepting a quest."""
        router = setup_systems["router"]
        quest_system = setup_systems["quest_system"]
        
        player = router.create_player("Jack", "human", "sol_1", "Fighter")
        
        # Get available quest
        available = quest_system.get_available_quests_in_realm("sol_1")
        assert len(available) > 0
        
        # Accept quest
        quest_id = available[0]["quest_id"]
        success, msg = quest_system.accept_quest(player.player_id, quest_id)
        
        assert success
        assert player.player_id in quest_system.player_quests
    
    def test_cross_realm_quest_progression(self, setup_systems):
        """Test progressing through quest objectives."""
        router = setup_systems["router"]
        quest_system = setup_systems["quest_system"]
        
        player = router.create_player("Kate", "elf", "sol_1", "Mage")
        
        # Accept first quest
        available = quest_system.get_available_quests_in_realm("sol_1")
        quest_id = available[0]["quest_id"]
        quest_system.accept_quest(player.player_id, quest_id)
        
        # Get quest and first objective
        quest = quest_system.quests[quest_id]
        first_objective = quest.objectives[0]
        
        # Progress objective
        success, msg, context = quest_system.progress_objective(
            player.player_id,
            quest_id,
            first_objective.objective_id,
            progress=1
        )
        
        assert success
        assert context["progress"] >= 1
    
    def test_full_integration_scenario(self, setup_systems):
        """
        Full integration test: Player journey across 3 realms
        with NPCs, quests, and narrative awareness.
        """
        router = setup_systems["router"]
        bridge = setup_systems["bridge"]
        query_service = setup_systems["query_service"]
        city_integration = setup_systems["city_integration"]
        quest_system = setup_systems["quest_system"]
        
        print("\n=== Full Phase 2 Integration Scenario ===")
        
        # 1. Create player
        player = router.create_player("Legend", "human", "sol_1", "Paladin")
        print(f"✅ Created player: {player.player_name}")
        
        # 2. Register cities in 3 realms
        for realm in ["sol_1", "sol_2", "sol_3"]:
            npc_ids = city_integration.register_city_simulation(realm, None, num_npcs=15)
            print(f"✅ Registered {len(npc_ids)} NPCs in {realm}")
        
        # 3. Register NPCs with Warbler bridge
        npcs_in_sol_1 = city_integration.realm_npcs.get("sol_1", [])
        for npc_id in npcs_in_sol_1[:3]:  # Register first 3
            npc = city_integration.npcs[npc_id]
            bridge.register_npc(npc_id, npc.npc_name, npc.realm_id, npc.role)
        print(f"✅ Registered NPCs with Warbler bridge")
        
        # 4. Accept multi-realm quest
        available = quest_system.get_available_quests_in_realm("sol_1")
        quest_id = available[0]["quest_id"]
        success, msg = quest_system.accept_quest(player.player_id, quest_id)
        print(f"✅ Accepted quest: {quest_system.quests[quest_id].title}")
        
        # 5. Player travels across realms
        router.transition_player(player.player_id, "sol_1", "sol_2", "Portal")
        print(f"✅ Player traveled to sol_2")
        
        city_integration.on_player_transition(
            player.player_id, "sol_1", "sol_2", {"reason": "portal"}
        )
        
        # 6. Modify player reputation
        router.modify_reputation(player.player_id, ReputationFaction.THE_WANDERERS, 600)
        print(f"✅ Player became 'revered' by The Wanderers")
        
        # 7. Get dialogue from NPC aware of player
        npcs_in_sol_2 = city_integration.realm_npcs.get("sol_2", [])
        npc_id = npcs_in_sol_2[0]
        npc = city_integration.npcs[npc_id]
        bridge.register_npc(npc_id, npc.npc_name, npc.realm_id, npc.role)
        
        response = query_service.query_npc(
            player.player_id,
            npc_id,
            "What have you heard about me?",
            "sol_2"
        )
        print(f"✅ NPC response: {response['npc_response'][:50]}...")
        
        # 8. Player travels to third realm
        router.transition_player(player.player_id, "sol_2", "sol_3", "Portal")
        print(f"✅ Player traveled to sol_3")
        
        # 9. Verify narrative events were created
        narrative_events = [
            e for e in router.narrative_events 
            if e.get("player_id") == player.player_id
        ]
        print(f"✅ {len(narrative_events)} narrative events recorded")
        
        # 10. Verify player journey context
        context = bridge.get_dialogue_context(player.player_id, npcs_in_sol_1[0])
        print(f"✅ Player journey summary: {context.player_journey}")
        
        # 11. Get system stats
        stats = city_integration.get_integration_stats()
        quest_stats = quest_system.get_system_stats()
        
        print(f"\n📊 Phase 2 Stats:")
        print(f"   Total NPCs: {stats['total_npcs']}")
        print(f"   Quests created: {quest_stats['total_quests_created']}")
        print(f"   Player realms visited: {len(player.visited_realms)}")
        
        assert player.active_realm == "sol_3"
        assert len(player.visited_realms) == 3
        assert len(narrative_events) > 0
        
        print(f"\n✅ Full integration scenario completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])