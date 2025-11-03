#!/usr/bin/env python3
"""
Quick diagnostic script to test the visualization pipeline
"""

import subprocess
import time
import sys
import os

print("=" * 60)
print("STAT7 Visualization Debug")
print("=" * 60)

# Start the auto-launch script
print("\n[1/3] Starting auto-launcher...")
proc = subprocess.Popen(
    [sys.executable, "web/launchers/full_auto_launch.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd="E:/Tiny_Walnut_Games/the-seed"
)

# Give it time to start and output messages
print("\nWaiting for servers to start...\n")
time.sleep(8)

# Read output
print("[2/3] Server output:")
print("-" * 60)
try:
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
        if "Opening browser" in line or "SIMULATION IS LIVE" in line:
            break
except Exception as e:
    print(f"Error reading output: {e}")

print("-" * 60)
print("\n[3/3] System should now be running:")
print("  - WebSocket: ws://localhost:8765")
print("  - HTTP: http://localhost:8000/stat7threejs.html")
print("\nOpen that URL and check browser console (F12) for:")
print("  1. Any JavaScript errors")
print("  2. WebSocket connection status")
print("  3. Message flow from server")
print("\nPress Ctrl+C to stop the debug script (servers will continue)")

try:
    proc.wait()
except KeyboardInterrupt:
    print("\n\nShutting down...")
    proc.terminate()
    time.sleep(2)
    proc.kill()