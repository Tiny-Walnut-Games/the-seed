"""
Tick Engine: Hybrid tick model with deterministic cascades.

Model: Fixed 100ms ticks + immediate event lane for reactive responses.

Architecture:
- Fixed tick loop at 100ms intervals
- Immediate event queue (processed within current tick)
- Reaction rules DSL that transforms events → cascades
- Causal chain tracing for audit logs
- Depth limiting to prevent infinite cascades
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ReactionPhase(Enum):
    """Phase of reaction execution within a tick."""
    PRE_TICK = "pre_tick"        # Before fixed tick
    IMMEDIATE = "immediate"      # Instant response to event
    CASCADE = "cascade"           # Reaction rule cascades
    POST_TICK = "post_tick"       # After fixed tick


@dataclass
class ReactionRule:
    """A rule that transforms events into cascading reactions."""
    name: str
    trigger_type: str  # Event type that triggers this rule
    depth_limit: int = 5  # Max cascade depth to prevent infinite loops
    handler: Callable = None  # Function that produces reaction events

    def apply(self, event: Dict[str, Any], depth: int = 0) -> List[Dict[str, Any]]:
        """Apply the rule to an event, respecting depth limits."""
        if depth > self.depth_limit:
            return []  # Stop cascading
        if self.handler:
            return self.handler(event, depth)
        return []


@dataclass
class CascadeTrace:
    """Audit trail for a cascade chain."""
    initial_event_id: str
    phase: ReactionPhase
    reactions: List[Dict[str, Any]] = field(default_factory=list)
    depth: int = 0
    timestamp_utc: str = ""


class TickEngine:
    """
    Hybrid tick engine: fixed ticks + immediate event lane.
    
    Mental model:
    1. Fixed tick loop runs at 100ms intervals
    2. Events can be immediate (processed this tick) or scheduled (next tick)
    3. Reactions rules cascade with depth limiting
    4. All cascades traced for determinism verification
    """

    def __init__(self, tick_interval_ms: int = 100):
        """Initialize the tick engine."""
        self.tick_interval_ms = tick_interval_ms
        self.tick_count = 0
        self.reactions = {}  # name -> ReactionRule
        self.immediate_queue = []  # Events to process this tick
        self.scheduled_queue = []  # Events for next tick
        self.cascade_traces = []  # Audit trail
        self.is_running = False
        self.tick_start_time = None

    def register_reaction(self, rule: ReactionRule):
        """Register a reaction rule."""
        self.reactions[rule.name] = rule

    def queue_immediate_event(self, event: Dict[str, Any]):
        """Queue event for immediate processing (this tick)."""
        self.immediate_queue.append(event)

    def queue_scheduled_event(self, event: Dict[str, Any]):
        """Queue event for next tick."""
        self.scheduled_queue.append(event)

    def execute_tick(self) -> Dict[str, Any]:
        """
        Execute one tick of the simulation.
        
        Returns dict with: {
            'tick_number': int,
            'events_processed': int,
            'reactions_fired': int,
            'cascade_depth': int,
            'elapsed_ms': float,
        }
        """
        self.tick_count += 1
        tick_start = time.perf_counter()
        
        # Move scheduled events to immediate for this tick
        current_events = self.immediate_queue + self.scheduled_queue
        self.immediate_queue = []
        self.scheduled_queue = []

        events_processed = 0
        reactions_fired = 0
        max_depth = 0

        # Process each event through reaction rules
        for event in current_events:
            events_processed += 1
            cascade_trace = CascadeTrace(
                initial_event_id=event.get("event_id", "unknown"),
                phase=ReactionPhase.IMMEDIATE,
                timestamp_utc=datetime.utcnow().isoformat(),
            )

            # Find and apply matching rules
            for rule_name, rule in self.reactions.items():
                if rule.trigger_type == event.get("event_type"):
                    reactions = rule.apply(event, depth=0)
                    reactions_fired += len(reactions)
                    cascade_trace.reactions.extend(reactions)
                    cascade_trace.depth = max(cascade_trace.depth, rule.depth_limit)
                    max_depth = max(max_depth, cascade_trace.depth)

            self.cascade_traces.append(cascade_trace)

        elapsed = (time.perf_counter() - tick_start) * 1000  # Convert to ms

        return {
            "tick_number": self.tick_count,
            "events_processed": events_processed,
            "reactions_fired": reactions_fired,
            "cascade_depth": max_depth,
            "elapsed_ms": elapsed,
        }

    def get_cascade_chain(self, event_id: str) -> List[CascadeTrace]:
        """Retrieve cascade chain for a specific event."""
        return [t for t in self.cascade_traces if t.initial_event_id == event_id]

    def get_tick_metrics(self) -> Dict[str, Any]:
        """Get aggregate metrics for all ticks executed."""
        if not self.cascade_traces:
            return {
                "total_ticks": self.tick_count,
                "total_events": 0,
                "total_reactions": 0,
                "avg_cascade_depth": 0,
            }

        total_events = len(self.cascade_traces)
        total_reactions = sum(len(t.reactions) for t in self.cascade_traces)
        avg_depth = sum(t.depth for t in self.cascade_traces) / total_events if total_events > 0 else 0

        return {
            "total_ticks": self.tick_count,
            "total_events": total_events,
            "total_reactions": total_reactions,
            "avg_cascade_depth": avg_depth,
        }