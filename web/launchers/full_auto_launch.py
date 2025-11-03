#!/usr/bin/env python3
"""
STAT7 Full Auto-Launch
Starts everything and immediately begins continuous visualization.
No manual input required.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("[STAT7] Auto-Launch Sequence")
    print("=" * 60)
    
    # Get paths
    repo_root = Path(__file__).parent.parent.parent
    web_dir = repo_root / "web"
    server_dir = web_dir / "server"
    
    print(f"\n[INFO] Repo root: {repo_root}")
    print(f"[INFO] Web server dir: {server_dir}")
    
    # Start WebSocket server with auto-start flag
    print("\n[STAT7] Starting WebSocket server with auto-start...")
    ws_process = subprocess.Popen(
        [sys.executable, str(server_dir / "stat7wsserve.py"), "--continuous"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(repo_root)
    )
    
    # Give it a moment to start and begin generation
    time.sleep(3)
    print("[OK] WebSocket server started (generating data stream)")
    
    # Start web server
    print("\n[STAT7] Starting web server...")
    web_process = subprocess.Popen(
        [sys.executable, str(server_dir / "simple_web_server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(web_dir)
    )
    
    time.sleep(2)
    print("[OK] Web server started on port 8000")
    
    # Open browser to visualization
    print("\n[STAT7] Opening browser to visualization...")
    url = "http://localhost:8000/stat7threejs.html"
    webbrowser.open(url)
    time.sleep(1)
    print(f"[OK] Browser opened to: {url}")
    
    print("\n" + "=" * 60)
    print("[STAT7] SIMULATION IS LIVE!")
    print("=" * 60)
    print("\n[INFO] Available Dashboards:")
    print(f"  * Public/3D Visualization: http://localhost:8000/stat7threejs.html")
    print(f"  * Admin Dashboard: http://localhost:8000/phase6c_dashboard.html")
    print(f"  * Entity Viewer: http://localhost:8000/admin-entity-viewer.html")
    print(f"  * WebSocket API: ws://localhost:8765")
    print("\n[INFO] The 3D multiverse visualization should now appear in your browser.")
    print("   It streams real-time STAT7 events from the Python backend.")
    print("   (If blank, check that FPS counter shows activity in the HUD)")
    print("\n[INFO] Keyboard Controls:")
    print("   * H = Toggle HUD")
    print("   * P = Pause/Resume")
    print("   * WASD/Mouse Drag = Navigate 3D space")
    print("\n[INFO] Press Ctrl+C in this terminal to stop all servers")
    print("=" * 60)
    
    try:
        # Keep processes alive
        while True:
            time.sleep(1)
            if ws_process.poll() is not None:
                print("[WARN] WebSocket server stopped unexpectedly")
                break
            if web_process.poll() is not None:
                print("[WARN] Web server stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n[STAT7] Shutdown sequence initiated...")
        ws_process.terminate()
        web_process.terminate()
        
        # Wait for graceful shutdown
        try:
            ws_process.wait(timeout=3)
            web_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print("  [INFO] Force killing processes...")
            ws_process.kill()
            web_process.kill()
        
        print("[OK] All servers stopped")
        print("=" * 60)

if __name__ == "__main__":
    main()