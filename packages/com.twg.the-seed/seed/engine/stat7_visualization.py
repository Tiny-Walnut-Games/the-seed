"""
STAT7 Visualization Integration

Integrates STAT7 experiments with the WebSocket visualization system.
Provides easy-to-use functions for connecting experiments to real-time visualization.

Usage:
    from stat7_visualization import visualize_experiment

    # Visualize EXP-01
    await visualize_experiment("EXP-01", sample_size=1000, iterations=5)

    # Visualize custom bit-chain generation
    await visualize_continuous_generation(duration_seconds=30)
"""

import asyncio
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path

from stat7_experiments import (
    BitChain, generate_random_bitchain,
    EXP01_AddressUniqueness, EXP02_RetrievalEfficiency, EXP03_DimensionNecessity
)

# Import the visualization components
try:
    from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
except ImportError:
    print("Warning: stat7wsserve not found. Visualization features disabled.")
    STAT7EventStreamer = None
    ExperimentVisualizer = None


class STAT7VisualizationManager:
    """
    High-level manager for STAT7 visualization.

    Handles WebSocket server startup, experiment integration, and cleanup.
    """

    def __init__(self, host: str = "localhost", port: int = 8765, auto_start: bool = True):
        self.host = host
        self.port = port
        self.event_streamer: Optional[STAT7EventStreamer] = None
        self.visualizer: Optional[ExperimentVisualizer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False

        if STAT7EventStreamer is None:
            raise ImportError("stat7wsserve module not available. Install required dependencies.")

        if auto_start:
            self.start_server()

    def start_server(self):
        """Start the WebSocket visualization server in a background thread."""
        if self.is_running:
            return

        self.event_streamer = STAT7EventStreamer(host=self.host, port=self.port)
        self.visualizer = ExperimentVisualizer(self.event_streamer)

        # Start server in background thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        # Wait for server to start
        time.sleep(2)
        self.is_running = True

        print(f"🚀 STAT7 Visualization Server started on ws://{self.host}:{self.port}")
        print(f"🌐 Open stat7threejs.html in your browser to view visualization")

    def _run_server(self):
        """Run the WebSocket server in asyncio event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.event_streamer.start_server())
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            loop.close()

    def stop_server(self):
        """Stop the WebSocket server."""
        if self.event_streamer:
            self.event_streamer.stop_server()
        self.is_running = False
        print("👋 STAT7 Visualization Server stopped")

    async def visualize_exp01(self, sample_size: int = 1000, iterations: int = 10):
        """Visualize EXP-01 address uniqueness test."""
        if not self.visualizer:
            raise RuntimeError("Visualization server not started")

        await self.visualizer.visualize_exp01_uniqueness(sample_size, iterations)

    async def visualize_continuous_generation(self, duration_seconds: int = 60, rate_per_second: int = 10):
        """Visualize continuous bit-chain generation."""
        if not self.visualizer:
            raise RuntimeError("Visualization server not started")

        await self.visualizer.visualize_continuous_generation(duration_seconds, rate_per_second)

    async def visualize_bitchain_batch(self, bitchains: list, experiment_id: str = "custom"):
        """Visualize a batch of existing bit-chains."""
        if not self.event_streamer:
            raise RuntimeError("Visualization server not started")

        for bitchain in bitchains:
            event = self.event_streamer.create_bitchain_event(bitchain, experiment_id)
            await self.event_streamer.broadcast_event(event)
            await asyncio.sleep(0.01)  # Small delay for visualization effect


# Global visualization manager instance
_viz_manager: Optional[STAT7VisualizationManager] = None


def get_visualization_manager() -> STAT7VisualizationManager:
    """Get or create the global visualization manager."""
    global _viz_manager
    if _viz_manager is None:
        _viz_manager = STAT7VisualizationManager()
    return _viz_manager


async def visualize_experiment(experiment_name: str, **kwargs) -> Dict[str, Any]:
    """
    High-level function to visualize STAT7 experiments.

    Args:
        experiment_name: Name of experiment ("EXP-01", "EXP-02", "EXP-03", "continuous")
        **kwargs: Experiment-specific parameters

    Returns:
        Dictionary with experiment results and visualization info
    """
    manager = get_visualization_manager()

    print(f"🧪 Starting visualization for {experiment_name}")

    if experiment_name == "EXP-01":
        sample_size = kwargs.get('sample_size', 1000)
        iterations = kwargs.get('iterations', 10)
        await manager.visualize_exp01(sample_size, iterations)

        # Run actual experiment for results
        exp01 = EXP01_AddressUniqueness(sample_size=sample_size, iterations=iterations)
        results, success = exp01.run()

        return {
            'experiment': experiment_name,
            'success': success,
            'results': results,
            'visualization': 'completed'
        }

    elif experiment_name == "continuous":
        duration = kwargs.get('duration_seconds', 60)
        rate = kwargs.get('rate_per_second', 10)
        await manager.visualize_continuous_generation(duration, rate)

        return {
            'experiment': experiment_name,
            'duration_seconds': duration,
            'rate_per_second': rate,
            'visualization': 'completed'
        }

    else:
        raise ValueError(f"Unknown experiment: {experiment_name}")


def create_jupyter_widget(width: str = "100%", height: str = "600px") -> str:
    """
    Create HTML widget for embedding STAT7 visualization in Jupyter notebooks.

    Args:
        width: Widget width (CSS value)
        height: Widget height (CSS value)

    Returns:
        HTML string for Jupyter notebook display
    """
    # Read the visualization HTML
    html_path = Path(__file__).parent.parent.parent / "stat7threejs.html"

    if not html_path.exists():
        # Fallback to inline HTML
        return create_inline_jupyter_widget(width, height)

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Wrap in iframe for Jupyter
    widget_html = f"""
    <div style="width: {width}; height: {height}; border: 1px solid #333; border-radius: 8px; overflow: hidden;">
        <iframe src="file://{html_path.absolute()}"
                width="100%"
                height="100%"
                frameborder="0"
                style="background: #0a0a0a;">
        </iframe>
    </div>
    """

    return widget_html


def create_inline_jupyter_widget(width: str = "100%", height: str = "600px") -> str:
    """
    Create inline HTML widget for Jupyter (fallback when external file not available).

    Args:
        width: Widget width (CSS value)
        height: Widget height (CSS value)

    Returns:
        HTML string for Jupyter notebook display
    """
    return f"""
    <div style="width: {width}; height: {height}; border: 1px solid #333; border-radius: 8px; background: #0a0a0a; color: white; padding: 20px; text-align: center; font-family: monospace;">
        <h3>🔌 STAT7 Visualization</h3>
        <p>WebSocket Status: <span id="ws-status">Connecting...</span></p>
        <p>Points Rendered: <span id="point-count">0</span></p>
        <p>FPS: <span id="fps">0</span></p>

        <script>
        // Simple WebSocket connection for Jupyter
        const ws = new WebSocket('ws://localhost:8765');
        const statusEl = document.getElementById('ws-status');
        const pointEl = document.getElementById('point-count');
        const fpsEl = document.getElementById('fps');

        let pointCount = 0;
        let lastFrameTime = performance.now();
        let frameCount = 0;

        ws.onopen = () => {{
            statusEl.textContent = 'Connected';
            statusEl.style.color = '#2ecc71';
        }};

        ws.onclose = () => {{
            statusEl.textContent = 'Disconnected';
            statusEl.style.color = '#e74c3c';
        }};

        ws.onmessage = (event) => {{
            const data = JSON.parse(event.data);
            if (data.event_type === 'bitchain_created') {{
                pointCount++;
                pointEl.textContent = pointCount;
            }}
        }};

        // Simple FPS counter
        function updateFPS() {{
            frameCount++;
            const currentTime = performance.now();
            const deltaTime = currentTime - lastFrameTime;

            if (deltaTime >= 1000) {{
                fpsEl.textContent = Math.round(frameCount * 1000 / deltaTime);
                frameCount = 0;
                lastFrameTime = currentTime;
            }}

            requestAnimationFrame(updateFPS);
        }}

        updateFPS();
        </script>
    </div>
    """


# Jupyter notebook display helper
def display_in_jupyter(width: str = "100%", height: str = "600px"):
    """
    Display STAT7 visualization in Jupyter notebook.

    Usage in Jupyter:
        from stat7_visualization import display_in_jupyter, visualize_experiment

        # Display visualization widget
        display_in_jupyter()

        # Run visualization
        await visualize_experiment("EXP-01", sample_size=500, iterations=3)
    """
    try:
        from IPython.display import HTML, display
        widget_html = create_jupyter_widget(width, height)
        display(HTML(widget_html))
    except ImportError:
        print("IPython not available. Cannot display in Jupyter notebook.")
        print(f"Open stat7threejs.html in your browser instead.")


# Convenience functions for quick start
def quick_start_visualization():
    """Quick start visualization with default settings."""
    manager = get_visualization_manager()
    print("🚀 STAT7 Visualization started!")
    print("📊 Open stat7threejs.html in your browser")
    print("🧪 Use visualize_experiment() to run experiments")
    return manager


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = quick_start_visualization()

        print("\nRunning example visualizations...")

        # Visualize EXP-01
        await manager.visualize_exp01(sample_size=100, iterations=2)

        # Continuous generation
        await manager.visualize_continuous_generation(duration_seconds=10, rate_per_second=5)

        print("\n✅ Example visualizations complete!")
        print("Keep the server running and refresh your browser to see the results.")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            manager.stop_server()

    asyncio.run(main())
