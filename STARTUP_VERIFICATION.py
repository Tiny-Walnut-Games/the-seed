#!/usr/bin/env python3
"""
Complete STAT7 Startup Verification
Tests the full customer journey from launcher to running servers
"""

import subprocess
import sys
import time
from pathlib import Path

print("=" * 70)
print("[OK] COMPLETE STARTUP VERIFICATION")
print("=" * 70)

# Test 1: Launcher script exists
print("\n[TEST 1] Checking launcher script...")
launcher = Path("web/launchers/run_stat7_visualization.py")
if launcher.exists():
    print(f"  [OK] Launcher found: {launcher}")
else:
    print(f"  [ERROR] Launcher not found: {launcher}")
    sys.exit(1)

# Test 2: Required server files exist
print("\n[TEST 2] Checking required server files...")
required_files = [
    "web/server/stat7wsserve.py",
    "web/server/simple_web_server.py",
    "web/stat7threejs.html"
]
for f in required_files:
    path = Path(f)
    if path.exists():
        print(f"  [OK] {f}")
    else:
        print(f"  [ERROR] {f}")
        sys.exit(1)

# Test 3: Start the launcher and capture output
print("\n[TEST 3] Starting launcher (10 second capture window)...")
print("-" * 70)

try:
    process = subprocess.Popen(
        [sys.executable, str(launcher)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )
    
    start_time = time.time()
    output_lines = []
    web_ok = False
    ws_ok = False
    browser_ok = False
    errors = []
    
    # Capture output for 10 seconds
    while time.time() - start_time < 10:
        try:
            line = process.stdout.readline()
            if line:
                output_lines.append(line.rstrip())
                print(line.rstrip())
                
                # Check for success indicators
                if "[OK] Web server started" in line:
                    web_ok = True
                if "[OK] WebSocket server started" in line:
                    ws_ok = True
                if "Browser opened" in line or "Please open:" in line:
                    browser_ok = True
                
                # Check for failures
                if "[ERROR]" in line:
                    errors.append(line.rstrip())
            else:
                time.sleep(0.05)
        except Exception as e:
            time.sleep(0.05)
    
    print("-" * 70)
    
    # Terminate gracefully
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
    
    # Results
    print("\n" + "=" * 70)
    print("[RESULTS] VERIFICATION RESULTS")
    print("=" * 70)
    
    print("\nServer Status:")
    if web_ok:
        print("  [OK] Web Server: Started successfully")
    else:
        print("  [ERROR] Web Server: Not confirmed")
    
    if ws_ok:
        print("  [OK] WebSocket Server: Started successfully")
    else:
        print("  [ERROR] WebSocket Server: Not confirmed")
    
    if browser_ok:
        print("  [INFO] Browser: Opened (or tried to open)")
    else:
        print("  [INFO] Browser: Not opened")
    
    if errors:
        print(f"\nErrors Detected ({len(errors)}):")
        for err in errors[:5]:
            print(f"  [WARN] {err}")
    else:
        print("\n[OK] No errors detected!")
    
    # Final verdict
    print("\n" + "-" * 70)
    if web_ok and ws_ok:
        print("[OK] STARTUP SUCCESSFUL!")
        print("\nThe STAT7 visualization system is ready.")
        print("Web: http://localhost:8001/stat7threejs.html")
        print("WebSocket: ws://localhost:8765")
        sys.exit(0)
    else:
        print("[ERROR] STARTUP INCOMPLETE")
        if not web_ok:
            print("  - Web server failed to start")
        if not ws_ok:
            print("  - WebSocket server failed to start")
        sys.exit(1)

except KeyboardInterrupt:
    print("\n\n⏹️  Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)