"""
Integration test for Warbler Autonomous Loop

Demonstrates:
1. Initializing the autonomous narrative loop
2. Running autonomous ticks for a realm
3. Verifying narrative events are generated and stored
4. Tracking entity lifecycles
5. Proving continuous autonomous generation works
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

# Add server path
current_dir = Path(__file__).parent
server_dir = current_dir.parent / "web" / "server"
sys.path.insert(0, str(server_dir))

from warbler_autonomous_loop import (
    WarblerAutonomousLoop,
    WarblerNarrativeParser,
    EntityEventType,
)

# Mock event store for testing
class MockEventStore:
    def __init__(self):
        self.events = {}  # stream_id -> list of events
    
    def append_event(
        self,
        stream_id: str,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Mock append_event implementation."""
        if stream_id not in self.events:
            self.events[stream_id] = []
        
        event = {
            "stream_id": stream_id,
            "event_type": event_type,
            "payload": payload,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        self.events[stream_id].append(event)
        return event
    
    def get_stream(self, stream_id: str) -> list:
        """Get all events for a stream."""
        return self.events.get(stream_id, [])


# Mock Warbler query service
class MockWarblerQueryService:
    def __init__(self):
        self.queries = []
    
    async def query_narrative(self, context: Dict[str, Any]) -> str:
        """Mock narrative query."""
        self.queries.append(context)
        # Return a mock narrative
        return (
            "In the marketplace, Kayla the merchant arranges exotic spices. "
            "Two hooded traders approach her with an unusual offer. "
            "The merchant sets out toward the mountain pass to find rare herbs. "
            "A storm is brewing on the horizon."
        )


class TestWarblerNarrativeParser:
    """Test the narrative parsing logic."""
    
    def test_parse_entity_spawn(self):
        """Test parsing entity spawn from narrative."""
        parser = WarblerNarrativeParser()
        
        narrative = "Kayla the merchant appears in the marketplace."
        events = parser.parse_narrative(narrative, "realm_1", 100)
        
        assert len(events) > 0
        assert any(e["event_type"] == EntityEventType.ENTITY_SPAWN.value for e in events)
    
    def test_parse_entity_action(self):
        """Test parsing entity action from narrative."""
        parser = WarblerNarrativeParser()
        
        narrative = "The merchant speaks to a customer about rare goods."
        events = parser.parse_narrative(narrative, "realm_1", 100)
        
        assert len(events) > 0
    
    def test_parse_entity_movement(self):
        """Test parsing entity movement from narrative."""
        parser = WarblerNarrativeParser()
        
        narrative = "Thorne sets out toward the northern pass."
        events = parser.parse_narrative(narrative, "realm_1", 100)
        
        assert len(events) > 0
        movement_events = [e for e in events if e["event_type"] == EntityEventType.NPC_DECISION.value]
        assert len(movement_events) > 0
    
    def test_parse_environment_change(self):
        """Test parsing environment changes from narrative."""
        parser = WarblerNarrativeParser()
        
        narrative = "The sun sets and darkness falls over the realm."
        events = parser.parse_narrative(narrative, "realm_1", 100)
        
        assert len(events) > 0


@pytest.mark.asyncio
async def test_autonomous_loop_initialization():
    """Test autonomous loop initialization."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    assert loop is not None
    assert loop.event_store == event_store
    await loop.initialize_realm("test_realm")
    assert "test_realm" in loop.realm_states


@pytest.mark.asyncio
async def test_autonomous_tick_generation():
    """Test a single autonomous tick generates events."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    result = await loop.execute_autonomous_tick(
        realm_id="test_realm",
        current_tick=100
    )
    
    # Should generate at least one event
    assert result["status"] == "success"
    assert result["events_generated"] > 0
    assert "events" in result
    assert isinstance(result["events"], list)


@pytest.mark.asyncio
async def test_multiple_autonomous_ticks():
    """Test multiple consecutive ticks generate entity lifecycle."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    # Run 5 ticks
    tick_results = []
    for tick in range(5):
        result = await loop.execute_autonomous_tick(
            realm_id="test_realm",
            current_tick=tick
        )
        tick_results.append(result)
    
    # Should have generated events in most/all ticks
    total_events = sum(r["events_generated"] for r in tick_results)
    assert total_events > 0
    
    # Check realm stats
    stats = loop.get_realm_narrative_stats("test_realm")
    assert stats["ticks_run"] == 5
    assert stats["entities_spawned_lifetime"] >= 0


@pytest.mark.asyncio
async def test_entity_lifecycle_tracking():
    """Test that entity lifecycles are tracked correctly."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    # Generate a tick
    result = await loop.execute_autonomous_tick(
        realm_id="test_realm",
        current_tick=100
    )
    
    # Check if any entities were spawned
    spawn_events = [e for e in result.get("events", []) 
                    if e.get("event_type") == EntityEventType.ENTITY_SPAWN.value]
    
    if spawn_events:
        # Entities should be tracked in realm state
        realm_state = loop.realm_states["test_realm"]
        assert len(realm_state.active_entities) > 0
        
        # Each tracked entity should have lifecycle data
        for entity_id, lifecycle in realm_state.active_entities.items():
            assert lifecycle.entity_id == entity_id
            assert lifecycle.realm_id == "test_realm"
            assert lifecycle.is_active


@pytest.mark.asyncio
async def test_event_store_persistence():
    """Test that generated events are persisted to event store."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    result = await loop.execute_autonomous_tick(
        realm_id="test_realm",
        current_tick=100
    )
    
    # Check that events were added to event store
    assert len(event_store.events) > 0
    
    # Verify event structure
    for stream_id, events in event_store.events.items():
        assert "stat7" in stream_id
        for event in events:
            assert "event_type" in event
            assert "payload" in event
            assert "timestamp" in event


@pytest.mark.asyncio
async def test_realm_narrative_statistics():
    """Test realm narrative statistics tracking."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    # Run several ticks
    for tick in range(3):
        await loop.execute_autonomous_tick(
            realm_id="test_realm",
            current_tick=tick * 10
        )
    
    stats = loop.get_realm_narrative_stats("test_realm")
    
    assert stats["realm_id"] == "test_realm"
    assert stats["ticks_run"] >= 3
    assert "entities_spawned_lifetime" in stats
    assert "entities_active" in stats
    assert "narrative_density" in stats
    assert "total_events_generated" in stats


@pytest.mark.asyncio
async def test_autonomous_loop_graceful_shutdown():
    """Test autonomous loop can shutdown gracefully."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    # Should not raise any errors
    await loop.shutdown()
    assert loop.is_running == False


@pytest.mark.asyncio
async def test_continuous_autonomous_generation():
    """Integration test: continuous autonomous generation scenario."""
    event_store = MockEventStore()
    warbler_service = MockWarblerQueryService()
    
    loop = WarblerAutonomousLoop(
        event_store=event_store,
        warbler_query_service=warbler_service,
    )
    
    # Simulate 100 ticks of continuous generation
    total_events = 0
    total_entities_spawned = 0
    
    for tick in range(100):
        result = await loop.execute_autonomous_tick(
            realm_id="multiverse_realm",
            current_tick=tick
        )
        
        if result["status"] == "success":
            total_events += result["events_generated"]
            
            # Check entity spawning
            spawn_count = len([e for e in result.get("events", [])
                             if e.get("event_type") == EntityEventType.ENTITY_SPAWN.value])
            total_entities_spawned += spawn_count
    
    # Should have generated many events over 100 ticks
    assert total_events > 0
    
    # Stats should show ongoing generation
    stats = loop.get_realm_narrative_stats("multiverse_realm")
    assert stats["ticks_run"] == 100
    assert stats["total_events_generated"] > 0
    
    logger = __import__("logging").getLogger(__name__)
    logger.info(
        f"✅ Continuous Generation Test: "
        f"Generated {total_events} events, spawned {total_entities_spawned} entities "
        f"over 100 ticks"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])