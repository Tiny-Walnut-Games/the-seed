"""
Unified Backend API Gateway (Layer 3).

Bridges external clients (Unity, Three.js, CLI) to the internal tick engine.

Model:
- Commands are validated by governance, persisted to event store, queued for cascade
- Entities are queried via read-model (derived by replaying event stream)
- Events can be streamed for audit/replay with pagination
- WebSocket subscriptions deliver live state deltas

This module is imported by clients and depends on:
- EventStore (for persistence and replay)
- TickEngine (for queuing cascade processing)
- GovernanceMiddleware (for policy validation, optional)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Callable, Optional


# ============================================================================
# EXCEPTIONS
# ============================================================================

class CommandValidationError(Exception):
    """Command failed validation by governance."""
    pass


class EntityNotFoundError(Exception):
    """Entity does not exist."""
    pass


# ============================================================================
# DATA MODELS (Request/Response Contract)
# ============================================================================

@dataclass
class CommandRequest:
    """A command submitted to the API."""
    entity_id: str
    command_type: str
    payload: Dict[str, Any]
    actor: str = "client"


@dataclass
class CommandResponse:
    """Response from a command submission."""
    command_id: str
    status: str  # "accepted", "rejected", "applied"
    entity_id: str
    message: str = ""
    applied_event_id: str = None


@dataclass
class EntityReadModel:
    """State snapshot of an entity at a point in time."""
    entity_id: str
    state: Dict[str, Any]
    version: int
    timestamp_utc: str
    as_of: str = None  # Temporal query timestamp if applicable


# ============================================================================
# GOVERNANCE MIDDLEWARE
# ============================================================================

class GovernanceMiddleware:
    """
    Governance layer that validates commands before execution.
    
    Mental model: Policies that can accept, reject, or mutate commands.
    """

    def __init__(self):
        self.policies = []

    def add_policy(self, name: str, check_fn: Callable[[CommandRequest], bool]):
        """Add a governance policy."""
        self.policies.append({"name": name, "check": check_fn})

    def is_permitted(self, command: CommandRequest) -> bool:
        """Check if command passes all governance policies."""
        for policy in self.policies:
            if not policy["check"](command):
                return False
        return True


# ============================================================================
# API GATEWAY
# ============================================================================

class APIGateway:
    """
    Unified API Gateway.
    
    Mental model:
    1. Commands are validated, persisted to event store, queued for tick engine
    2. Entities are queried from read-model (derived from event store)
    3. Events can be streamed for audit/replay
    4. WebSocket subscriptions deliver live deltas
    """

    def __init__(
        self,
        event_store,
        tick_engine,
        governance: Optional[GovernanceMiddleware] = None
    ):
        """Initialize gateway with dependencies."""
        self.event_store = event_store
        self.tick_engine = tick_engine
        self.governance = governance
        self.read_model = {}  # entity_id -> EntityReadModel
        self.subscriptions = {}  # subscription_id -> {entity_ids: set, callback}
        self.client_counter = 0

    def submit_command(self, command: CommandRequest) -> CommandResponse:
        """
        Submit a command to the system.
        
        Flow:
        1. Validate by governance (reject if policy violated)
        2. Append to event store
        3. Queue for tick engine
        4. Return accepted response
        
        Args:
            command: CommandRequest to submit
            
        Returns:
            CommandResponse with status and command ID
            
        Raises:
            CommandValidationError: If governance policy rejects the command
        """
        # Validate
        if self.governance:
            if not self.governance.is_permitted(command):
                raise CommandValidationError(
                    f"Governance policy rejected: {command.command_type}"
                )

        # Persist
        event = self.event_store.append_event(
            stream_id=f"stat7/{command.entity_id}",
            event_type=f"Command:{command.command_type}",
            payload=command.payload,
            metadata={"actor": command.actor},
        )

        # Queue for cascade
        self.tick_engine.queue_immediate_event(event)

        return CommandResponse(
            command_id=event["event_id"],
            status="accepted",
            entity_id=command.entity_id,
            applied_event_id=event["event_id"],
        )

    def get_entity(self, entity_id: str, as_of: str = None) -> EntityReadModel:
        """
        Retrieve entity state.
        
        Returns read-model snapshot, optionally from a specific timestamp.
        
        Args:
            entity_id: Entity to retrieve
            as_of: Optional timestamp for temporal read
            
        Returns:
            EntityReadModel with current state and version
            
        Raises:
            EntityNotFoundError: If entity has no events
        """
        stream_id = f"stat7/{entity_id}"

        # Temporal read if as_of provided
        if as_of:
            events = self.event_store.read_as_of(stream_id, as_of)
        else:
            events = self.event_store.read_stream(stream_id)

        if not events:
            raise EntityNotFoundError(f"Entity not found: {entity_id}")

        # Replay state
        state = self.event_store.replay_state(stream_id)

        latest_event = events[-1] if events else {}

        return EntityReadModel(
            entity_id=entity_id,
            state=state,
            version=latest_event.get("version", 0),
            timestamp_utc=latest_event.get("timestamp_utc", ""),
            as_of=as_of,
        )

    def get_events(
        self,
        entity_id: str,
        since_version: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve event stream for audit/replay.
        
        Supports pagination with version offset and limit.
        
        Args:
            entity_id: Entity to retrieve events for
            since_version: Start from this version (inclusive)
            limit: Maximum number of events to return
            
        Returns:
            List of events, empty list if entity doesn't exist
        """
        stream_id = f"stat7/{entity_id}"
        events = self.event_store.read_stream(stream_id, from_version=since_version)
        return events[:limit]

    def subscribe_to_entity(
        self,
        entity_id: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to live updates for an entity.
        
        Args:
            entity_id: Entity to subscribe to
            callback: Function called with {subscription_id, entity_id, delta}
            
        Returns:
            subscription_id: Unique identifier for this subscription
        """
        sub_id = f"sub_{self.client_counter}"
        self.client_counter += 1

        if sub_id not in self.subscriptions:
            self.subscriptions[sub_id] = {
                "entity_ids": set(),
                "callback": callback,
            }

        self.subscriptions[sub_id]["entity_ids"].add(entity_id)
        return sub_id

    def unsubscribe(self, subscription_id: str):
        """
        Unsubscribe from all entities.
        
        Args:
            subscription_id: Subscription ID to remove
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]

    def publish_entity_delta(self, entity_id: str, delta: Dict[str, Any]):
        """
        Publish a state delta to all subscribers.
        
        Called by tick engine after cascades complete.
        Only subscribers who subscribed to this entity_id receive the message.
        
        Args:
            entity_id: Entity that changed
            delta: State changes {key: value}
        """
        for sub_id, sub in self.subscriptions.items():
            if entity_id in sub["entity_ids"]:
                sub["callback"](
                    {
                        "subscription_id": sub_id,
                        "entity_id": entity_id,
                        "delta": delta,
                    }
                )