"""
Test: MultiGame Orchestration with Control-Tick Architecture

Demonstrates:
1. MultiGameTickEngine coordinating multiple games
2. Control-tick synchronization across realms
3. Cross-game event routing via STAT7 addressing
4. UniversalPlayerRouter managing player transitions
5. Full integration of orchestrator

Run: pytest tests/test_multigame_orchestration.py -v -s
"""

import sys
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

import pytest
from web.server.tick_engine import TickEngine, ReactionRule
from web.server.multigame_tick_engine import (
    MultiGameTickEngine,
    RealmCoordinate,
    CrossGameEvent,
    GameInstanceState,
)
from web.server.universal_player_router import (
    UniversalPlayerRouter,
    ReputationFaction,
    InventoryItem,
)


class TestMultiGameTickEngine:
    """Test MultiGame Tick Engine functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create test engine."""
        return MultiGameTickEngine(
            control_tick_interval_ticks=3,
            local_tick_interval_ms=100,
        )
    
    def test_register_games(self, engine):
        """Test registering game instances."""
        # Create two games
        game_a_engine = TickEngine(tick_interval_ms=100)
        game_b_engine = TickEngine(tick_interval_ms=100)
        
        realm_a = RealmCoordinate(
            realm_id="sol_1",
            realm_type="sol_system",
            adjacency="cluster_0",
            resonance="narrative_prime",
            density=0,
        )
        
        realm_b = RealmCoordinate(
            realm_id="sol_2",
            realm_type="sol_system",
            adjacency="cluster_0",
            resonance="narrative_prime",
            density=0,
        )
        
        # Register
        engine.register_game("sol_1", game_a_engine, realm_a)
        engine.register_game("sol_2", game_b_engine, realm_b)
        
        assert len(engine.games) == 2
        assert "sol_1" in engine.games
        assert "sol_2" in engine.games
        assert engine.game_states["sol_1"] == GameInstanceState.BOOTING
    
    def test_control_tick_synchronization(self, engine):
        """Test control-tick synchronizes all games."""
        # Setup two games
        games = {}
        for i in range(2):
            game_engine = TickEngine(tick_interval_ms=100)
            realm = RealmCoordinate(
                realm_id=f"sol_{i+1}",
                realm_type="sol_system",
                adjacency=f"cluster_{i}",
                resonance="narrative_prime",
                density=0,
            )
            engine.register_game(f"sol_{i+1}", game_engine, realm)
            games[f"sol_{i+1}"] = game_engine
        
        # Execute control-tick
        metrics = engine.execute_control_tick()
        
        # Verify synchronization
        assert metrics["control_tick_id"] == 1
        assert metrics["games_synced"] == 2
        assert engine.control_tick_count == 1
        assert len(engine.control_tick_traces) == 1
    
    def test_cross_game_event_routing(self, engine):
        """Test events route between games."""
        # Setup games
        for i in range(2):
            game_engine = TickEngine(tick_interval_ms=100)
            realm = RealmCoordinate(
                realm_id=f"sol_{i+1}",
                realm_type="sol_system",
                adjacency="cluster_0",
                resonance="narrative_prime",
                density=0,
            )
            engine.register_game(f"sol_{i+1}", game_engine, realm)
        
        # Subscribe both games to events
        engine.subscribe_to_events("sol_1", ["world_event"])
        engine.subscribe_to_events("sol_2", ["world_event"])
        
        # Create cross-game event
        event = CrossGameEvent(
            event_id="test_event_1",
            source_realm=RealmCoordinate(
                realm_id="sol_1",
                realm_type="sol_system",
                adjacency="cluster_0",
                resonance="narrative_prime",
                density=0,
            ),
            target_realm=None,  # Broadcast
            event_type="world_event",
            data={"message": "Test broadcast"},
            control_tick_id=1,
        )
        
        # Queue and propagate
        engine.queue_cross_game_event(event)
        propagated = engine._propagate_cross_game_events()
        
        # Verify propagation
        assert propagated == 2  # Both games received
        assert len(event.propagation_path) == 2
        assert "sol_1" in event.propagation_path
        assert "sol_2" in event.propagation_path


class TestUniversalPlayerRouter:
    """Test player routing across realms."""
    
    @pytest.fixture
    def router(self):
        """Create test router."""
        return UniversalPlayerRouter()
    
    def test_create_player(self, router):
        """Test player creation."""
        player = router.create_player(
            player_name="Alice",
            character_race="human",
            starting_realm="sol_1",
        )
        
        assert player.player_name == "Alice"
        assert player.active_realm == "sol_1"
        assert player.character_race == "human"
        assert "sol_1" in player.visited_realms
        assert len(player.reputation) == len(ReputationFaction)
    
    def test_player_realm_transition(self, router):
        """Test player transitioning between realms."""
        player = router.create_player(
            player_name="Bob",
            character_race="elf",
            starting_realm="sol_1",
        )
        
        # Transition to sol_2
        success, msg = router.transition_player(
            player.player_id,
            "sol_1",
            "sol_2",
            narrative_context="Portal Jump",
        )
        
        assert success
        assert player.active_realm == "sol_2"
        assert len(player.visited_realms) == 2
        assert len(router.transition_history) == 1
    
    def test_reputation_modification(self, router):
        """Test reputation changes."""
        player = router.create_player(
            player_name="Charlie",
            character_race="dwarf",
            starting_realm="sol_1",
        )
        
        # Gain reputation
        success = router.modify_reputation(
            player.player_id,
            ReputationFaction.THE_WANDERERS,
            +300,
        )
        
        assert success
        wanderer_rep = next(
            r for r in player.reputation 
            if r.faction == ReputationFaction.THE_WANDERERS
        )
        assert wanderer_rep.score == 300
        assert wanderer_rep.standing == "liked"
    
    def test_inventory_management(self, router):
        """Test item inventory."""
        player = router.create_player(
            player_name="Diana",
            character_race="human",
            starting_realm="sol_1",
        )
        
        # Add item
        sword = InventoryItem(
            item_id="sword_001",
            name="Legendary Sword",
            item_type="weapon",
            rarity="legendary",
            source_realm="sol_1",
            transferable=True,
        )
        
        success = router.add_item_to_inventory(player.player_id, sword)
        assert success
        assert len(player.inventory) == 1
        assert player.inventory[0].name == "Legendary Sword"
    
    def test_warbler_context_generation(self, router):
        """Test Warbler context generation from player state."""
        # Create complex player
        player = router.create_player(
            player_name="Eve",
            character_race="elf",
            starting_realm="sol_1",
        )
        
        # Transition to another realm
        router.transition_player(player.player_id, "sol_1", "sol_2")
        
        # Gain reputation (reach "liked" status)
        router.modify_reputation(
            player.player_id,
            ReputationFaction.REALM_KEEPERS,
            +400,
        )
        
        # Add item
        item = InventoryItem(
            item_id="amulet_001",
            name="Amulet of Passing",
            item_type="cosmetic",
            rarity="legendary",
            source_realm="sol_1",
        )
        router.add_item_to_inventory(player.player_id, item)
        
        # Generate Warbler context
        context = router.get_warbler_context(player.player_id)
        
        # Verify context
        assert context["player_name"] == "Eve"
        assert context["active_realm"] == "sol_2"
        assert len(context["visited_realms"]) == 2
        assert context["world_state"]["player_traveled_realms"] == 2
        assert context["world_state"]["player_has_legendary_items"]
        assert "liked" in context["world_state"]["player_reputation_standing"].values()


class TestFullOrchestration:
    """Test full orchestration scenario."""
    
    def test_three_game_universe_scenario(self):
        """
        Scenario: 3 games running simultaneously with players traveling.
        
        - Create 3 game instances (sol_1, sol_2, sol_3)
        - Create 2 players
        - Execute control-ticks with cross-game events
        - Verify temporal synchronization and player mobility
        """
        # Setup orchestrator
        orchestrator_engine = MultiGameTickEngine(
            control_tick_interval_ticks=2,
            local_tick_interval_ms=100,
        )
        
        # Setup player router
        player_router = UniversalPlayerRouter()
        
        # Register 3 games
        for i in range(3):
            game_engine = TickEngine(tick_interval_ms=100)
            realm = RealmCoordinate(
                realm_id=f"sol_{i+1}",
                realm_type="sol_system",
                adjacency=f"cluster_{i % 2}",
                resonance="narrative_prime",
                density=0,
            )
            orchestrator_engine.register_game(f"sol_{i+1}", game_engine, realm)
            orchestrator_engine.subscribe_to_events(f"sol_{i+1}", ["player_traveled"])
        
        # Create 2 players
        player_a = player_router.create_player(
            "Alice",
            "human",
            "sol_1",
        )
        
        player_b = player_router.create_player(
            "Bob",
            "elf",
            "sol_1",
        )
        
        # Execute 3 control-ticks
        for tick in range(3):
            metrics = orchestrator_engine.execute_control_tick()
            assert metrics["games_synced"] == 3
            assert metrics["control_tick_id"] == tick + 1
            time.sleep(0.01)  # Tiny delay
        
        # Player A travels to sol_2
        success, msg = player_router.transition_player(
            player_a.player_id,
            "sol_1",
            "sol_2",
            "Dimensional Portal",
        )
        assert success
        
        # Emit travel event as cross-game event
        travel_event = CrossGameEvent(
            event_id="travel_alice_001",
            source_realm=RealmCoordinate(
                realm_id="sol_1",
                realm_type="sol_system",
                adjacency="cluster_0",
                resonance="narrative_prime",
                density=0,
            ),
            target_realm=RealmCoordinate(
                realm_id="sol_2",
                realm_type="sol_system",
                adjacency="cluster_0",
                resonance="narrative_prime",
                density=0,
            ),
            event_type="player_traveled",
            data={
                "player_id": player_a.player_id,
                "player_name": "Alice",
                "transition": "sol_1 → sol_2",
            },
            control_tick_id=orchestrator_engine.control_tick_count,
        )
        
        orchestrator_engine.queue_cross_game_event(travel_event)
        orchestrator_engine.execute_control_tick()
        
        # Verify state
        state = orchestrator_engine.get_multiverse_state()
        assert state["control_tick_id"] == 4
        assert len(player_router.transition_history) >= 1
        
        print("\n✅ Full orchestration test passed!")
        print(f"   - 3 games synchronized")
        print(f"   - 2 players created and managed")
        print(f"   - Player travel events routed cross-game")
        print(f"   - Control-ticks executed: {state['control_tick_id']}")
        print(f"   - Games in multiverse: {state['games_registered']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])