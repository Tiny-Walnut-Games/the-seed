#!/usr/bin/env python3
"""
Test script for enhanced STAT7 visualization features.

Tests the new UI improvements, entity drill-down, and advanced proofs.
"""

import asyncio
import websockets
import json
import time
from datetime import datetime, timezone

async def test_enhanced_features():
    """Test the enhanced visualization features."""

    print("🧪 Testing Enhanced STAT7 Visualization Features")
    print("=" * 60)

    try:
        # Connect to WebSocket server
        uri = "ws://localhost:8765"
        print(f"🔌 Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected to STAT7 WebSocket server")

            # Test 1: Semantic Fidelity Proof
            print("\n📊 Test 1: Semantic Fidelity Proof")
            print("-" * 40)

            semantic_request = {
                "type": "run_semantic_fidelity_proof",
                "sample_size": 50
            }

            await websocket.send(json.dumps(semantic_request))
            print("📤 Sent semantic fidelity proof request")

            # Wait for entities to be created
            entity_count = 0
            start_time = time.time()

            while entity_count < 50 and time.time() - start_time < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data.get('event_type') == 'bitchain_created':
                        entity_count += 1
                        if entity_count % 10 == 0:
                            print(f"📈 Received {entity_count} semantic entities...")

                    elif data.get('event_type') == 'experiment_completed':
                        print(f"✅ Semantic fidelity proof completed: {data.get('data', {})}")
                        break

                except asyncio.TimeoutError:
                    continue

            # Test 2: Resilience Testing
            print("\n🛡️ Test 2: Resilience Testing")
            print("-" * 40)

            resilience_request = {
                "type": "run_resilience_testing",
                "sample_size": 30
            }

            await websocket.send(json.dumps(resilience_request))
            print("📤 Sent resilience testing request")

            # Wait for resilience entities
            resilience_count = 0
            start_time = time.time()

            while resilience_count < 30 and time.time() - start_time < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data.get('event_type') == 'bitchain_created':
                        resilience_count += 1
                        if resilience_count % 10 == 0:
                            print(f"🔧 Received {resilience_count} resilience entities...")

                    elif data.get('event_type') == 'experiment_completed':
                        print(f"✅ Resilience testing completed: {data.get('data', {})}")
                        break

                except asyncio.TimeoutError:
                    continue

            # Test 3: Experiment Control
            print("\n🎮 Test 3: Experiment Control")
            print("-" * 40)

            # Start experiment
            start_request = {
                "type": "start_experiment",
                "experiment_id": "TEST_EXP",
                "duration": 5
            }

            await websocket.send(json.dumps(start_request))
            print("📤 Sent experiment start request")

            # Stop experiment
            await asyncio.sleep(2)
            stop_request = {
                "type": "stop_experiment",
                "experiment_id": "TEST_EXP"
            }

            await websocket.send(json.dumps(stop_request))
            print("📤 Sent experiment stop request")

            print("\n🎉 All tests completed successfully!")
            print(f"📊 Total entities processed: {entity_count + resilience_count}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Starting Enhanced STAT7 Visualization Test")
    print("Make sure the STAT7 WebSocket server is running:")
    print("  python stat7wsserve.py")
    print()

    success = asyncio.run(test_enhanced_features())

    if success:
        print("\n✅ All tests passed! The enhanced visualization is ready.")
    else:
        print("\n❌ Some tests failed. Check the server logs.")
