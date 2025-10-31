#!/usr/bin/env python3
"""
Customer Experience Test - Startup Validation
Tests the complete startup flow and captures all output
"""

import subprocess
import time
import sys
import threading
import io

# Fix encoding first
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 70)
print("[TEST] CUSTOMER EXPERIENCE TEST - Startup Flow")
print("=" * 70)

# Test 1: Check imports
print("\n[TEST 1] Checking Python imports...")
try:
    import websockets
    print(f"  [OK] websockets {websockets.__version__}")
except Exception as e:
    print(f"  [ERROR] websockets: {e}")
    sys.exit(1)

try:
    from pathlib import Path
    print("  [OK] pathlib.Path")
except Exception as e:
    print(f"  [ERROR] pathlib.Path: {e}")
    sys.exit(1)

# Test 2: Check file structure
print("\n[TEST 2] Checking file structure...")
required_files = [
    'web/server/stat7wsserve.py',
    'web/server/simple_web_server.py',
    'web/stat7threejs.html',
    'web/launchers/run_stat7_visualization.py',
    'start_stat7.py',
]

all_exist = True
for f in required_files:
    exists = Path(f).exists()
    symbol = "[OK]" if exists else "[ERROR]"
    print(f"  {symbol} {f}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n[ERROR] Missing required files!")
    sys.exit(1)

# Test 3: Try to run the startup script for 8 seconds
print("\n[TEST 3] Starting STAT7 visualization (8 second timeout)...")
print("  Output from startup script:")
print("  " + "-" * 66)

try:
    process = subprocess.Popen(
        [sys.executable, 'web/launchers/run_stat7_visualization.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',  # Replace undecodable bytes
        bufsize=1
    )
    
    # Run for 8 seconds and capture output
    start_time = time.time()
    output_lines = []
    web_ok = False
    ws_ok = False
    errors = []
    
    while time.time() - start_time < 8:
        try:
            line = process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            output_lines.append(line.rstrip())
            print(f"  {line.rstrip()}")
            
            # Check for success indicators
            if "[OK] Web server started" in line:
                web_ok = True
            if "[OK] WebSocket server started" in line:
                ws_ok = True
            
            # Check for error indicators
            if "[ERROR]" in line or "Error" in line or "error" in line or "Traceback" in line:
                errors.append(line.rstrip())
        except Exception as e:
            time.sleep(0.1)
    
    # Kill the process
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
    
    print("  " + "-" * 66)
    
    # Analyze output
    output_text = "\n".join(output_lines)
    
    print("\n  Analysis:")
    if web_ok:
        print("  [OK] Web server started successfully")
    elif "web server" in output_text.lower():
        print("  [WARN] Web server output detected but status unclear")
    else:
        print("  [ERROR] No web server startup confirmation")
    
    if ws_ok:
        print("  [OK] WebSocket server started successfully")
    elif "websocket" in output_text.lower():
        print("  [WARN] WebSocket output detected but status unclear")
    else:
        print("  [ERROR] No WebSocket server startup confirmation")
    
    if errors:
        print("\n  [WARN] Errors detected:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"    - {error}")

except subprocess.TimeoutExpired:
    print("  [WARN] Process did not terminate gracefully")
    try:
        process.kill()
    except:
        pass
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

# Test 4: Summary
print("\n" + "=" * 70)
print("[RESULTS] TEST SUMMARY")
print("=" * 70)
print("\n[OK] Customer journey test completed!")
print("\nNext step: Open browser to http://localhost:8001/stat7threejs.html")
print("           or http://localhost:8000/stat7threejs.html (if 8001 not available)")
print("\n" + "=" * 70)