#!/usr/bin/env python3
"""
Debug script to check what data is being sent by the WebSocket server
"""

import asyncio
import websockets
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_websocket_data():
    """Connect to WebSocket server and print received data."""
    print("🔍 Connecting to WebSocket server...")

    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("✅ Connected to WebSocket server")
            print("📡 Listening for messages...")

            message_count = 0
            async for message in websocket:
                message_count += 1
                print(f"\n--- Message {message_count} ---")

                try:
                    data = json.loads(message)
                    print(f"Event Type: {data.get('event_type', 'Unknown')}")
                    print(f"Timestamp: {data.get('timestamp', 'Unknown')}")

                    if data.get('event_type') == 'bitchain_created':
                        print("BitChain Data:")
                        bitchain_data = data.get('data', {})
                        print(f"  - ID: {bitchain_data.get('id', 'Unknown')}")
                        print(f"  - Entity Type: {bitchain_data.get('entity_type', 'Unknown')}")
                        print(f"  - Realm: {bitchain_data.get('realm', 'Unknown')}")

                        coords = bitchain_data.get('stat7_coordinates', {})
                        if coords:
                            print(f"  - Coordinates: {coords}")

                        metadata = data.get('metadata', {})
                        if metadata:
                            print(f"  - Metadata: {metadata}")

                    print(f"Full JSON: {json.dumps(data, indent=2)}")

                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw message: {message}")

                # Stop after 10 messages to avoid spam
                if message_count >= 10:
                    print("\n📊 Received 10 messages, stopping...")
                    break

    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the WebSocket server is running:")
        print("   python stat7wsserve.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 WebSocket Data Debug Tool")
    print("=" * 40)
    print("Make sure the WebSocket server is running:")
    print("   python stat7wsserve.py")
    print("Then start some visualization:")
    print("   Type 'continuous' in the server")
    print("=" * 40)

    asyncio.run(test_websocket_data())
