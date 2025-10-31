#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test to verify server starts with --subprocess flag."""

import subprocess
import time
import sys
import os

# Force UTF-8 output encoding on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_server_with_flag():
    """Test server startup with --subprocess flag."""
    print("Starting server with --subprocess flag...")
    proc = subprocess.Popen(
        [sys.executable, 'web/server/stat7wsserve.py', '--subprocess'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Collect output for 3 seconds
    time.sleep(3)
    
    # Terminate server
    proc.terminate()
    
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    
    # Read output
    output_lines = []
    try:
        for line in proc.stdout:
            output_lines.append(line.rstrip())
            if len(output_lines) > 100:
                break
    except:
        pass
    
    print("\n=== SERVER OUTPUT (first 80 lines) ===")
    for line in output_lines[:80]:
        print(line)
    
    # Check for key indicators
    output_str = '\n'.join(output_lines)
    
    print("\n=== VERIFICATION ===")
    
    if '--subprocess flag detected' in output_str:
        print("[OK] --subprocess flag was detected by server")
    else:
        print("[WARN] --subprocess flag detection not visible in output")
    
    if 'SUBPROCESS-MODE' in output_str:
        print("[OK] Server entered SUBPROCESS mode")
    else:
        print("[WARN] Server did not show SUBPROCESS-MODE output")
    
    if 'Auto-starting continuous generation' in output_str:
        print("[OK] Auto-starting continuous generation message found")
    else:
        print("[WARN] Auto-starting message not found")
    
    if 'listening on' in output_str or 'WebSocket' in output_str or 'localhost:8765' in output_str:
        print("[OK] WebSocket server initialization successful")
    else:
        print("[ERROR] WebSocket server initialization failed")
    
    return 0 if 'listening' in output_str or 'WebSocket' in output_str else 1

if __name__ == "__main__":
    sys.exit(test_server_with_flag())