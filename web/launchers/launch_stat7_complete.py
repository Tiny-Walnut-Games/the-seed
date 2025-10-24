#!/usr/bin/env python3
"""
Complete STAT7 Visualization System Launcher
Handles all setup, error checking, and launches both servers
"""

import os
import sys
import time
import threading
import webbrowser
import subprocess
import asyncio
from pathlib import Path
import signal

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking system requirements...")

    # Change to web directory first
    web_dir = os.path.dirname(os.path.dirname(__file__))
    original_dir = os.getcwd()
    os.chdir(web_dir)

    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False

        # Check required packages
        try:
            import websockets
            print("✅ websockets package found")
        except ImportError:
            print("❌ websockets package missing")
            print("   Run: pip install websockets")
            return False

        # Check required files
        required_files = [
            "server/stat7wsserve.py",
            "stat7threejs.html",
            "js/stat7-core.js",
            "js/stat7-websocket.js",
            "js/stat7-ui.js",
            "js/stat7-main.js"
        ]

        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Missing file: {file}")
                return False

        print("✅ All requirements met")
        return True

    finally:
        # Change back to original directory
        os.chdir(original_dir)

def find_free_port(start_port=8000):
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def start_web_server():
    """Start the web server in background."""
    import subprocess

    # Change to web directory
    web_dir = os.path.dirname(os.path.dirname(__file__))
    os.chdir(web_dir)

    port = find_free_port(8000)
    if not port:
        print("❌ Could not find free port for web server")
        return None

    print(f"🌐 Starting web server on port {port}...")

    # Use simple_web_server.py if it exists, otherwise use built-in approach
    if os.path.exists("server/simple_web_server.py"):
        web_process = subprocess.Popen([
            sys.executable, "server/simple_web_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        # Fallback: use Python's built-in server
        web_process = subprocess.Popen([
            sys.executable, "-m", "http.server", str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait a moment to check if server started
    time.sleep(2)
    if web_process.poll() is not None:
        print("❌ Web server failed to start")
        return None

    url = f"http://localhost:{port}/stat7threejs.html"
    print(f"✅ Web server running at: {url}")

    # Try to open browser
    try:
        webbrowser.open(url)
        print("🌐 Browser opened automatically")
    except:
        print("⚠️ Could not open browser automatically")
        print(f"📊 Please open: {url}")

    return web_process, url

async def start_websocket_server():
    """Start the WebSocket server."""
    try:
        # Import the server components
        web_dir = os.path.dirname(os.path.dirname(__file__))
        server_dir = os.path.join(web_dir, 'server')
        sys.path.insert(0, server_dir)
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer

        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)

        print("🔌 Starting WebSocket server on port 8765...")

        # Start server in background task
        server_task = asyncio.create_task(streamer.start_server())

        # Wait for server to start
        await asyncio.sleep(1)

        print("✅ WebSocket server started successfully!")
        print("=" * 60)
        print("🎮 STAT7 Visualization System Ready!")
        print("📊 Web interface should be open in your browser")
        print("🔌 WebSocket server running")
        print()
        print("Available commands:")
        print("  exp01      - Run EXP-01 Address Uniqueness Test")
        print("  continuous - Run continuous bit-chain generation")
        print("  semantic   - Run semantic fidelity proof")
        print("  resilience - Run resilience testing")
        print("  quit       - Stop the system")
        print("=" * 60)

        # Interactive command loop
        while streamer.is_running:
            try:
                command = input("\nstat7> ").strip().lower()

                if command == 'quit' or command == 'exit':
                    break
                elif command == 'exp01':
                    print("🧪 Running EXP-01 Address Uniqueness Test...")
                    await visualizer.visualize_exp01_uniqueness(sample_size=300, iterations=3)
                    print("✅ EXP-01 completed")
                elif command == 'continuous':
                    print("🔄 Running continuous generation (30 seconds)...")
                    await visualizer.visualize_continuous_generation(duration_seconds=30, rate_per_second=15)
                    print("✅ Continuous generation completed")
                elif command == 'semantic':
                    print("🧠 Running semantic fidelity proof...")
                    await streamer.run_semantic_fidelity_proof(sample_size=150)
                    print("✅ Semantic fidelity proof completed")
                elif command == 'resilience':
                    print("🛡️ Running resilience testing...")
                    await streamer.run_resilience_testing(sample_size=100)
                    print("✅ Resilience testing completed")
                elif command in ['help', '?']:
                    print("\nAvailable commands:")
                    print("  exp01      - Run EXP-01 Address Uniqueness Test")
                    print("  continuous - Run continuous bit-chain generation")
                    print("  semantic   - Run semantic fidelity proof")
                    print("  resilience - Run resilience testing")
                    print("  quit       - Stop the system")
                elif command == '':
                    continue
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error executing command: {e}")

        # Cleanup
        print("\n🛑 Shutting down WebSocket server...")
        streamer.stop_server()
        server_task.cancel()

    except ImportError as e:
        print(f"❌ Error importing server components: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting WebSocket server: {e}")
        return False

    return True

def main():
    """Main launcher function."""
    print("🚀 STAT7 Complete Visualization System Launcher")
    print("=" * 60)

    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        input("Press Enter to exit...")
        return

    # Start web server
    web_result = start_web_server()
    if not web_result:
        print("\n❌ Failed to start web server")
        input("Press Enter to exit...")
        return

    web_process, web_url = web_result

    try:
        print(f"\n🌐 Web server running at: {web_url}")
        print("🔄 Starting WebSocket server...")

        # Start WebSocket server
        success = asyncio.run(start_websocket_server())

        if not success:
            print("\n❌ WebSocket server failed")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup web server
        if web_process:
            print("🛑 Stopping web server...")
            web_process.terminate()
            try:
                web_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                web_process.kill()

        print("👋 STAT7 Visualization System stopped")

if __name__ == "__main__":
    main()
