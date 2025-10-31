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
import io
from pathlib import Path

# Fix for Windows console encoding (emoji support)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def read_subprocess_output(process, label, timeout=3):
    """
    Read subprocess output without blocking.
    Returns the output collected during the timeout period.
    """
    output = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < timeout and process.poll() is None:
            try:
                # Non-blocking read with small timeout
                line = process.stdout.readline()
                if line:
                    output.append(line.rstrip())
                    print(f"  [{label}] {line.rstrip()}")
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"  Error reading output: {e}")
                break
    except Exception as e:
        print(f"  Error: {e}")
    
    return '\n'.join(output)

def start_web_server():
    """Start the web server."""
    web_dir = Path(__file__).parent.parent  # web/launchers/.. = web/
    server_script = web_dir / "server" / "simple_web_server.py"

    print("[SERVER] Starting web server...")
    process = subprocess.Popen([sys.executable, str(server_script)],
                             cwd=str(web_dir),
                             stdin=subprocess.DEVNULL,  # Redirect stdin to avoid blocking
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True,
                             encoding='utf-8',  # Explicit UTF-8 encoding
                             errors='replace',   # Replace undecodable bytes
                             bufsize=1)  # Line buffered

    # Read startup output
    output = read_subprocess_output(process, "WEB", timeout=2)

    # Check if server started successfully
    if process.poll() is None:
        print("[OK] Web server started successfully!")
        return process
    else:
        print("[ERROR] Web server failed to start")
        if output:
            print(f"  Output: {output}")
        return None

def start_websocket_server():
    """Start the WebSocket server."""
    web_dir = Path(__file__).parent.parent  # web/launchers/.. = web/
    server_script = web_dir / "server" / "stat7wsserve.py"

    print("[WEBSOCKET] Starting WebSocket server...")
    process = subprocess.Popen([sys.executable, str(server_script), "--subprocess"],
                             cwd=str(web_dir),
                             stdin=subprocess.DEVNULL,  # CRITICAL: Redirect stdin so server detects subprocess mode
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True,
                             encoding='utf-8',  # Explicit UTF-8 encoding
                             errors='replace',   # Replace undecodable bytes
                             bufsize=1)  # Line buffered

    # Read startup output
    output = read_subprocess_output(process, "WEBSOCKET", timeout=3)

    # Check if server started successfully
    if process.poll() is None:
        print("[OK] WebSocket server started successfully!")
        return process
    else:
        print("[ERROR] WebSocket server failed to start")
        if output:
            print(f"  Output:\n{output}")
        return None

def main():
    """Main runner function."""
    print("[STARTUP] STAT7 Visualization System")
    print("=" * 50)

    # Start web server
    web_process = start_web_server()
    if not web_process:
        return 1

    # Open browser
    try:
        webbrowser.open("http://localhost:8001/stat7threejs.html")
        print("[BROWSER] Browser opened to visualization")
    except:
        print("[WARN] Could not open browser automatically")
        print("[URL] Please open: http://localhost:8001/stat7threejs.html")

    # Start WebSocket server
    ws_process = start_websocket_server()
    if not ws_process:
        web_process.terminate()
        return 1

    print("\n" + "=" * 50)
    print("[READY] STAT7 Visualization System Ready!")
    print("[URL] Web interface: http://localhost:8001/stat7threejs.html")
    print("[WEBSOCKET] WebSocket server: ws://localhost:8765")
    print()
    print("[COMMANDS] Available Commands:")
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
                print("[ERROR] Web server stopped unexpectedly")
                break

            if ws_process.poll() is not None:
                print("[ERROR] WebSocket server stopped unexpectedly")
                break

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping servers...")

    # Cleanup
    try:
        web_process.terminate()
        ws_process.terminate()
        web_process.wait(timeout=5)
        ws_process.wait(timeout=5)
    except:
        pass

    print("[OK] All servers stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())
