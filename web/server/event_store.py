"""
Production Event Store Implementation.

An append-only, file-based event log with support for:
- Immutable event append with version envelope
- State replay from events
- Snapshot creation and acceleration
- Temporal queries ("what was state at time T?")
- Correlation IDs for causal chains
- Multi-stream independence

Persistence Format: JSONL (one JSON object per line)
Stream Structure: stat7/{entity_id}.jsonl
Snapshots: stat7/{entity_id}.snapshot.json

Date: October 28, 2025
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class EventStore:
    """
    Canonical Event Store implementation.
    
    Responsibilities:
    1. Append immutable events to entity streams
    2. Replay events to reconstruct state
    3. Snapshot for faster replay
    4. Temporal queries ("as of T")
    5. Linearizable ordering via correlation IDs
    """

    def __init__(self, store_dir: str):
        """
        Initialize event store with file-based JSON backend.
        
        Args:
            store_dir: Root directory for all event streams and snapshots
        """
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._streams = {}  # In-memory index: stream_id -> List[event]

    def append_event(
        self,
        stream_id: str,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Append an immutable event to a stream.
        
        Events are:
        - Timestamped (UTC ISO format)
        - Versioned (monotonic per stream)
        - Wrapped with correlation_id (for causal chains)
        - Persisted to JSONL file
        - Indexed in memory for speed
        
        Args:
            stream_id: Unique stream identifier (e.g., "stat7/entity_1")
            event_type: Type of event (e.g., "StateSet", "StateIncrement")
            payload: Event data (application-specific)
            metadata: Optional metadata (actor, correlation_id, etc.)
        
        Returns:
            Event envelope with all metadata recorded
        """
        if metadata is None:
            metadata = {}

        # Build event envelope with immutable metadata
        event_envelope = {
            "stream_id": stream_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "event_id": str(uuid.uuid4()),
            "correlation_id": metadata.get("correlation_id", str(uuid.uuid4())),
            "actor": metadata.get("actor", "system"),
            "version": self._get_next_version(stream_id),
        }

        # Persist to file (append-only, ensure parent dirs exist)
        stream_path = self.store_dir / f"{stream_id}.jsonl"
        stream_path.parent.mkdir(parents=True, exist_ok=True)
        with open(stream_path, "a") as f:
            f.write(json.dumps(event_envelope) + "\n")

        # Update in-memory index
        if stream_id not in self._streams:
            self._streams[stream_id] = []
        self._streams[stream_id].append(event_envelope)

        return event_envelope

    def _get_next_version(self, stream_id: str) -> int:
        """
        Get the next version number for a stream (1-indexed).
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            Next version number (monotonically increasing)
        """
        if stream_id not in self._streams:
            return 1
        return len(self._streams[stream_id]) + 1

    def read_stream(
        self,
        stream_id: str,
        from_version: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Read all events from a stream, optionally starting from a version.
        
        Events are returned in append order. If the stream doesn't exist,
        returns an empty list.
        
        Args:
            stream_id: Stream identifier
            from_version: Minimum version (0 = all events, 1+ = starting version)
        
        Returns:
            List of events in order
        """
        events = []
        stream_path = self.store_dir / f"{stream_id}.jsonl"

        if not stream_path.exists():
            return []

        with open(stream_path, "r") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    # Filter by version if specified
                    if event.get("version", 0) >= from_version:
                        events.append(event)

        return events

    def read_as_of(
        self,
        stream_id: str,
        timestamp_utc: str,
    ) -> List[Dict[str, Any]]:
        """
        Read all events that occurred before a given timestamp.
        
        Enables temporal queries: "What was the state at time T?"
        
        Args:
            stream_id: Stream identifier
            timestamp_utc: ISO format timestamp (e.g., "2025-10-28T12:34:56.789...")
        
        Returns:
            List of events that occurred at or before the timestamp
        """
        events = []
        stream_path = self.store_dir / f"{stream_id}.jsonl"

        if not stream_path.exists():
            return []

        query_time = datetime.fromisoformat(timestamp_utc)

        with open(stream_path, "r") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    event_time = datetime.fromisoformat(event["timestamp_utc"])
                    # Include only events before or at the query timestamp
                    if event_time <= query_time:
                        events.append(event)

        return events

    def replay_state(
        self,
        stream_id: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reconstruct state by replaying events.
        
        If snapshot is provided, replay only events after snapshot version.
        This accelerates state reconstruction for long-lived entities.
        
        Event types:
        - StateSet: Merge payload into state
        - StateIncrement: Add delta to numeric fields
        - StateRemove: Remove specified keys
        
        Args:
            stream_id: Stream identifier
            snapshot: Optional snapshot to start from (must have _version)
        
        Returns:
            Final reconstructed state with _version and _timestamp
        """
        # Start with snapshot or empty state
        state = snapshot or {"_entity_id": stream_id, "_version": 0}

        start_version = state.get("_version", 0)
        # When replaying from snapshot, start from version AFTER snapshot
        events = self.read_stream(stream_id, from_version=start_version + 1)

        # Apply events in order
        for event in events:
            if event["event_type"] == "StateSet":
                # Merge payload into state
                state.update(event["payload"])
            elif event["event_type"] == "StateIncrement":
                # Add deltas to numeric fields
                for key, delta in event["payload"].items():
                    state[key] = state.get(key, 0) + delta
            elif event["event_type"] == "StateRemove":
                # Remove specified keys
                for key in event["payload"].get("keys", []):
                    state.pop(key, None)

            # Track metadata
            state["_version"] = event["version"]
            state["_timestamp"] = event["timestamp_utc"]

        return state

    def create_snapshot(
        self,
        stream_id: str,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a snapshot of current state for faster replay.
        
        Snapshots are stored separately from event log and referenced
        during replay to skip early events.
        
        Args:
            stream_id: Stream identifier
            state: Current state to snapshot
        
        Returns:
            Snapshot metadata
        """
        snapshot = {
            "stream_id": stream_id,
            "state": state,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "snapshot_id": str(uuid.uuid4()),
        }

        snapshot_path = self.store_dir / f"{stream_id}.snapshot.json"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot

    def get_latest_snapshot(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest snapshot for a stream, if it exists.
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            Snapshot object or None if no snapshot exists
        """
        snapshot_path = self.store_dir / f"{stream_id}.snapshot.json"

        if not snapshot_path.exists():
            return None

        with open(snapshot_path, "r") as f:
            return json.load(f)

    def list_streams(self) -> List[str]:
        """
        List all streams in the store.
        
        Returns sorted list of stream identifiers (not including snapshots).
        
        Returns:
            List of stream IDs
        """
        streams = set()
        # Recursively find all .jsonl files (not snapshots)
        for path in self.store_dir.rglob("*.jsonl"):
            # Get the relative path and remove .jsonl extension
            rel_path = path.relative_to(self.store_dir)
            stream_id = str(rel_path.with_suffix("")).replace("\\", "/")
            streams.add(stream_id)
        return sorted(list(streams))