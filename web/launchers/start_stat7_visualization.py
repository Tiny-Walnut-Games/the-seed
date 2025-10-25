#!/usr/bin/env python3
"""
STAT7 Visualization Launcher

Simple launcher that starts both the WebSocket server and a web server
to serve the HTML visualization page properly.
"""

import asyncio
import websockets
import threading
import time
import os
import sys
from pathlib import Path
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Add the seed engine to Python path
seed_path = os.path.join(os.path.dirname(__file__), 'Packages', 'com.twg.the-seed', 'seed', 'engine')
if seed_path not in sys.path:
    sys.path.insert(0, seed_path)

try:
    from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
except ImportError:
    print("Error: stat7wsserve.py not found. Make sure it's in the same directory.")
    sys.exit(1)


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve files with proper MIME types."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def end_headers(self):
        # Add CORS headers to allow WebSocket connections
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Redirect root to the visualization HTML
        if self.path == '/':
            self.path = '/stat7threejs.html'
        return super().do_GET()


def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_web_server(port=8000):
    """Start a simple HTTP server to serve the HTML file."""
    # Find an available port
    available_port = find_available_port(port)
    if available_port is None:
        print(f"❌ No available ports found in range {port}-{port + 10}")
        return None

    try:
        httpd = socketserver.TCPServer(("", available_port), CustomHTTPRequestHandler)
        print(f"🌐 Web server started at http://localhost:{available_port}")
        print(f"📊 Open http://localhost:{available_port}/stat7threejs.html in your browser")
        return available_port, httpd
    except OSError as e:
        print(f"❌ Error starting web server: {e}")
        return None


async def start_websocket_server(host="localhost", port=8765):
    """Start the WebSocket server for STAT7 events."""
    try:
        # Import here to avoid circular imports
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer

        streamer = STAT7EventStreamer(host=host, port=port)
        visualizer = ExperimentVisualizer(streamer)

        print(f"🔌 WebSocket server started at ws://{host}:{port}")

        # Start server in background
        server_task = asyncio.create_task(streamer.start_server())

        # Wait a moment for server to start
        await asyncio.sleep(1)

        return streamer, visualizer, server_task

    except Exception as e:
        print(f"❌ Error starting WebSocket server: {e}")
        return None, None, None


async def main():
    """Main launcher function."""
    print("🚀 Starting STAT7 Visualization System...")
    print("=" * 50)

    # Start WebSocket server
    streamer, visualizer, server_task = await start_websocket_server()
    if streamer is None:
        print("❌ Failed to start WebSocket server. Exiting.")
        return

    # Start web server and get the actual port
    web_server_result = start_web_server()
    if web_server_result is None:
        print("❌ Failed to start web server. Exiting.")
        if streamer:
            streamer.stop_server()
        return

    web_port, httpd = web_server_result

    # Start web server in a separate thread
    web_server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    web_server_thread.start()

    # Wait a moment for web server to start
    time.sleep(2)

    # Try to open the browser automatically
    visualization_url = f'http://localhost:{web_port}/stat7threejs.html'
    try:
        webbrowser.open(visualization_url)
        print("🌐 Opening visualization in your default browser...")
    except:
        print("⚠️ Could not open browser automatically.")
        print(f"📊 Please open {visualization_url} manually")

    print("\n" + "=" * 50)
    print("🎮 STAT7 Visualization is ready!")
    print(f"📊 Visualization: {visualization_url}")
    print("🔌 WebSocket: ws://localhost:8765")
    print("\nAvailable commands:")
    print("  - Type 'exp01' to run EXP-01 visualization")
    print("  - Type 'continuous' to start continuous generation")
    print("  - Type 'quit' to stop servers")
    print("=" * 50)

    # Interactive command loop
    try:
        while True:
            command = input("\nstat7-viz> ").strip().lower()

            if command == 'quit':
                break
            elif command == 'exp01':
                print("🧪 Starting EXP-01 visualization...")
                try:
                    await visualizer.visualize_exp01_uniqueness(sample_size=200, iterations=2)
                    print("✅ EXP-01 visualization complete")
                except Exception as e:
                    print(f"❌ Error running EXP-01: {e}")
            elif command == 'continuous':
                print("🔄 Starting continuous generation (15 seconds)...")
                try:
                    await visualizer.visualize_continuous_generation(duration_seconds=15, rate_per_second=10)
                    print("✅ Continuous generation complete")
                except Exception as e:
                    print(f"❌ Error running continuous generation: {e}")
            elif command == '':
                continue
            else:
                print(f"Unknown command: {command}")
                print("Available: exp01, continuous, quit")

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

    # Cleanup
    print("\n🛑 Shutting down servers...")
    if streamer:
        streamer.stop_server()
    if server_task:
        server_task.cancel()
    if 'httpd' in locals():
        httpd.shutdown()
        httpd.server_close()

    print("👋 STAT7 Visualization System stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
