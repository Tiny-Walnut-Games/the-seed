"""
End-to-End Simulation Engine (Layer 5: Full System Integration)

Provides E2ESimulationHarness, a complete simulation of the five-layer architecture:
Event Store, Tick Engine, Governance, and API Gateway working in concert.

Supports:
- Multi-entity state coordination
- Event correlation across entities
- Temporal consistency (state as of timestamp)
- Error recovery (governance-based command rejection)
- Long-running simulations (tick-based execution)
- Subscription lifecycle (state change notifications)
- State consistency under cascades
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
import uuid


@dataclass
class StateChange:
    """A single state change in an entity."""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime


@dataclass
class EntitySnapshot:
    """Immutable snapshot of entity state at a point in time."""
    entity_id: str
    version: int
    timestamp: datetime
    state: Dict[str, Any]
    correlation_id: str


@dataclass
class CorrelatedCommand:
    """Command that may trigger cascades in related entities."""
    command_id: str
    command_type: str
    entity_id: str
    actor_id: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str
    depends_on: List[str] = field(default_factory=list)  # Previous commands


@dataclass
class SimulationScenario:
    """A test scenario describing a sequence of operations."""
    name: str
    description: str
    entities_to_create: List[str]
    initial_state: Dict[str, Dict[str, Any]]
    commands: List[CorrelatedCommand]
    expected_final_state: Dict[str, Dict[str, Any]]
    expected_events_per_entity: Dict[str, int]
    max_cascade_depth: int = 3


class E2ESimulationHarness:
    """
    Harness that simulates a complete system execution.
    
    Orchestrates Event Store, Tick Engine, Governance, and API Gateway
    as if they were a real deployed system.
    """
    
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.entity_versions: Dict[str, int] = {}
        self.entity_initial_state: Dict[str, Dict[str, Any]] = {}  # Track initial state for temporal queries
        self.entity_creation_time: Dict[str, datetime] = {}  # Track when entity was created
        self.event_log: List[Dict[str, Any]] = []
        self.snapshots: Dict[str, List[EntitySnapshot]] = {}
        self.subscriptions: Dict[str, List[str]] = {}  # entity_id -> [subscriber_ids]
        self.notifications: Dict[str, List[StateChange]] = {}  # subscriber_id -> [changes]
        self.tick_count = 0
        self.cascade_traces: Dict[str, List[str]] = {}  # correlation_id -> [event_trace]
    
    def initialize_entity(self, entity_id: str, initial_state: Dict[str, Any]) -> None:
        """Create an entity with initial state."""
        self.entities[entity_id] = dict(initial_state)
        self.entity_initial_state[entity_id] = dict(initial_state)  # Store for temporal queries
        self.entity_creation_time[entity_id] = datetime.utcnow()
        self.entity_versions[entity_id] = 0
        self.snapshots[entity_id] = []
        self.subscriptions[entity_id] = []
        self.cascade_traces[entity_id] = []
    
    def submit_command(
        self,
        command: CorrelatedCommand,
        governance_check_fn: Optional[Callable[[CorrelatedCommand], bool]] = None
    ) -> bool:
        """
        Submit a command. Returns True if processed, False if rejected.
        
        Governance check is optional (governs whether command is accepted).
        """
        # Check governance
        if governance_check_fn and not governance_check_fn(command):
            return False
        
        # Record in event log
        event_record = {
            "event_id": str(uuid.uuid4()),
            "command_id": command.command_id,
            "command_type": command.command_type,
            "entity_id": command.entity_id,
            "actor_id": command.actor_id,
            "version": self.entity_versions.get(command.entity_id, 0) + 1,
            "payload": command.payload,
            "timestamp": command.timestamp,
            "correlation_id": command.correlation_id,
        }
        self.event_log.append(event_record)
        
        # Increment entity version
        if command.entity_id not in self.entity_versions:
            self.entity_versions[command.entity_id] = 0
        self.entity_versions[command.entity_id] += 1
        
        # Apply to entity state (payload becomes state delta)
        if command.entity_id not in self.entities:
            self.entities[command.entity_id] = {}
        
        for key, value in command.payload.items():
            old_value = self.entities[command.entity_id].get(key)
            self.entities[command.entity_id][key] = value
            
            # Record notification for subscribers
            change = StateChange(
                key=key,
                old_value=old_value,
                new_value=value,
                timestamp=command.timestamp
            )
            
            for subscriber_id in self.subscriptions.get(command.entity_id, []):
                if subscriber_id not in self.notifications:
                    self.notifications[subscriber_id] = []
                self.notifications[subscriber_id].append(change)
        
        # Trace in cascade log
        if command.correlation_id not in self.cascade_traces:
            self.cascade_traces[command.correlation_id] = []
        self.cascade_traces[command.correlation_id].append(command.command_type)
        
        return True
    
    def execute_tick(self) -> Dict[str, int]:
        """
        Simulate one tick (100ms). Returns metrics.
        """
        self.tick_count += 1
        return {
            "tick": self.tick_count,
            "events_processed": len(self.event_log),
            "entities_updated": len([e for e in self.entities if self.entity_versions.get(e, 0) > 0])
        }
    
    def subscribe_to_entity(self, entity_id: str, subscriber_id: str) -> None:
        """Subscribe to entity state changes."""
        if entity_id not in self.subscriptions:
            self.subscriptions[entity_id] = []
        self.subscriptions[entity_id].append(subscriber_id)
        self.notifications[subscriber_id] = []
    
    def unsubscribe_from_entity(self, entity_id: str, subscriber_id: str) -> None:
        """Unsubscribe from entity."""
        if entity_id in self.subscriptions:
            self.subscriptions[entity_id] = [
                s for s in self.subscriptions[entity_id] if s != subscriber_id
            ]
    
    def get_entity_state(self, entity_id: str) -> Dict[str, Any]:
        """Get current entity state."""
        return self.entities.get(entity_id, {})
    
    def get_entity_state_as_of(
        self,
        entity_id: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Get entity state as it was at a specific time."""
        # If entity doesn't exist, return empty
        if entity_id not in self.entity_initial_state:
            return {}
        
        # Start with initial state (exists from moment of creation)
        state = dict(self.entity_initial_state[entity_id])
        
        # Apply all events that occurred before or at timestamp
        relevant_events = [
            e for e in self.event_log
            if e["entity_id"] == entity_id and e["timestamp"] <= timestamp
        ]
        
        # Replay events on top of initial state
        for event in relevant_events:
            for key, value in event["payload"].items():
                state[key] = value
        
        return state
    
    def create_snapshot(self, entity_id: str, version: int) -> EntitySnapshot:
        """Create a snapshot of entity state."""
        snapshot = EntitySnapshot(
            entity_id=entity_id,
            version=version,
            timestamp=datetime.utcnow(),
            state=dict(self.entities.get(entity_id, {})),
            correlation_id=str(uuid.uuid4())
        )
        
        if entity_id not in self.snapshots:
            self.snapshots[entity_id] = []
        self.snapshots[entity_id].append(snapshot)
        
        return snapshot
    
    def get_events_for_entity(
        self,
        entity_id: str,
        since_version: int = 0,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve events for an entity."""
        events = [
            e for e in self.event_log
            if e["entity_id"] == entity_id and e["version"] > since_version
        ]
        
        if limit:
            events = events[:limit]
        
        return events
    
    def get_notifications_for_subscriber(self, subscriber_id: str) -> List[StateChange]:
        """Get all notifications received by a subscriber."""
        return self.notifications.get(subscriber_id, [])
    
    def verify_state_consistency(self, scenario: SimulationScenario) -> bool:
        """Verify that final state matches expected state."""
        for entity_id, expected_state in scenario.expected_final_state.items():
            actual_state = self.get_entity_state(entity_id)
            for key, expected_value in expected_state.items():
                actual_value = actual_state.get(key)
                if actual_value != expected_value:
                    return False
        return True
    
    def clear(self) -> None:
        """Clear all state (for testing)."""
        self.entities.clear()
        self.entity_versions.clear()
        self.entity_initial_state.clear()
        self.entity_creation_time.clear()
        self.event_log.clear()
        self.snapshots.clear()
        self.subscriptions.clear()
        self.notifications.clear()
        self.cascade_traces.clear()
        self.tick_count = 0