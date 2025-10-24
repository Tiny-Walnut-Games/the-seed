#!/usr/bin/env python3
"""
Quick test to verify the WebSocket server is sending correct data
"""

import asyncio
import sys
import os
import pytest

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestServerData:
    """WebSocket server data generation tests."""

    def test_server_components_creation(self):
        """Test server components can be created."""
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)
        
        assert streamer is not None
        assert visualizer is not None

    def test_bitchain_generation(self):
        """Test BitChain generation with seed."""
        from stat7wsserve import generate_random_bitchain
        
        bitchain = generate_random_bitchain(seed=42)
        
        assert bitchain is not None
        assert hasattr(bitchain, 'id')
        assert bitchain.id is not None

    def test_event_creation(self):
        """Test event creation from BitChain."""
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "test-exp")
        
        assert event is not None
        assert hasattr(event, 'event_type')
        assert hasattr(event, 'timestamp')
        assert hasattr(event, 'experiment_id')
        assert hasattr(event, 'data')

    def test_event_data_structure(self):
        """Test event data structure completeness."""
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "test-exp")
        
        assert event.event_type is not None
        assert event.timestamp is not None
        assert event.experiment_id == "test-exp"
        assert event.data is not None
        
        # Check data contains expected keys
        data = event.data
        assert 'id' in data or 'bitchain' in data


if __name__ == "__main__":
    pytest.main([__file__])