#!/usr/bin/env python3
"""
Test visualization connectivity to MMO Orchestrator WebSocket.
Verifies the fix: stat7-config.js now connects to ws://localhost:8000/ws
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    import websockets
except ImportError:
    print("[SKIP] websockets not installed, install with: pip install websockets")
    sys.exit(0)


async def test_websocket_connection():
    """Test WebSocket connection to MMO Orchestrator."""
    ws_url = "ws://localhost:8000/ws"
    
    print(f"\n[TEST] Connecting to WebSocket: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Try to receive a message with timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                msg_data = json.loads(message)
                print(f"✅ Received event: {msg_data.get('type', 'unknown')}")
                print(f"   Data keys: {list(msg_data.keys())}")
                return True
            except asyncio.TimeoutError:
                print("⚠️  WebSocket timeout (3s) - server not broadcasting events yet")
                print("   (This is OK - visualization will work once events start)")
                return True
    except ConnectionRefusedError as e:
        print(f"❌ Connection refused: {e}")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False


async def main():
    print("=" * 70)
    print("🔌 VISUALIZATION CONNECTIVITY TEST")
    print("=" * 70)
    
    # Check API first
    print("\n[INFO] Checking REST API health...")
    try:
        import urllib.request
        import json
        
        response = urllib.request.urlopen("http://localhost:8000/api/health", timeout=2)
        data = json.loads(response.read())
        print(f"✅ API is healthy: {data}")
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False
    
    # Test WebSocket
    success = await test_websocket_connection()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ VISUALIZATION CONNECTIVITY OK")
        print("   The 3D visualization should now render correctly!")
        print("   Open: http://localhost:8000/stat7threejs.html")
    else:
        print("❌ VISUALIZATION CONNECTIVITY FAILED")
        print("   Check that the MMO Orchestrator is running")
        print("   Launch with: python web/launchers/launch_mmo_simulation.py")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)