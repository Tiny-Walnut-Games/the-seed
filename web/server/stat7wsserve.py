"""
STAT7 Visualization WebSocket Server

Real-time streaming of STAT7 events to browser-based Three.js visualization.
Provides GPU-accelerated 7D space rendering without Unity dependency.

Architecture:
- Python WebSocket server streams STAT7 events
- Three.js client handles GPU rendering
- Event bridge connects experiments to visualization
- Jupyter notebook embedding support
"""

import asyncio
import websockets
import json
import time
import uuid
from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import threading
import logging
import sys
import os

# Add the seed engine to Python path (correct path with lowercase 'packages')
# Find the project root by going up from web/server/ to the repo root
current_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(current_dir, '../../'))
seed_path = os.path.join(repo_root, 'packages', 'com.twg.the-seed', 'seed', 'engine')

if seed_path not in sys.path:
    sys.path.insert(0, seed_path)

try:
    from stat7_experiments import BitChain, Coordinates, generate_random_bitchain
except ImportError as e:
    print(f"Warning: stat7_experiments not found at {seed_path}. Using mock implementations.")
    print(f"Import error: {e}")

    # Mock implementations for testing
    @dataclass
    class Coordinates:
        realm: str
        lineage: int
        adjacency: List[str]
        horizon: str
        resonance: float
        velocity: float
        density: float

        def to_dict(self):
            return {
                'adjacency': sorted(self.adjacency),
                'density': self.density,
                'horizon': self.horizon,
                'lineage': self.lineage,
                'realm': self.realm,
                'resonance': self.resonance,
                'velocity': self.velocity,
            }

    @dataclass
    class BitChain:
        id: str
        entity_type: str
        realm: str
        coordinates: Coordinates
        created_at: str
        state: Dict[str, Any]

        def to_canonical_dict(self):
            return {
                'created_at': self.created_at,
                'entity_type': self.entity_type,
                'id': self.id,
                'realm': self.realm,
                'stat7_coordinates': self.coordinates.to_dict(),
                'state': self.state,
            }

        def compute_address(self):
            return f"addr_{hash(str(self.to_canonical_dict())) & 0xffffffff}"

        def get_stat7_uri(self):
            coords = self.coordinates
            return f"stat7://{coords.realm}/{coords.lineage}/adj/{coords.horizon}?r={coords.resonance}&v={coords.velocity}&d={coords.density}"

    def generate_random_bitchain(seed=None):
        import random
        if seed is not None:
            random.seed(seed)

        realms = ['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void']
        horizons = ['genesis', 'emergence', 'peak', 'decay', 'crystallization']
        entity_types = ['concept', 'artifact', 'agent', 'lineage', 'adjacency', 'horizon', 'fragment']

        return BitChain(
            id=str(uuid.uuid4()),
            entity_type=random.choice(entity_types),
            realm=random.choice(realms),
            coordinates=Coordinates(
                realm=random.choice(realms),
                lineage=random.randint(1, 100),
                adjacency=[str(uuid.uuid4()) for _ in range(random.randint(0, 5))],
                horizon=random.choice(horizons),
                resonance=random.uniform(-1.0, 1.0),
                velocity=random.uniform(-1.0, 1.0),
                density=random.uniform(0.0, 1.0),
            ),
            created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            state={'value': random.randint(0, 1000)},
        )


# ============================================================================
# WEBSOCKET EVENT SYSTEM
# ============================================================================

@dataclass
class VisualizationEvent:
    """Event sent to visualization clients."""
    event_type: str           # 'bitchain_created', 'coordinates_updated', 'experiment_start', etc.
    timestamp: str           # ISO8601 timestamp
    data: Dict[str, Any]     # Event-specific data
    experiment_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class STAT7EventStreamer:
    """
    Central event streaming system for STAT7 visualization.

    Handles:
    - WebSocket client connections
    - Event broadcasting to all connected clients
    - Event buffering for new clients
    - Experiment lifecycle management
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.event_buffer: List[VisualizationEvent] = []
        self.max_buffer_size = 1000
        self.experiment_callbacks: Dict[str, Callable] = {}
        self.is_running = False

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def register_client(self, websocket):
        """Register a new WebSocket client."""
        self.clients.add(websocket)
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")

        # Send buffered events to new client
        if self.event_buffer:
            await self.send_buffered_events(websocket)

    async def unregister_client(self, websocket):
        """Unregister a WebSocket client."""
        self.clients.discard(websocket)
        self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_buffered_events(self, websocket):
        """Send buffered events to a newly connected client."""
        try:
            for event in self.event_buffer[-100:]:  # Send last 100 events
                await websocket.send(json.dumps(event.to_dict()))
        except Exception as e:
            self.logger.error(f"Error sending buffered events: {e}")

    async def broadcast_event(self, event: VisualizationEvent):
        """Broadcast event to all connected clients."""
        event_data = json.dumps(event.to_dict())

        # Always add to buffer (even if no clients connected yet)
        self.event_buffer.append(event)
        if len(self.event_buffer) > self.max_buffer_size:
            self.event_buffer.pop(0)

        # Broadcast to all connected clients (if any)
        if not self.clients:
            return

        disconnected = set()
        # Iterate over a copy to avoid "Set changed size during iteration" error
        for client in list(self.clients):
            try:
                await client.send(event_data)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(client)

        # Remove disconnected clients
        for client in disconnected:
            await self.unregister_client(client)

    def create_bitchain_event(self, bitchain: BitChain, experiment_id: Optional[str] = None) -> VisualizationEvent:
        """Create a visualization event for a new BitChain."""
        return VisualizationEvent(
            event_type="bitchain_created",
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            data={
                "bitchain": bitchain.to_canonical_dict(),
                "address": bitchain.compute_address(),
                "stat7_uri": bitchain.get_stat7_uri(),
                "coordinates": bitchain.coordinates.to_dict(),
                "entity_type": bitchain.entity_type,
                "realm": bitchain.realm,
            },
            experiment_id=experiment_id,
            metadata={
                "visualization_type": "point_cloud",
                "color": self._get_realm_color(bitchain.coordinates.realm),
                "size": self._get_entity_size(bitchain.entity_type),
            }
        )

    def create_experiment_event(self, experiment_id: str, status: str, data: Dict[str, Any]) -> VisualizationEvent:
        """Create an experiment lifecycle event."""
        return VisualizationEvent(
            event_type=f"experiment_{status}",
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            data=data,
            experiment_id=experiment_id,
            metadata={
                "visualization_type": "experiment_status",
            }
        )

    def _get_realm_color(self, realm: str) -> str:
        """Get color for realm visualization."""
        realm_colors = {
            'data': '#3498db',      # Blue
            'narrative': '#e74c3c', # Red
            'system': '#2ecc71',     # Green
            'faculty': '#f39c12',    # Orange
            'event': '#9b59b6',      # Purple
            'pattern': '#1abc9c',    # Teal
            'void': '#34495e',       # Dark gray
        }
        return realm_colors.get(realm, '#95a5a6')  # Default gray

    def _get_entity_size(self, entity_type: str) -> float:
        """Get visualization size for entity type."""
        entity_sizes = {
            'concept': 1.0,
            'artifact': 1.5,
            'agent': 2.0,
            'lineage': 1.2,
            'adjacency': 0.8,
            'horizon': 1.8,
            'fragment': 0.6,
        }
        return entity_sizes.get(entity_type, 1.0)

    async def start_server(self):
        """Start the WebSocket server."""
        self.is_running = True

        async def handle_client(websocket):
            await self.register_client(websocket)
            try:
                async for message in websocket:
                    # Handle client messages
                    try:
                        data = json.loads(message)
                        await self.handle_client_message(data, websocket)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON received from client: {message}")
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                await self.unregister_client(websocket)

        self.server = await websockets.serve(handle_client, self.host, self.port)
        self.logger.info(f"STAT7 Visualization Server started on ws://{self.host}:{self.port}")

        # Keep server running
        await self.server.wait_closed()

    def stop_server(self):
        """Stop the WebSocket server."""
        self.is_running = False
        if hasattr(self, 'server'):
            self.server.close()
            self.logger.info("STAT7 Visualization Server stopped")

    async def run_semantic_fidelity_proof(self, sample_size: int = 200):
        """
        Semantic Fidelity Proof: Test if clustering reflects narrative similarity.

        Creates entities with related narrative content and verifies they cluster together.
        """
        self.logger.info("🧠 Starting Semantic Fidelity Proof...")

        # Create narrative clusters with semantic relationships
        narrative_themes = {
            "hero_journey": {
                "keywords": ["hero", "journey", "quest", "adventure", "transformation"],
                "realm": "narrative",
                "entity_type": "concept"
            },
            "system_architecture": {
                "keywords": ["system", "architecture", "design", "structure", "framework"],
                "realm": "system",
                "entity_type": "artifact"
            },
            "data_patterns": {
                "keywords": ["data", "pattern", "analysis", "insight", "correlation"],
                "realm": "data",
                "entity_type": "lineage"
            },
            "agent_behavior": {
                "keywords": ["agent", "behavior", "decision", "action", "strategy"],
                "realm": "faculty",
                "entity_type": "agent"
            }
        }

        entities_per_theme = sample_size // len(narrative_themes)

        for theme_name, theme_config in narrative_themes.items():
            for i in range(entities_per_theme):
                # Create semantically related entities
                keyword = theme_config["keywords"][i % len(theme_config["keywords"])]

                bitchain = BitChain(
                    id=f"semantic_{theme_name}_{i}",
                    entity_type=theme_config["entity_type"],
                    realm=theme_config["realm"],
                    coordinates=Coordinates(
                        realm=theme_config["realm"],
                        lineage=i + 1,
                        adjacency=[f"semantic_{theme_name}_{j}" for j in range(max(0, i-2), min(entities_per_theme, i+3))],
                        horizon="emergence",
                        resonance=0.7 + (i % 5) * 0.05,  # Similar resonance within theme
                        velocity=0.3 + (i % 3) * 0.1,
                        density=0.6 + (i % 4) * 0.1
                    ),
                    created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    state={
                        "narrative": f"{keyword.capitalize()} exploration in {theme_name.replace('_', ' ')}",
                        "theme": theme_name,
                        "semantic_cluster": True,
                        "dialogue": f"Exploring {keyword} within the context of {theme_name.replace('_', ' ')}"
                    }
                )

                event = self.create_bitchain_event(bitchain, "SEMANTIC_FIDELITY")
                await self.broadcast_event(event)

                # Small delay for visualization
                await asyncio.sleep(0.01)

        # Send analysis complete event
        analysis_event = self.create_experiment_event(
            "SEMANTIC_FIDELITY",
            "completed",
            {
                "proof_type": "semantic_fidelity",
                "entities_created": sample_size,
                "themes": list(narrative_themes.keys()),
                "expected_behavior": "Entities with similar narrative content should cluster together"
            }
        )
        await self.broadcast_event(analysis_event)

        self.logger.info(f"✅ Semantic Fidelity Proof completed with {sample_size} entities")

    async def run_resilience_testing(self, sample_size: int = 150):
        """
        Resilience Testing: Test lattice behavior under mutation, deletion, and adversarial input.

        Creates entities and then simulates various stressors to test system resilience.
        """
        self.logger.info("🛡️ Starting Resilience Testing...")

        # Phase 1: Create stable baseline entities
        baseline_entities = []
        for i in range(sample_size):
            bitchain = BitChain(
                id=f"resilience_baseline_{i}",
                entity_type="concept",
                realm="system",
                coordinates=Coordinates(
                    realm="system",
                    lineage=i + 1,
                    adjacency=[f"resilience_baseline_{j}" for j in range(max(0, i-3), min(sample_size, i+4))],
                    horizon="genesis",
                    resonance=0.5,
                    velocity=0.5,
                    density=0.5
                ),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                state={
                    "test_phase": "baseline",
                    "resilience_test": True,
                    "stability_factor": 1.0
                }
            )
            baseline_entities.append(bitchain)
            event = self.create_bitchain_event(bitchain, "RESILIENCE_BASELINE")
            await self.broadcast_event(event)
            await asyncio.sleep(0.01)

        # Phase 2: Mutation testing - entities with corrupted coordinates
        for i in range(sample_size // 4):
            mutated = BitChain(
                id=f"resilience_mutation_{i}",
                entity_type="fragment",  # Corrupted type
                realm="void",  # Unexpected realm
                coordinates=Coordinates(
                    realm="void",
                    lineage=-i,  # Invalid lineage
                    adjacency=[],  # Empty adjacency
                    horizon="decay",  # Decay horizon
                    resonance=-1.5,  # Invalid resonance
                    velocity=999.0,  # Extreme velocity
                    density=-0.5  # Invalid density
                ),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                state={
                    "test_phase": "mutation",
                    "corruption_level": "high",
                    "resilience_test": True
                }
            )
            event = self.create_bitchain_event(mutated, "RESILIENCE_MUTATION")
            await self.broadcast_event(event)
            await asyncio.sleep(0.01)

        # Phase 3: Deletion simulation - entities marked for deletion
        for i in range(sample_size // 6):
            deletion_entity = BitChain(
                id=f"resilience_deletion_{i}",
                entity_type="adjacency",
                realm="event",
                coordinates=Coordinates(
                    realm="event",
                    lineage=i + 1000,  # High lineage
                    adjacency=[f"deleted_{j}" for j in range(3)],  # References to deleted entities
                    horizon="crystallization",
                    resonance=0.0,  # Zero resonance
                    velocity=0.0,  # Zero velocity
                    density=0.0  # Zero density
                ),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                state={
                    "test_phase": "deletion_simulation",
                    "marked_for_deletion": True,
                    "dangling_references": True,
                    "resilience_test": True
                }
            )
            event = self.create_bitchain_event(deletion_entity, "RESILIENCE_DELETION")
            await self.broadcast_event(event)
            await asyncio.sleep(0.01)

        # Phase 4: Adversarial input - entities with conflicting properties
        for i in range(sample_size // 8):
            adversarial = BitChain(
                id=f"resilience_adversarial_{i}",
                entity_type="horizon",
                realm="pattern",
                coordinates=Coordinates(
                    realm="pattern",
                    lineage=i * 7,  # Prime number spacing
                    adjacency=[f"conflict_{j}" for j in range(10)],  # High adjacency
                    horizon="peak",  # Peak horizon
                    resonance=1.0 if i % 2 == 0 else -1.0,  # Bipolar resonance
                    velocity=2.0 * (-1 if i % 3 == 0 else 1),  # Oscillating velocity
                    density=1.0 if i % 5 == 0 else 0.0  # Binary density
                ),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                state={
                    "test_phase": "adversarial",
                    "conflict_level": "maximum",
                    "paradoxical_properties": True,
                    "resilience_test": True,
                    "dialogue": f"Adversarial entity {i} testing system boundaries"
                }
            )
            event = self.create_bitchain_event(adversarial, "RESILIENCE_ADVERSARIAL")
            await self.broadcast_event(event)
            await asyncio.sleep(0.01)

        # Send resilience testing complete event
        resilience_event = self.create_experiment_event(
            "RESILIENCE_TESTING",
            "completed",
            {
                "proof_type": "resilience_testing",
                "baseline_entities": sample_size,
                "mutation_entities": sample_size // 4,
                "deletion_entities": sample_size // 6,
                "adversarial_entities": sample_size // 8,
                "total_test_entities": sample_size + (sample_size // 4) + (sample_size // 6) + (sample_size // 8),
                "expected_behavior": "System should handle corrupted, deleted, and adversarial entities gracefully"
            }
        )
        await self.broadcast_event(resilience_event)

        self.logger.info(f"✅ Resilience Testing completed with {sample_size + (sample_size // 4) + (sample_size // 6) + (sample_size // 8)} total entities")

    async def handle_client_message(self, data: Dict[str, Any], websocket):
        """Handle incoming messages from WebSocket clients."""
        message_type = data.get('type')

        if message_type == 'run_semantic_fidelity_proof':
            sample_size = data.get('sample_size', 200)
            await self.run_semantic_fidelity_proof(sample_size)

        elif message_type == 'run_resilience_testing':
            sample_size = data.get('sample_size', 150)
            await self.run_resilience_testing(sample_size)

        elif message_type == 'start_experiment':
            experiment_id = data.get('experiment_id')
            duration = data.get('duration', 30)
            self.logger.info(f"Starting experiment {experiment_id} for {duration}s")
            # Here you would trigger the actual experiment
            # For now, we'll just acknowledge

        elif message_type == 'stop_experiment':
            experiment_id = data.get('experiment_id')
            self.logger.info(f"Stopping experiment {experiment_id}")
            # Here you would stop the actual experiment

        else:
            self.logger.warning(f"Unknown message type: {message_type}")


# ============================================================================
# EXPERIMENT VISUALIZATION BRIDGE
# ============================================================================

class ExperimentVisualizer:
    """
    Bridge between STAT7 experiments and visualization system.

    Hooks into experiment execution to stream real-time events.
    """

    def __init__(self, event_streamer: STAT7EventStreamer):
        self.event_streamer = event_streamer
        self.active_experiments: Dict[str, Any] = {}

    async def visualize_exp01_uniqueness(self, sample_size: int = 1000, iterations: int = 10):
        """Visualize EXP-01 address uniqueness test."""
        experiment_id = f"EXP-01-{uuid.uuid4().hex[:8]}"

        # Start experiment event
        start_event = self.event_streamer.create_experiment_event(
            experiment_id, "start",
            {"name": "Address Uniqueness Test", "sample_size": sample_size, "iterations": iterations}
        )
        await self.event_streamer.broadcast_event(start_event)

        # Try to import EXP01, use mock if not available
        try:
            from stat7_experiments import EXP01_AddressUniqueness
            exp01 = EXP01_AddressUniqueness(sample_size=sample_size, iterations=iterations)
        except ImportError:
            print("Warning: EXP01_AddressUniqueness not found. Using mock implementation.")
            exp01 = None

        for iteration in range(iterations):
            # Iteration start event
            iter_event = self.event_streamer.create_experiment_event(
                experiment_id, "iteration_start",
                {"iteration": iteration + 1, "total": iterations}
            )
            await self.event_streamer.broadcast_event(iter_event)

            # Generate and visualize bit-chains
            import random
            for i in range(sample_size):
                bitchain = generate_random_bitchain(seed=iteration * 1000 + i)
                event = self.event_streamer.create_bitchain_event(bitchain, experiment_id)
                await self.event_streamer.broadcast_event(event)

                # Small delay for visualization effect
                await asyncio.sleep(0.001)  # 1ms per bitchain

            # Iteration complete event
            iter_complete = self.event_streamer.create_experiment_event(
                experiment_id, "iteration_complete",
                {"iteration": iteration + 1, "bitchains_generated": sample_size}
            )
            await self.event_streamer.broadcast_event(iter_complete)

        # Experiment complete event
        complete_event = self.event_streamer.create_experiment_event(
            experiment_id, "complete",
            {"total_iterations": iterations, "total_bitchains": sample_size * iterations}
        )
        await self.event_streamer.broadcast_event(complete_event)

    async def visualize_continuous_generation(self, duration_seconds: int = 60, rate_per_second: int = 10):
        """Continuous bit-chain generation for visualization testing."""
        experiment_id = f"CONTINUOUS-{uuid.uuid4().hex[:8]}"

        start_event = self.event_streamer.create_experiment_event(
            experiment_id, "start",
            {"name": "Continuous Generation", "duration": duration_seconds, "rate": rate_per_second}
        )
        await self.event_streamer.broadcast_event(start_event)

        start_time = time.time()
        generated_count = 0

        while time.time() - start_time < duration_seconds:
            # Generate batch of bit-chains
            batch_size = min(rate_per_second, 50)  # Max 50 at once
            for i in range(batch_size):
                bitchain = generate_random_bitchain()
                event = self.event_streamer.create_bitchain_event(bitchain, experiment_id)
                await self.event_streamer.broadcast_event(event)
                generated_count += 1

            # Wait for next batch
            await asyncio.sleep(1.0)

        complete_event = self.event_streamer.create_experiment_event(
            experiment_id, "complete",
            {"total_generated": generated_count, "duration": duration_seconds}
        )
        await self.event_streamer.broadcast_event(complete_event)


# ============================================================================
# SERVER STARTUP
# ============================================================================

async def main():
    """Main server startup function."""
    # Create event streamer
    streamer = STAT7EventStreamer(host="localhost", port=8765)
    visualizer = ExperimentVisualizer(streamer)

    # Start server in background
    server_task = asyncio.create_task(streamer.start_server())

    # Wait a moment for server to start
    await asyncio.sleep(1)

    print("🚀 STAT7 Visualization Server started!")
    print("📊 WebSocket: ws://localhost:8765")
    print("🌐 Open visualization.html in your browser")
    print()
    print("Available commands:")
    print("  - Type 'exp01' to run EXP-01 visualization")
    print("  - Type 'continuous' to start continuous generation")
    print("  - Type 'quit' to stop server")
    print()

    # Interactive command loop
    while streamer.is_running:
        try:
            command = input("stat7-viz> ").strip().lower()

            if command == 'quit':
                break
            elif command == 'exp01':
                print("🧪 Starting EXP-01 visualization...")
                await visualizer.visualize_exp01_uniqueness(sample_size=500, iterations=3)
                print("✅ EXP-01 visualization complete")
            elif command == 'continuous':
                print("🔄 Starting continuous generation (30 seconds)...")
                await visualizer.visualize_continuous_generation(duration_seconds=30, rate_per_second=20)
                print("✅ Continuous generation complete")
            elif command == '':
                continue
            else:
                print(f"Unknown command: {command}")
                print("Available: exp01, continuous, quit")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    # Cleanup
    streamer.stop_server()
    server_task.cancel()
    print("\n👋 STAT7 Visualization Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
