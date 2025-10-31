#!/usr/bin/env python3
"""STAT7 server functionality tests."""

import pytest
import sys
import os
import asyncio
import json
from pathlib import Path

# Add root to path and ensure project paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Use path_utils for consistent path resolution
try:
    from path_utils import ensure_project_paths
    ensure_project_paths()
except ImportError:
    # Fallback if path_utils not available
    web_server_dir = os.path.join(root_dir, 'web', 'server')
    if web_server_dir not in sys.path:
        sys.path.insert(0, web_server_dir)


@pytest.mark.integration
class TestStat7Server:
    """STAT7 server functionality tests."""

    @pytest.mark.e2e
    def test_server_imports(self):
        """Test that server components can be imported."""
        try:
            from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer, generate_random_bitchain
            assert STAT7EventStreamer is not None
            assert ExperimentVisualizer is not None 
            assert generate_random_bitchain is not None
        except ImportError as e:
            pytest.fail(f"Server imports failed: {e}")

    @pytest.mark.e2e
    def test_server_initialization(self):
        """Test server initialization."""
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        visualizer = ExperimentVisualizer(streamer)
        
        assert streamer.host == "localhost"
        assert streamer.port == 8765
        assert visualizer.streamer is streamer

    @pytest.mark.integration
    def test_bitchain_generation(self):
        """Test BitChain generation."""
        from stat7wsserve import generate_random_bitchain
        
        # Test with seed for reproducibility
        bitchain1 = generate_random_bitchain(seed=42)
        bitchain2 = generate_random_bitchain(seed=42)
        
        assert bitchain1 is not None
        assert bitchain2 is not None
        assert hasattr(bitchain1, 'id')
        assert hasattr(bitchain1, 'realm')
        assert hasattr(bitchain1, 'entity_type')

    @pytest.mark.e2e
    def test_event_creation(self):
        """Test event creation from BitChain."""
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_EXP")
        
        assert event is not None
        assert event.event_type == "bitchain_created"
        assert event.experiment_id == "TEST_EXP"
        assert event.data is not None

    @pytest.mark.e2e
    def test_event_serialization(self):
        """Test event JSON serialization."""
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_EXP")
        
        # Test to_dict method
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert 'event_type' in event_dict
        assert 'timestamp' in event_dict
        assert 'data' in event_dict
        
        # Test JSON serialization
        json_str = json.dumps(event_dict)
        assert len(json_str) > 0
        
        # Test deserialization
        parsed = json.loads(json_str)
        assert parsed['event_type'] == 'bitchain_created'


if __name__ == "__main__":
    pytest.main([__file__])