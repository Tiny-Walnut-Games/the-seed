#!/usr/bin/env python3
"""
WebSocket Server Diagnostic
Attempts to start WebSocket server and capture all errors
"""

import subprocess
import sys
import time
import os
from pathlib import Path

print("=" * 70)
print("🔍 WEBSOCKET SERVER DIAGNOSTIC")
print("=" * 70)

# Navigate to web directory
web_dir = Path(__file__).parent / "web"
server_script = web_dir / "server" / "stat7wsserve.py"

print(f"\n[1] Checking WebSocket server file...")
if not server_script.exists():
    print(f"❌ WebSocket server not found at {server_script}")
    sys.exit(1)
print(f"✅ WebSocket server found: {server_script}")

print(f"\n[2] Starting WebSocket server with full output capture...")
print("-" * 70)

try:
    # Start the WebSocket server with all output visible
    process = subprocess.Popen(
        [sys.executable, str(server_script)],
        cwd=str(web_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',  # Replace undecodable bytes with replacement char
        bufsize=1,
        universal_newlines=True
    )
    
    # Capture output for 5 seconds
    start_time = time.time()
    all_output = []
    errors_found = []
    
    while time.time() - start_time < 5:
        try:
            line = process.stdout.readline()
            if line:
                all_output.append(line.rstrip())
                print(line.rstrip())
                
                # Capture errors
                if "Error" in line or "error" in line or "Traceback" in line or "Exception" in line:
                    errors_found.append(line.rstrip())
            else:
                time.sleep(0.1)
        except Exception as e:
            print(f"ERROR reading output: {e}")
            break
    
    print("-" * 70)
    
    # Check process status
    exit_code = process.poll()
    
    if exit_code is None:
        print("\n✅ WebSocket server is RUNNING")
        print("   (Process still active after 5 seconds)")
    else:
        print(f"\n❌ WebSocket server EXITED with code {exit_code}")
    
    # Display errors if found
    if errors_found:
        print(f"\n⚠️  ERRORS DETECTED ({len(errors_found)}):")
        for i, error in enumerate(errors_found[:10], 1):
            print(f"   {i}. {error}")
    else:
        print("\n✅ No obvious errors in output")
    
    # Display full output for analysis
    print(f"\n📋 FULL OUTPUT ({len(all_output)} lines):")
    print("-" * 70)
    for line in all_output[:50]:  # Show first 50 lines
        print(line)
    if len(all_output) > 50:
        print(f"   ... ({len(all_output) - 50} more lines)")
    
    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=2)
    except:
        process.kill()
    
except Exception as e:
    print(f"❌ Error starting WebSocket server: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)