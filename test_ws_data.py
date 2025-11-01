#!/usr/bin/env python3
"""
Quick test to verify WebSocket server is streaming data.
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Connect to WebSocket and receive 5 events."""
    try:
        async with websockets.connect('ws://localhost:8765') as websocket:
            print("[OK] Connected to WebSocket server on ws://localhost:8765")
            print("[INFO] Waiting for events...\n")
            
            event_count = 0
            async for message in websocket:
                try:
                    event = json.loads(message)
                    event_count += 1
                    
                    # Print event summary
                    event_type = event.get('type', 'unknown')
                    timestamp = event.get('timestamp', 'N/A')
                    print(f"[EVENT {event_count}] Type: {event_type}, Timestamp: {timestamp}")
                    
                    if event_type == 'bitchain':
                        entity_type = event.get('data', {}).get('entity_type', 'N/A')
                        realm = event.get('data', {}).get('realm', 'N/A')
                        print(f"  -> Entity: {entity_type} in Realm: {realm}")
                    elif event_type == 'experiment':
                        exp_event = event.get('data', {}).get('event', 'N/A')
                        print(f"  -> Experiment Event: {exp_event}")
                    
                    if event_count >= 5:
                        print(f"\n[OK] Successfully received {event_count} events!")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"[WARN] Failed to decode JSON: {e}")
                    print(f"  Raw message: {message[:100]}")
                    
    except ConnectionRefusedError:
        print("[ERROR] Failed to connect to WebSocket server")
        print("[INFO] Make sure the server is running on ws://localhost:8765")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())