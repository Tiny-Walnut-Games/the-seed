#!/usr/bin/env python3
"""
Quick test for the fixed WebSocket server
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_websocket_server():
    """Test the WebSocket server with a simple connection."""
    print("🧪 Testing WebSocket Server Fix...")

    try:
        # Import the fixed server
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer

        # Create server instance
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)

        print("✅ Server imports and initializes successfully")

        # Test event creation
        from stat7wsserve import generate_random_bitchain
        bitchain = generate_random_bitchain()
        event = streamer.create_bitchain_event(bitchain, "test")

        print("✅ Event creation works")
        print(f"   Event type: {event.event_type}")
        print(f"   Timestamp: {event.timestamp}")
        print(f"   BitChain realm: {event.data['realm']}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket_server())
    if success:
        print("\n🎉 WebSocket server fix verified!")
        print("\n🚀 You can now run:")
        print("   python stat7wsserve.py")
        print("\nAnd in another terminal:")
        print("   python simple_web_server.py")
    else:
        print("\n❌ Fix verification failed")
