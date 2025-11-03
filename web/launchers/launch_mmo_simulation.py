#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launch the actual MMO Simulation.

This starts:
1. MMO Orchestrator with FastAPI (HTTP REST API + WebSocket)
   - Game registry and multi-game tick synchronization
   - Static file serving for dashboards
   - REST API endpoints for dashboard queries
   - WebSocket for real-time updates

This is what enables developers to register games into the multiverse.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    # Ensure UTF-8 output on Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 70)
    print("🎮 THE SEED - MMO SIMULATION LAUNCHER")
    print("=" * 70)
    
    # Get paths
    repo_root = Path(__file__).parent.parent.parent
    web_dir = repo_root / "web"
    server_dir = web_dir / "server"
    
    print(f"\n[INFO] Repo root: {repo_root}")
    print(f"[INFO] Server dir: {server_dir}")
    
    # Start MMO Orchestrator with FastAPI (HTTP + WebSocket on same port)
    print("\n[STARTUP] Starting MMO Orchestrator (FastAPI + WebSocket)...")
    orchestrator_process = subprocess.Popen(
        [sys.executable, str(server_dir / "mmo_orchestrator.py"), "--demo"],
        cwd=str(repo_root)
    )
    
    # Wait for server to start
    time.sleep(4)
    
    print("[OK] MMO Orchestrator started")
    print("     HTTP API: http://localhost:8000/api")
    print("     WebSocket: ws://localhost:8000/ws")
    
    # Open browser to dashboard
    print("\n[STARTUP] Opening browser to MMO dashboard...")
    url = "http://localhost:8000/"
    webbrowser.open(url)
    time.sleep(1)
    print(f"[OK] Browser opened to: {url}")
    
    print("\n" + "=" * 70)
    print("✅ MMO SIMULATION IS LIVE!")
    print("=" * 70)
    print("\n[INFO] Available Interfaces:")
    print("  * Admin Dashboard: http://localhost:8000/")
    print("  * Phase 6C Dashboard: http://localhost:8000/phase6c_dashboard.html")
    print("  * Entity Viewer: http://localhost:8000/admin-entity-viewer.html")
    print("  * 3D Visualization: http://localhost:8000/stat7threejs.html")
    print("  * REST API Base: http://localhost:8000/api")
    print("  * WebSocket API: ws://localhost:8000/ws")
    print("\n[INFO] Available REST Endpoints:")
    print("  * GET /api/health - System health check")
    print("  * GET /api/realms - List all registered game realms")
    print("  * GET /api/npcs - List NPCs")
    print("  * GET /api/stats - System statistics")
    print("\n[INFO] Developer Game Registration:")
    print("  Connect to ws://localhost:8000/ws")
    print("  Send: {\"action\": \"list_games\"}")
    print("  See docs/MMO_GAME_REGISTRATION.md for full API reference")
    print("\n[INFO] Press Ctrl+C in this terminal to stop all servers")
    print("=" * 70)
    
    try:
        # Keep process alive and monitor it
        while True:
            time.sleep(1)
            if orchestrator_process.poll() is not None:
                print("[ERROR] MMO Orchestrator stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Shutdown sequence initiated...")
        orchestrator_process.terminate()
        
        # Wait for graceful shutdown
        try:
            orchestrator_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("  [INFO] Force killing process...")
            orchestrator_process.kill()
        
        print("[OK] Server stopped")
        print("=" * 70)

if __name__ == "__main__":
    main()