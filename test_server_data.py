#!/usr/bin/env python3
"""
Quick test to verify the WebSocket server is sending correct data
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_server_data():
    """Test what data the server is generating."""
    print("🧪 Testing WebSocket Server Data Generation...")

    try:
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer, generate_random_bitchain

        # Create server components
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)

        print("✅ Server components created")

        # Test event creation
        bitchain = generate_random_bitchain(seed=42)
        print(f"✅ Generated test BitChain: {bitchain.id}")

        event = streamer.create_bitchain_event(bitchain, "test-exp")
        print(f"✅ Created event: {event.event_type}")

        # Check event data structure
        print("\n📊 Event Data Structure:")
        print(f"  Event Type: {event.event_type}")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  Experiment ID: {event.experiment_id}")

        print("\n📋 BitChain Data:")
        data = event.data
        print(f"  ID: {data.get('id', 'MISSING')}")
        print(f"  Entity Type: {data.get('entity_type', 'MISSING')}")
        print(f"  Realm: {data.get('realm', 'MISSING')}")

        print("\n📍 STAT7 Coordinates:")
        coords = data.get('stat7_coordinates')
        if coords:
            print(f"  Realm: {coords.get('realm', 'MISSING')}")
            print(f"  Lineage: {coords.get('lineage', 'MISSING')}")
            print(f"  Horizon: {coords.get('horizon', 'MISSING')}")
            print(f"  Resonance: {coords.get('resonance', 'MISSING')}")
            print(f"  Velocity: {coords.get('velocity', 'MISSING')}")
            print(f"  Density: {coords.get('density', 'MISSING')}")
            print(f"  Adjacency: {coords.get('adjacency', 'MISSING')}")
        else:
            print("  ❌ NO STAT7_COORDINATES FOUND!")

        print("\n🎨 Metadata:")
        metadata = event.metadata
        if metadata:
            print(f"  Color: {metadata.get('color', 'MISSING')}")
            print(f"  Size: {metadata.get('size', 'MISSING')}")
            print(f"  Type: {metadata.get('visualization_type', 'MISSING')}")
        else:
            print("  ❌ NO METADATA FOUND!")

        # Test JSON serialization
        import json
        event_dict = event.to_dict()
        json_str = json.dumps(event_dict)
        print(f"\n✅ JSON serialization works ({len(json_str)} chars)")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 STAT7 WebSocket Server Data Test")
    print("=" * 50)
    success = asyncio.run(test_server_data())

    if success:
        print("\n🎉 Server data generation test PASSED!")
        print("\n📋 Next steps:")
        print("1. Start WebSocket server: python stat7wsserve.py")
        print("2. Start web server: python simple_web_server.py")
        print("3. Open browser and check console for detailed logs")
    else:
        print("\n❌ Server data generation test FAILED!")
