"""
End-to-End Scenario Tests (Layer 5: Full System Integration)

This test suite defines complete user journeys that exercise all layers:
Event Store, Tick Engine, Governance, and API Gateway working in concert.

Scenarios test:
- Multi-entity state coordination
- Event correlation across entities
- Temporal consistency
- Error recovery
- Long-running simulations
- Subscription lifecycle
- State consistency under cascades

All tests MUST pass before integration is considered complete.
"""

import pytest
import sys
from pathlib import Path as PathlibPath
from datetime import datetime, timedelta
import uuid

# Add web/server to path so we can import e2e_simulation
sys.path.insert(0, str(PathlibPath(__file__).parent.parent / "web" / "server"))

from e2e_simulation import (
    StateChange,
    EntitySnapshot,
    CorrelatedCommand,
    SimulationScenario,
    E2ESimulationHarness,
)


# ============================================================================
# TEST SCENARIOS
# ============================================================================

@pytest.mark.e2e
class TestE2ESimpleCommandSubmission:
    """User submits a command; it updates state."""
    
    @pytest.mark.e2e
    def test_single_command_updates_entity(self):
        """Single command updates entity state."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("user_1", {"name": "Alice", "points": 0})
        
        command = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetPoints",
            entity_id="user_1",
            actor_id="system",
            payload={"points": 100},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        success = harness.submit_command(command)
        assert success is True
        
        state = harness.get_entity_state("user_1")
        assert state["points"] == 100
        assert state["name"] == "Alice"  # Unchanged
    
    @pytest.mark.e2e
    def test_multiple_commands_update_state_sequentially(self):
        """Multiple commands update state in order."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"count": 0})
        
        for i in range(1, 4):
            command = CorrelatedCommand(
                command_id=str(uuid.uuid4()),
                command_type="IncrementCount",
                entity_id="entity_1",
                actor_id="system",
                payload={"count": i},
                timestamp=datetime.utcnow() + timedelta(milliseconds=i*10),
                correlation_id=str(uuid.uuid4())
            )
            success = harness.submit_command(command)
            assert success is True
        
        state = harness.get_entity_state("entity_1")
        assert state["count"] == 3
    
    @pytest.mark.e2e
    def test_multiple_entities_maintain_independence(self):
        """Multiple entities maintain independent state."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        harness.initialize_entity("entity_2", {"value": 0})
        
        cmd1 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 10},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        cmd2 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_2",
            actor_id="system",
            payload={"value": 20},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(cmd1)
        harness.submit_command(cmd2)
        
        state1 = harness.get_entity_state("entity_1")
        state2 = harness.get_entity_state("entity_2")
        
        assert state1["value"] == 10
        assert state2["value"] == 20


@pytest.mark.e2e
class TestE2ETemporalQueries:
    """System can answer "what was state at time T?" questions."""
    
    @pytest.mark.e2e
    def test_state_as_of_timestamp(self):
        """Can retrieve state as it was at a past timestamp."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        
        t1 = datetime.utcnow()
        t2 = t1 + timedelta(seconds=1)
        t3 = t2 + timedelta(seconds=1)
        
        cmd1 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 1},
            timestamp=t1,
            correlation_id=str(uuid.uuid4())
        )
        
        cmd2 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 2},
            timestamp=t2,
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(cmd1)
        harness.submit_command(cmd2)
        
        # Query state at different times
        state_at_t1_minus = harness.get_entity_state_as_of("entity_1", t1 - timedelta(milliseconds=1))
        state_at_t1 = harness.get_entity_state_as_of("entity_1", t1)
        state_at_t2 = harness.get_entity_state_as_of("entity_1", t2)
        state_at_t3 = harness.get_entity_state_as_of("entity_1", t3)
        
        assert state_at_t1_minus == {"value": 0}
        assert state_at_t1 == {"value": 1}
        assert state_at_t2 == {"value": 2}
        assert state_at_t3 == {"value": 2}


@pytest.mark.e2e
class TestE2ESubscriptions:
    """Subscribers receive notifications of state changes."""
    
    @pytest.mark.e2e
    def test_subscriber_receives_notifications(self):
        """Subscriber receives notifications for subscribed entity."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        harness.subscribe_to_entity("entity_1", "subscriber_1")
        
        command = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 100},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(command)
        
        notifications = harness.get_notifications_for_subscriber("subscriber_1")
        assert len(notifications) == 1
        assert notifications[0].key == "value"
        assert notifications[0].new_value == 100
    
    @pytest.mark.e2e
    def test_multiple_subscribers_receive_notifications(self):
        """Multiple subscribers receive same notification."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        harness.subscribe_to_entity("entity_1", "subscriber_1")
        harness.subscribe_to_entity("entity_1", "subscriber_2")
        
        command = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 50},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(command)
        
        notif1 = harness.get_notifications_for_subscriber("subscriber_1")
        notif2 = harness.get_notifications_for_subscriber("subscriber_2")
        
        assert len(notif1) == 1
        assert len(notif2) == 1
        assert notif1[0].new_value == notif2[0].new_value
    
    @pytest.mark.e2e
    def test_unsubscriber_does_not_receive_notifications(self):
        """Unsubscribed entity does not receive notifications."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        harness.subscribe_to_entity("entity_1", "subscriber_1")
        harness.unsubscribe_from_entity("entity_1", "subscriber_1")
        
        command = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="entity_1",
            actor_id="system",
            payload={"value": 50},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(command)
        
        notifications = harness.get_notifications_for_subscriber("subscriber_1")
        assert len(notifications) == 0


@pytest.mark.e2e
class TestE2ESnapshots:
    """Snapshots accelerate state replay."""
    
    @pytest.mark.e2e
    def test_create_and_use_snapshot(self):
        """Snapshot preserves state for fast replay."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        
        # Add several commands
        for i in range(1, 5):
            cmd = CorrelatedCommand(
                command_id=str(uuid.uuid4()),
                command_type="SetValue",
                entity_id="entity_1",
                actor_id="system",
                payload={"value": i},
                timestamp=datetime.utcnow() + timedelta(milliseconds=i*10),
                correlation_id=str(uuid.uuid4())
            )
            harness.submit_command(cmd)
        
        # Create snapshot at version 3
        snapshot = harness.create_snapshot("entity_1", version=3)
        
        assert snapshot.entity_id == "entity_1"
        assert snapshot.version == 3
        assert snapshot.state["value"] == 4  # Latest value
    
    @pytest.mark.e2e
    def test_snapshot_allows_faster_replay(self):
        """Snapshot reduces number of events to replay."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"value": 0})
        
        # 100 commands
        for i in range(1, 101):
            cmd = CorrelatedCommand(
                command_id=str(uuid.uuid4()),
                command_type="SetValue",
                entity_id="entity_1",
                actor_id="system",
                payload={"value": i},
                timestamp=datetime.utcnow() + timedelta(milliseconds=i),
                correlation_id=str(uuid.uuid4())
            )
            harness.submit_command(cmd)
        
        # Create snapshot at version 50
        snapshot = harness.create_snapshot("entity_1", version=50)
        
        # To replay from snapshot, only need events after version 50
        events_to_replay = harness.get_events_for_entity("entity_1", since_version=50)
        
        assert len(events_to_replay) == 50  # Only last 50 events
        assert snapshot.state["value"] == 100


@pytest.mark.e2e
class TestE2EGovernanceRejection:
    """Governance policies prevent invalid commands from persisting."""
    
    @pytest.mark.e2e
    def test_policy_rejects_command_prevents_state_update(self):
        """Rejected command does not update state."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("sensitive_1", {"value": 0, "locked": False})
        
        def governance_check(cmd):
            # Reject if entity is locked
            return not harness.get_entity_state(cmd.entity_id).get("locked", False)
        
        # Lock the entity
        lock_cmd = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="Lock",
            entity_id="sensitive_1",
            actor_id="system",
            payload={"locked": True},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        harness.submit_command(lock_cmd)
        
        # Try to update while locked
        update_cmd = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="sensitive_1",
            actor_id="user_1",
            payload={"value": 100},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        success = harness.submit_command(update_cmd, governance_check_fn=governance_check)
        
        assert success is False
        state = harness.get_entity_state("sensitive_1")
        assert state["value"] == 0  # Unchanged


@pytest.mark.e2e
class TestE2EMultiEntityCascade:
    """Commands cascade through related entities."""
    
    @pytest.mark.e2e
    def test_parent_command_triggers_child_updates(self):
        """Parent entity update cascades to children."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("parent_1", {"value": 0})
        harness.initialize_entity("child_1", {"parent_value": 0})
        harness.initialize_entity("child_2", {"parent_value": 0})
        
        # Submit parent command
        parent_cmd = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="SetValue",
            entity_id="parent_1",
            actor_id="system",
            payload={"value": 100},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(parent_cmd)
        
        # Simulate cascade: children update with parent's value
        # (In real system, Tick Engine would handle this via reaction rules)
        for child_id in ["child_1", "child_2"]:
            cascade_cmd = CorrelatedCommand(
                command_id=str(uuid.uuid4()),
                command_type="UpdateFromParent",
                entity_id=child_id,
                actor_id="system",
                payload={"parent_value": 100},
                timestamp=datetime.utcnow() + timedelta(milliseconds=10),
                correlation_id=parent_cmd.correlation_id  # Same correlation
            )
            harness.submit_command(cascade_cmd)
        
        # Verify cascade
        cascade_trace = harness.cascade_traces[parent_cmd.correlation_id]
        assert "SetValue" in cascade_trace
        assert "UpdateFromParent" in cascade_trace


@pytest.mark.e2e
class TestE2ETickExecution:
    """System executes in discrete ticks."""
    
    @pytest.mark.e2e
    def test_tick_increments_counter(self):
        """Each tick increments tick counter."""
        harness = E2ESimulationHarness()
        
        for i in range(5):
            metrics = harness.execute_tick()
            assert metrics["tick"] == i + 1
    
    @pytest.mark.e2e
    def test_multiple_ticks_process_events(self):
        """Multiple ticks process multiple events."""
        harness = E2ESimulationHarness()
        harness.initialize_entity("entity_1", {"count": 0})
        
        # Submit 3 commands across 3 ticks
        for tick_num in range(3):
            cmd = CorrelatedCommand(
                command_id=str(uuid.uuid4()),
                command_type="Increment",
                entity_id="entity_1",
                actor_id="system",
                payload={"count": tick_num + 1},
                timestamp=datetime.utcnow() + timedelta(milliseconds=tick_num*100),
                correlation_id=str(uuid.uuid4())
            )
            harness.submit_command(cmd)
            harness.execute_tick()
        
        metrics = harness.execute_tick()
        assert metrics["tick"] == 4
        assert metrics["events_processed"] == 3


@pytest.mark.e2e
class TestE2ECompleteScenario:
    """Complex scenario with multiple entities, cascades, and governance."""
    
    @pytest.mark.e2e
    def test_game_round_scenario(self):
        """
        Scenario: A game has players and a round.
        - Players join
        - Round starts (governance: only 2-4 players allowed)
        - Commands trigger cascades (player score → round leaderboard)
        - Subscribers watch updates
        """
        harness = E2ESimulationHarness()
        
        # Initialize entities
        harness.initialize_entity("round_1", {"state": "waiting", "players": 0, "phase": "setup"})
        harness.initialize_entity("player_1", {"name": "Alice", "score": 0})
        harness.initialize_entity("player_2", {"name": "Bob", "score": 0})
        
        # Subscribe to updates
        harness.subscribe_to_entity("round_1", "game_ui")
        harness.subscribe_to_entity("player_1", "game_ui")
        harness.subscribe_to_entity("player_2", "game_ui")
        
        # Add players
        join_cmd_1 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="PlayerJoined",
            entity_id="round_1",
            actor_id="player_1",
            payload={"players": 1},
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid.uuid4())
        )
        
        join_cmd_2 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="PlayerJoined",
            entity_id="round_1",
            actor_id="player_2",
            payload={"players": 2},
            timestamp=datetime.utcnow() + timedelta(milliseconds=10),
            correlation_id=str(uuid.uuid4())
        )
        
        assert harness.submit_command(join_cmd_1) is True
        assert harness.submit_command(join_cmd_2) is True
        
        # Start round (governance: only with 2-4 players)
        def round_governance(cmd):
            round_state = harness.get_entity_state("round_1")
            player_count = round_state.get("players", 0)
            return 2 <= player_count <= 4
        
        start_cmd = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="StartRound",
            entity_id="round_1",
            actor_id="system",
            payload={"phase": "playing"},
            timestamp=datetime.utcnow() + timedelta(milliseconds=20),
            correlation_id=str(uuid.uuid4())
        )
        
        assert harness.submit_command(start_cmd, governance_check_fn=round_governance) is True
        
        # Players score points
        score_cmd_1 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="ScorePoints",
            entity_id="player_1",
            actor_id="system",
            payload={"score": 10},
            timestamp=datetime.utcnow() + timedelta(milliseconds=30),
            correlation_id=str(uuid.uuid4())
        )
        
        score_cmd_2 = CorrelatedCommand(
            command_id=str(uuid.uuid4()),
            command_type="ScorePoints",
            entity_id="player_2",
            actor_id="system",
            payload={"score": 15},
            timestamp=datetime.utcnow() + timedelta(milliseconds=40),
            correlation_id=str(uuid.uuid4())
        )
        
        harness.submit_command(score_cmd_1)
        harness.submit_command(score_cmd_2)
        
        # Verify final state
        round_state = harness.get_entity_state("round_1")
        player1_state = harness.get_entity_state("player_1")
        player2_state = harness.get_entity_state("player_2")
        
        assert round_state["phase"] == "playing"
        assert player1_state["score"] == 10
        assert player2_state["score"] == 15
        
        # Verify subscribers received all updates
        ui_notifications = harness.get_notifications_for_subscriber("game_ui")
        assert len(ui_notifications) >= 5  # Multiple updates


# ============================================================================
# RITUAL CLOSURE
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])