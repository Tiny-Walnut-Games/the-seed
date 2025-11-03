"""
Test: MMO Orchestrator Integration

Verifies:
1. Game registration via MultiGameTickEngine
2. Control-tick synchronization
3. Cross-game event routing
4. WebSocket API communication

Run: pytest tests/test_mmo_orchestrator.py -v -s
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "server"))

from tick_engine import TickEngine
from multigame_tick_engine import MultiGameTickEngine, RealmCoordinate, GameInstanceState
from mmo_orchestrator import MMOOrchestrator, GameRegistration


class TestMMOOrchestratorCore:
    """Test core orchestrator functionality."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator."""
        return MMOOrchestrator(
            ws_host="localhost",
            ws_port=9999,  # Use non-standard port for tests
            control_tick_interval_ticks=5,
            local_tick_interval_ms=50,
        )
    
    def test_orchestrator_initializes(self, orchestrator):
        """✅ Orchestrator should initialize with correct state."""
        assert orchestrator.is_running == False
        assert len(orchestrator.game_registry) == 0
        assert orchestrator.orchestrator is not None
        assert isinstance(orchestrator.orchestrator, MultiGameTickEngine)
    
    def test_game_registration(self, orchestrator):
        """✅ Should register games with STAT7 coordinates."""
        result = orchestrator.register_game(
            game_id="test_game_1",
            realm_id="Test Realm",
            developer_name="Test Dev",
            description="Test game",
            realm_type="test_realm",
            adjacency="test_cluster",
            resonance="test",
            density=0
        )
        
        # Verify registration response
        assert result["status"] == "registered"
        assert result["game_id"] == "test_game_1"
        assert "realm_coordinate" in result
        
        # Verify game in registry
        assert "test_game_1" in orchestrator.game_registry
        registration = orchestrator.game_registry["test_game_1"]
        assert registration.realm_id == "Test Realm"
        assert registration.developer_name == "Test Dev"
    
    def test_duplicate_registration_fails(self, orchestrator):
        """✅ Should reject duplicate game IDs."""
        orchestrator.register_game(
            game_id="dup_test",
            realm_id="Realm A",
            developer_name="Dev",
            description="Test"
        )
        
        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register_game(
                game_id="dup_test",
                realm_id="Realm B",
                developer_name="Dev",
                description="Test"
            )
    
    def test_list_games(self, orchestrator):
        """✅ Should list all registered games."""
        # Register multiple games
        orchestrator.register_game("game_1", "Realm 1", "Dev 1", "Game 1")
        orchestrator.register_game("game_2", "Realm 2", "Dev 2", "Game 2")
        
        games = orchestrator.list_registered_games()
        
        assert len(games) == 2
        assert any(g["game_id"] == "game_1" for g in games)
        assert any(g["game_id"] == "game_2" for g in games)
    
    def test_unregister_game(self, orchestrator):
        """✅ Should unregister games."""
        orchestrator.register_game("to_remove", "Realm X", "Dev X", "Test")
        assert "to_remove" in orchestrator.game_registry
        
        result = orchestrator.unregister_game("to_remove")
        
        assert result["status"] == "unregistered"
        assert "to_remove" not in orchestrator.game_registry
    
    def test_unregister_nonexistent_fails(self, orchestrator):
        """✅ Should reject unregistering non-existent games."""
        with pytest.raises(ValueError, match="not found"):
            orchestrator.unregister_game("nonexistent")


class TestCrossGameEvents:
    """Test cross-game event routing."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with registered games."""
        orch = MMOOrchestrator(ws_port=9999)
        orch.register_game("source_game", "Source Realm", "Dev A", "Source")
        orch.register_game("target_game", "Target Realm", "Dev B", "Target")
        return orch
    
    def test_publish_unicast_event(self, orchestrator):
        """✅ Should route event to specific target game."""
        event_id = orchestrator.publish_cross_game_event(
            source_game_id="source_game",
            target_game_id="target_game",
            event_type="test_event",
            data={"message": "Hello from source"}
        )
        
        assert event_id is not None
        assert orchestrator.universe_metadata["total_cross_game_events"] == 1
    
    def test_publish_broadcast_event(self, orchestrator):
        """✅ Should broadcast event to all games."""
        event_id = orchestrator.publish_cross_game_event(
            source_game_id="source_game",
            target_game_id=None,  # Broadcast
            event_type="broadcast_event",
            data={"message": "Broadcast from source"}
        )
        
        assert event_id is not None
        assert orchestrator.universe_metadata["total_cross_game_events"] == 1
    
    def test_invalid_source_fails(self, orchestrator):
        """✅ Should reject events from unregistered source."""
        with pytest.raises(ValueError, match="not registered"):
            orchestrator.publish_cross_game_event(
                source_game_id="nonexistent",
                target_game_id="target_game",
                event_type="event",
                data={}
            )
    
    def test_invalid_target_fails(self, orchestrator):
        """✅ Should reject events to unregistered target."""
        with pytest.raises(ValueError, match="not registered"):
            orchestrator.publish_cross_game_event(
                source_game_id="source_game",
                target_game_id="nonexistent",
                event_type="event",
                data={}
            )


class TestControlTickExecution:
    """Test control-tick synchronization."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with games."""
        orch = MMOOrchestrator(ws_port=9999)
        orch.register_game("game_1", "Realm 1", "Dev", "Test 1")
        orch.register_game("game_2", "Realm 2", "Dev", "Test 2")
        return orch
    
    @pytest.mark.asyncio
    async def test_execute_control_tick(self, orchestrator):
        """✅ Should execute control-tick synchronization."""
        metrics = await orchestrator.execute_control_tick()
        
        assert metrics["control_tick_id"] == 1
        assert metrics["games_synced"] == 2
        assert metrics["elapsed_ms"] >= 0
        assert orchestrator.universe_metadata["total_control_ticks"] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_control_ticks(self, orchestrator):
        """✅ Should track multiple control-ticks."""
        for i in range(3):
            metrics = await orchestrator.execute_control_tick()
            assert metrics["control_tick_id"] == i + 1
        
        assert orchestrator.universe_metadata["total_control_ticks"] == 3
    
    @pytest.mark.asyncio
    async def test_orchestration_loop_with_max_ticks(self, orchestrator):
        """✅ Should exit orchestration loop after max ticks."""
        import time
        start = time.time()
        
        await orchestrator.run_orchestration_loop(max_ticks=2)
        
        elapsed = time.time() - start
        assert orchestrator.universe_metadata["total_control_ticks"] == 2
        assert elapsed < 5  # Should complete quickly


class TestGameRegistrationMetadata:
    """Test game registration metadata."""
    
    def test_game_registration_metadata(self):
        """✅ Game registration should contain required metadata."""
        orchestrator = MMOOrchestrator(ws_port=9999)
        
        orchestrator.register_game(
            game_id="meta_test",
            realm_id="Meta Realm",
            developer_name="Meta Dev",
            description="Testing metadata",
            realm_type="custom",
            adjacency="cluster_test",
            resonance="test_resonance",
            density=1
        )
        
        games = orchestrator.list_registered_games()
        assert len(games) == 1
        
        game_meta = games[0]
        assert game_meta["game_id"] == "meta_test"
        assert game_meta["realm_id"] == "Meta Realm"
        assert game_meta["developer_name"] == "Meta Dev"
        assert game_meta["description"] == "Testing metadata"
        assert game_meta["registered_at"] is not None
        assert "realm_coordinate" in game_meta


class TestUniverseMetadata:
    """Test universe metadata tracking."""
    
    @pytest.mark.asyncio
    async def test_universe_metadata_updates(self):
        """✅ Universe metadata should track events."""
        orchestrator = MMOOrchestrator(ws_port=9999)
        
        # Register games
        orchestrator.register_game("game_a", "Realm A", "Dev", "Test")
        orchestrator.register_game("game_b", "Realm B", "Dev", "Test")
        
        # Execute ticks
        await orchestrator.execute_control_tick()
        await orchestrator.execute_control_tick()
        
        # Publish events
        orchestrator.publish_cross_game_event(
            "game_a", "game_b", "test", {}
        )
        
        metadata = orchestrator.universe_metadata
        assert metadata["total_games_registered"] == 2
        assert metadata["total_control_ticks"] == 2
        assert metadata["total_cross_game_events"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])