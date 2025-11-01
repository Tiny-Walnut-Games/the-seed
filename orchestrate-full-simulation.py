#!/usr/bin/env python3
"""
Orchestrate Full Multiverse Simulation

Launches complete simulation stack in one command:
- STAT7 backend (tick engines)
- WebSocket server
- City simulations (multiple realms)
- Warbler narrative engine
- Admin visualization
- Event streaming

Usage:
    python orchestrate-full-simulation.py
    python orchestrate-full-simulation.py --games 3 --duration 60
    python orchestrate-full-simulation.py --game-list sol_1,sol_2,sol_3
"""

import asyncio
import time
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import signal

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "web" / "server"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

from tick_engine import TickEngine, ReactionRule
from multigame_tick_engine import MultiGameTickEngine, RealmCoordinate, GameInstanceState


class OrchestratorConfig:
    """Configuration for orchestration."""
    
    def __init__(self, 
                 num_games: int = 1,
                 control_tick_interval: int = 10,
                 local_tick_ms: int = 100,
                 duration_seconds: int = None):
        self.num_games = num_games
        self.control_tick_interval = control_tick_interval
        self.local_tick_ms = local_tick_ms
        self.duration_seconds = duration_seconds  # None = infinite
        self.game_names = [f"sol_{i+1}" for i in range(num_games)]
        self.start_time = None
        self.processes: List[subprocess.Popen] = []
    
    def is_expired(self) -> bool:
        """Check if orchestrator should stop."""
        if self.duration_seconds is None:
            return False
        elapsed = time.time() - self.start_time
        return elapsed >= self.duration_seconds


class Orchestrator:
    """Main orchestration engine for multiverse simulation."""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.engine = MultiGameTickEngine(
            control_tick_interval_ticks=config.control_tick_interval,
            local_tick_interval_ms=config.local_tick_ms,
        )
        self.game_engines: Dict[str, TickEngine] = {}
        self.running = False
        self.control_loops_executed = 0
    
    async def initialize(self) -> bool:
        """Initialize all game instances and register with multiverse engine."""
        print("🚀 Orchestrator Initialization\n")
        print(f"📊 Configuration:")
        print(f"   Games: {self.config.num_games}")
        print(f"   Control-tick interval: {self.config.control_tick_interval} local ticks")
        print(f"   Local tick: {self.config.local_tick_ms}ms")
        print(f"   Duration: {'∞' if self.config.duration_seconds is None else f'{self.config.duration_seconds}s'}")
        print()
        
        # Create game instances
        for game_name in self.config.game_names:
            try:
                # Create local tick engine for this game
                tick_engine = TickEngine(tick_interval_ms=self.config.local_tick_ms)
                self.game_engines[game_name] = tick_engine
                
                # Create STAT7 realm coordinate
                realm_coord = RealmCoordinate(
                    realm_id=game_name,
                    realm_type="sol_system",
                    adjacency=f"cluster_{hash(game_name) % 4}",  # Distribute across clusters
                    resonance="narrative_prime",
                    density=0,  # Main instance
                )
                
                # Register with multiverse engine
                self.engine.register_game(game_name, tick_engine, realm_coord)
                self.engine.game_states[game_name] = GameInstanceState.RUNNING
                
                # Register for cross-game events
                self.engine.subscribe_to_events(game_name, [
                    "player_traveled",
                    "narrative_event",
                    "reputation_change",
                    "world_event",
                ])
                
            except Exception as e:
                print(f"❌ Failed to initialize {game_name}: {e}")
                return False
        
        self.config.start_time = time.time()
        print(f"✅ Initialized {len(self.game_engines)} game instances\n")
        return True
    
    async def run(self) -> None:
        """Main orchestration loop."""
        print("🎮 Orchestrator Running\n")
        self.running = True
        
        try:
            while self.running and not self.config.is_expired():
                # Execute control-tick
                control_tick_start = time.perf_counter()
                control_metrics = self.engine.execute_control_tick()
                self.control_loops_executed += 1
                
                # Simulate some cross-game events
                await self._generate_simulation_events()
                
                # Check elapsed time
                elapsed = time.time() - self.config.start_time
                print(f"⏱️  Elapsed: {elapsed:.1f}s | Control-ticks: {self.control_loops_executed}")
                
                # Small delay between control-ticks (don't slam)
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏸️  Interrupted by user")
        finally:
            self.running = False
    
    async def _generate_simulation_events(self) -> None:
        """Generate cross-game events for demonstration."""
        # Simulate occasional cross-game events
        if self.control_loops_executed % 3 == 0 and len(self.config.game_names) > 1:
            source_realm = self.config.game_names[self.control_loops_executed % len(self.config.game_names)]
            target_realm_idx = (self.control_loops_executed + 1) % len(self.config.game_names)
            target_realm = self.config.game_names[target_realm_idx]
            
            from multigame_tick_engine import CrossGameEvent
            
            event = CrossGameEvent(
                event_id=f"event_{self.control_loops_executed}_{int(time.time() * 1000)}",
                source_realm=RealmCoordinate(
                    realm_id=source_realm,
                    realm_type="sol_system",
                    adjacency="cluster_0",
                    resonance="narrative_prime",
                    density=0,
                ),
                target_realm=RealmCoordinate(
                    realm_id=target_realm,
                    realm_type="sol_system",
                    adjacency="cluster_0",
                    resonance="narrative_prime",
                    density=0,
                ),
                event_type="world_event",
                data={
                    "message": f"Traveler journeyed from {source_realm} to {target_realm}",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                control_tick_id=self.engine.control_tick_count,
            )
            
            self.engine.queue_cross_game_event(event)
    
    def print_status(self) -> None:
        """Print current multiverse status."""
        state = self.engine.get_multiverse_state()
        print("\n📊 Multiverse Status:")
        print(f"  Control-tick: {state['control_tick_id']}")
        print(f"  Local ticks: {state['local_tick_count']}")
        print(f"  Games: {state['games_registered']}")
        print(f"  Pending events: {state['pending_cross_game_events']}")
        print(f"  Avg sync time: {state['avg_sync_time_ms']:.2f}ms")
        print(f"  Avg event latency: {state['avg_event_latency_ms']:.2f}ms")
        print()
        
        for realm_id, game_state in state['game_states'].items():
            print(f"  🎮 {realm_id}")
            print(f"     State: {game_state['state']}")
            print(f"     STAT7: {game_state['stat7_key']}")
            print(f"     Ticks: {game_state['local_tick']}")
    
    def shutdown(self) -> None:
        """Graceful shutdown."""
        print("\n🛑 Orchestrator Shutting Down...")
        self.running = False
        self.print_status()
        
        # Print audit trail
        audit = self.engine.dump_audit_trail()
        print(f"\n📋 Audit Trail:")
        print(f"   Control-ticks executed: {audit['control_ticks_executed']}")
        print(f"   Total cross-game events: {audit['total_cross_game_events']}")
        
        print("\n✅ Orchestrator stopped")


async def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Orchestrate full multiverse simulation"
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of game instances to create (default: 1)",
    )
    parser.add_argument(
        "--control-tick-interval",
        type=int,
        default=10,
        help="Local ticks per control-tick (default: 10)",
    )
    parser.add_argument(
        "--local-tick-ms",
        type=int,
        default=100,
        help="Milliseconds per local tick (default: 100)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration in seconds (default: infinite)",
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = OrchestratorConfig(
        num_games=args.games,
        control_tick_interval=args.control_tick_interval,
        local_tick_ms=args.local_tick_ms,
        duration_seconds=args.duration,
    )
    
    # Create and initialize orchestrator
    orchestrator = Orchestrator(config)
    
    if not await orchestrator.initialize():
        print("❌ Failed to initialize orchestrator")
        return 1
    
    # Run orchestration
    try:
        await orchestrator.run()
    except Exception as e:
        print(f"❌ Error during orchestration: {e}")
        return 1
    finally:
        orchestrator.shutdown()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)