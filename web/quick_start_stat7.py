#!/usr/bin/env python3
"""
Quick Start Script for STAT7 Visualization
Combines both WebSocket and HTTP server startup
"""

import asyncio
import subprocess
import sys
import time
import os
import webbrowser
from threading import Thread

def start_web_server():
    """Start the web server in a separate process"""
    print("🌐 Starting web server...")
    try:
        subprocess.Popen([sys.executable, "simple_web_server.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        print("✅ Web server started in background")
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")

async def main():
    """Main entry point"""
    print("🚀 STAT7 Quick Start")
    print("=" * 30)
    
    # Start web server
    start_web_server()
    
    # Wait for web server to start
    print("⏳ Waiting for web server to initialize...")
    time.sleep(3)
    
    # Try to open browser
    try:
        webbrowser.open("http://localhost:8000/stat7threejs.html")
        print("🌐 Browser opened to visualization")
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print("📋 Manual step: Open http://localhost:8000/stat7threejs.html")
    
    # Start WebSocket server
    print("🔌 Starting WebSocket server...")
    try:
        from stat7wsserve import main as ws_main
        await ws_main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ WebSocket server error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")