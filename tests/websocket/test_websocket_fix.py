#!/usr/bin/env python3
"""
Quick test for the fixed WebSocket server
"""

import asyncio
import sys
import os
import pytest

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestWebSocketFix:
    """WebSocket server fix validation tests."""

    def test_websocket_server_imports(self):
        """Test that WebSocket server imports work."""
        try:
            from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import WebSocket components: {e}")

    def test_websocket_server_creation(self):
        """Test WebSocket server instance creation."""
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)
        
        assert streamer is not None
        assert visualizer is not None

    def test_websocket_event_creation(self):
        """Test WebSocket event creation."""
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain()
        event = streamer.create_bitchain_event(bitchain, "test")
        
        assert event is not None
        assert hasattr(event, 'event_type')
        assert hasattr(event, 'timestamp') 
        assert hasattr(event, 'data')
        assert 'realm' in event.data


if __name__ == "__main__":
    pytest.main([__file__])