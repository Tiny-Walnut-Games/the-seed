"""
MultiGame Tick Engine: Control-Tick Architecture for Multiverse Simulation

Model: Master control-tick + local game ticks with periodic synchronization.

Architecture:
- Master control-tick coordinates all game instances (sol-systems)
- Each game runs local 100ms ticks independently
- Periodic sync to control-tick (every N local ticks)
- STAT7 addressing used for realm/chunk/instance routing
- Subtle temporal shift: all games experience time locally, but coordinate globally
- Supports chunking/instancing for hardware load distribution

Example:
    engine = MultiGameTickEngine(control_tick_interval_ticks=10)
    engine.register_game("sol_1", city_simulation_a)
    engine.register_game("sol_2", city_simulation_b)
    
    engine.execute_control_tick()  # Syncs all games to master clock
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from tick_engine import TickEngine, ReactionRule, ReactionPhase, CascadeTrace


class GameInstanceState(Enum):
    """State of a game instance within the multiverse."""
    OFFLINE = "offline"
    BOOTING = "booting"
    RUNNING = "running"
    SYNCING = "syncing"  # Syncing to control-tick
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class RealmCoordinate:
    """STAT7-based coordinate for realm identification."""
    realm_id: str  # Unique game instance identifier
    realm_type: str  # "sol_system", "chunk", "instance"
    
    # STAT7 dimensions (subset used for routing)
    adjacency: str  # Proximity/region grouping
    resonance: str  # Narrative context
    density: int  # Instance multiplicity (0=main, 1+=alt instances)
    
    def to_stat7_key(self) -> str:
        """Convert to STAT7 key for addressing."""
        return f"{self.realm_id}:{self.adjacency}:{self.resonance}:{self.density}"


@dataclass
class CrossGameEvent:
    """Event that can traverse between game instances."""
    event_id: str
    source_realm: RealmCoordinate
    target_realm: Optional[RealmCoordinate]  # None = broadcast to all
    event_type: str
    data: Dict[str, Any]
    control_tick_id: int  # Which control-tick this originated from
    timestamp_utc: str = ""
    propagation_path: List[str] = field(default_factory=list)  # Audit trail


@dataclass
class ControlTickTrace:
    """Audit trail for a control-tick event."""
    control_tick_id: int
    timestamp_utc: str
    games_synced: List[str] = field(default_factory=list)
    events_propagated: int = 0
    cascade_depth: int = 0
    elapsed_ms: float = 0.0


class MultiGameTickEngine:
    """
    Master orchestrator for multiverse simulation.
    
    Coordinates multiple game instances with:
    - Master control-tick for temporal synchronization
    - Local tick independence for each game
    - Periodic sync points where games align
    - Cross-game event routing via STAT7 addressing
    - Deterministic causality tracking across realms
    """
    
    def __init__(self, 
                 control_tick_interval_ticks: int = 10,
                 local_tick_interval_ms: int = 100):
        """
        Initialize MultiGame Tick Engine.
        
        Args:
            control_tick_interval_ticks: How many local ticks before control-tick fires
            local_tick_interval_ms: Milliseconds per local tick (typically 100ms)
        """
        self.control_tick_interval_ticks = control_tick_interval_ticks
        self.local_tick_interval_ms = local_tick_interval_ms
        
        # Control-tick tracking
        self.control_tick_count = 0
        self.local_tick_count = 0
        self.is_running = False
        
        # Game registry: realm_id -> (TickEngine, RealmCoordinate)
        self.games: Dict[str, tuple] = {}  # (tick_engine, realm_coord)
        self.game_states: Dict[str, GameInstanceState] = {}
        
        # Cross-game event routing
        self.cross_game_events: List[CrossGameEvent] = []
        self.event_subscriptions: Dict[str, List[str]] = defaultdict(list)  # event_type -> [realm_ids]
        
        # Audit trails
        self.control_tick_traces: List[ControlTickTrace] = []
        self.cascade_traces_by_realm: Dict[str, List[CascadeTrace]] = defaultdict(list)
        
        # Performance metrics
        self.sync_times_ms: List[float] = []
        self.event_latencies_ms: List[float] = []
        
    def register_game(self, realm_id: str, 
                      tick_engine: TickEngine,
                      realm_coord: RealmCoordinate) -> None:
        """
        Register a game instance to the multiverse.
        
        Args:
            realm_id: Unique identifier for this game
            tick_engine: The TickEngine managing this game's local ticks
            realm_coord: STAT7 coordinate for this realm
        """
        if realm_id in self.games:
            raise ValueError(f"Realm {realm_id} already registered")
        
        self.games[realm_id] = (tick_engine, realm_coord)
        self.game_states[realm_id] = GameInstanceState.BOOTING
        print(f"✅ Registered realm: {realm_id} at {realm_coord.to_stat7_key()}")
    
    def unregister_game(self, realm_id: str) -> None:
        """Unregister a game instance."""
        if realm_id in self.games:
            del self.games[realm_id]
            del self.game_states[realm_id]
            print(f"❌ Unregistered realm: {realm_id}")
    
    def subscribe_to_events(self, realm_id: str, event_types: List[str]) -> None:
        """
        Subscribe a game to cross-game events.
        
        Args:
            realm_id: Game instance ID
            event_types: List of event type strings to subscribe to
        """
        for event_type in event_types:
            if realm_id not in self.event_subscriptions[event_type]:
                self.event_subscriptions[event_type].append(realm_id)
    
    def queue_cross_game_event(self, event: CrossGameEvent) -> None:
        """Queue an event for cross-game propagation."""
        event.timestamp_utc = datetime.utcnow().isoformat()
        self.cross_game_events.append(event)
    
    def execute_local_tick(self, realm_id: str) -> Dict[str, Any]:
        """
        Execute one local tick for a specific game.
        
        Args:
            realm_id: Which game to tick
            
        Returns:
            Tick metrics dict
        """
        if realm_id not in self.games:
            raise ValueError(f"Unknown realm: {realm_id}")
        
        tick_engine, _ = self.games[realm_id]
        self.local_tick_count += 1
        
        # Execute local tick
        metrics = tick_engine.execute_tick()
        
        # Capture cascade traces for audit
        self.cascade_traces_by_realm[realm_id].extend(tick_engine.cascade_traces[-len(tick_engine.cascade_traces):])
        
        return metrics
    
    def execute_control_tick(self) -> Dict[str, Any]:
        """
        Execute master control-tick: synchronizes all games.
        
        This is the "subtle temporal shift" point where all games
        align to the master timeline, but players don't notice because
        it happens smoothly across local tick cycles.
        
        Returns:
            Control-tick metrics
        """
        control_start = time.perf_counter()
        self.control_tick_count += 1
        
        trace = ControlTickTrace(
            control_tick_id=self.control_tick_count,
            timestamp_utc=datetime.utcnow().isoformat(),
        )
        
        # Phase 1: Sync all games to control-tick
        print(f"\n⏰ CONTROL-TICK {self.control_tick_count} Starting...")
        synced_games = []
        
        for realm_id, (tick_engine, realm_coord) in self.games.items():
            try:
                self.game_states[realm_id] = GameInstanceState.SYNCING
                
                # Execute pending local ticks for this game
                while self.local_tick_count % self.control_tick_interval_ticks != 0:
                    self.execute_local_tick(realm_id)
                
                self.game_states[realm_id] = GameInstanceState.RUNNING
                synced_games.append(realm_id)
                trace.games_synced.append(realm_id)
                
            except Exception as e:
                self.game_states[realm_id] = GameInstanceState.ERROR
                print(f"  ❌ {realm_id}: Sync error: {e}")
        
        # Phase 2: Propagate cross-game events
        events_propagated = self._propagate_cross_game_events()
        trace.events_propagated = events_propagated
        
        # Phase 3: Update metrics
        elapsed = (time.perf_counter() - control_start) * 1000
        trace.elapsed_ms = elapsed
        self.sync_times_ms.append(elapsed)
        self.control_tick_traces.append(trace)
        
        print(f"  ✅ Synced {len(synced_games)} games")
        print(f"  📡 Propagated {events_propagated} cross-game events")
        print(f"  ⏱️  Control-tick took {elapsed:.2f}ms\n")
        
        return {
            "control_tick_id": self.control_tick_count,
            "games_synced": len(synced_games),
            "events_propagated": events_propagated,
            "elapsed_ms": elapsed,
        }
    
    def _propagate_cross_game_events(self) -> int:
        """
        Propagate queued cross-game events to subscribed realms.
        
        Uses STAT7 addressing to route events intelligently.
        """
        if not self.cross_game_events:
            return 0
        
        events_to_process = self.cross_game_events[:]
        self.cross_game_events = []
        
        propagated_count = 0
        
        for event in events_to_process:
            # Determine target realms
            if event.target_realm:
                # Unicast to specific realm
                target_realms = [event.target_realm.realm_id]
            else:
                # Broadcast to all subscribed realms
                target_realms = self.event_subscriptions.get(event.event_type, [])
            
            # Route event to each target
            for target_realm_id in target_realms:
                if target_realm_id in self.games:
                    tick_engine, realm_coord = self.games[target_realm_id]
                    
                    # Convert to local event and queue
                    local_event = {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "source_realm": event.source_realm.realm_id,
                        "data": event.data,
                        "control_tick_id": self.control_tick_count,
                    }
                    
                    # Track propagation path for audit
                    event.propagation_path.append(target_realm_id)
                    
                    # Queue as immediate event in target game
                    tick_engine.queue_immediate_event(local_event)
                    propagated_count += 1
                    
                    # Track latency
                    latency_ms = (time.time() - (datetime.fromisoformat(event.timestamp_utc).timestamp())) * 1000
                    self.event_latencies_ms.append(latency_ms)
        
        return propagated_count
    
    def get_multiverse_state(self) -> Dict[str, Any]:
        """Get current state of entire multiverse."""
        game_states_summary = {
            realm_id: {
                "state": self.game_states[realm_id].value,
                "stat7_key": coord.to_stat7_key(),
                "local_tick": self.games[realm_id][0].tick_count,
            }
            for realm_id, (_, coord) in self.games.items()
        }
        
        return {
            "control_tick_id": self.control_tick_count,
            "local_tick_count": self.local_tick_count,
            "games_registered": len(self.games),
            "game_states": game_states_summary,
            "pending_cross_game_events": len(self.cross_game_events),
            "avg_sync_time_ms": sum(self.sync_times_ms) / len(self.sync_times_ms) if self.sync_times_ms else 0,
            "avg_event_latency_ms": sum(self.event_latencies_ms) / len(self.event_latencies_ms) if self.event_latencies_ms else 0,
        }
    
    def get_cascade_chain(self, realm_id: str, event_id: str) -> List[CascadeTrace]:
        """Retrieve cascade chain for a cross-realm event."""
        if realm_id not in self.cascade_traces_by_realm:
            return []
        return [t for t in self.cascade_traces_by_realm[realm_id] 
                if t.initial_event_id == event_id]
    
    def dump_audit_trail(self) -> Dict[str, Any]:
        """Full audit trail for determinism verification."""
        return {
            "control_ticks_executed": len(self.control_tick_traces),
            "total_cross_game_events": len([e for t in self.control_tick_traces 
                                           for e in self.cross_game_events]),
            "control_tick_traces": [
                {
                    "id": t.control_tick_id,
                    "timestamp": t.timestamp_utc,
                    "games_synced": t.games_synced,
                    "events_propagated": t.events_propagated,
                    "elapsed_ms": t.elapsed_ms,
                }
                for t in self.control_tick_traces
            ],
        }