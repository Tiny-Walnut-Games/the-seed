#!/usr/bin/env python3
"""
Simple STAT7 Visualization Runner
Starts both web server and WebSocket server in the correct order
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def start_web_server():
    """Start the web server."""
    web_dir = Path(__file__).parent / "web"
    server_script = web_dir / "server" / "simple_web_server.py"

    print("🌐 Starting web server...")
    process = subprocess.Popen([sys.executable, str(server_script)],
                             cwd=str(web_dir),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True)

    # Wait a moment for server to start
    time.sleep(2)

    # Check if server started successfully
    if process.poll() is None:
        print("✅ Web server started successfully!")
        return process
    else:
        print("❌ Web server failed to start")
        return None

def start_websocket_server():
    """Start the WebSocket server."""
    web_dir = Path(__file__).parent / "web"
    server_script = web_dir / "server" / "stat7wsserve.py"

    print("🔌 Starting WebSocket server...")
    process = subprocess.Popen([sys.executable, str(server_script)],
                             cwd=str(web_dir),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True)

    # Wait a moment for server to start
    time.sleep(2)

    # Check if server started successfully
    if process.poll() is None:
        print("✅ WebSocket server started successfully!")
        return process
    else:
        print("❌ WebSocket server failed to start")
        return None

def main():
    """Main runner function."""
    print("🚀 STAT7 Visualization System")
    print("=" * 50)

    # Start web server
    web_process = start_web_server()
    if not web_process:
        return 1

    # Open browser
    try:
        webbrowser.open("http://localhost:8001/stat7threejs.html")
        print("🌐 Browser opened to visualization")
    except:
        print("⚠️ Could not open browser automatically")
        print("📊 Please open: http://localhost:8001/stat7threejs.html")

    # Start WebSocket server
    ws_process = start_websocket_server()
    if not ws_process:
        web_process.terminate()
        return 1

    print("\n" + "=" * 50)
    print("🎮 STAT7 Visualization System Ready!")
    print("📊 Web interface: http://localhost:8001/stat7threejs.html")
    print("🔌 WebSocket server: ws://localhost:8765")
    print()
    print("📋 Available Commands:")
    print("   - Type 'exp01' to run EXP-01 visualization")
    print("   - Type 'continuous' for continuous generation")
    print("   - Type 'quit' to stop the WebSocket server")
    print("   - Press Ctrl+C here to stop both servers")
    print("=" * 50)

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)

            # Check if servers are still running
            if web_process.poll() is not None:
                print("❌ Web server stopped unexpectedly")
                break

            if ws_process.poll() is not None:
                print("❌ WebSocket server stopped unexpectedly")
                break

    except KeyboardInterrupt:
        print("\n👋 Stopping servers...")

    # Cleanup
    try:
        web_process.terminate()
        ws_process.terminate()
        web_process.wait(timeout=5)
        ws_process.wait(timeout=5)
    except:
        pass

    print("✅ All servers stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())
