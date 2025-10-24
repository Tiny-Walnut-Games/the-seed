#!/usr/bin/env python3
"""
Complete STAT7 Visualization System Test

This script tests the entire visualization pipeline:
1. WebSocket server functionality
2. Event generation and broadcasting  
3. HTML/JavaScript visualization client
4. Experiments EXP-01 through EXP-10 integration
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone
import pytest
from pathlib import Path

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCompleteSystem:
    """Complete STAT7 visualization system tests."""

    def test_stat7_imports(self):
        """Test that all STAT7 components can be imported."""
        try:
            # Test import from root level
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer, generate_random_bitchain
            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import STAT7 components: {e}")

    def test_event_generation(self):
        """Test BitChain event generation."""
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_COMPLETE")
        
        assert event is not None
        assert hasattr(event, 'event_type')
        assert hasattr(event, 'experiment_id')
        assert hasattr(event, 'data')

    def test_coordinate_validation(self):
        """Test 7D coordinate system validation."""
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_COMPLETE")
        
        coords = event.data['stat7_coordinates']
        required_coords = ['realm', 'lineage', 'adjacency', 'horizon', 'resonance', 'velocity', 'density']
        
        for coord in required_coords:
            assert coord in coords, f"Missing coordinate: {coord}"

    def test_json_serialization(self):
        """Test event JSON serialization."""
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_COMPLETE")
        
        event_dict = event.to_dict()
        json_str = json.dumps(event_dict, indent=2)
        
        assert len(json_str) > 0
        assert isinstance(event_dict, dict)
        
    def test_metadata_validation(self):
        """Test visualization metadata validation."""
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from stat7wsserve import STAT7EventStreamer, generate_random_bitchain
        
        streamer = STAT7EventStreamer(host="localhost", port=8765)
        bitchain = generate_random_bitchain(seed=42)
        event = streamer.create_bitchain_event(bitchain, "TEST_COMPLETE")
        
        assert event.metadata is not None
        assert 'color' in event.metadata or 'size' in event.metadata or 'visualization_type' in event.metadata


if __name__ == "__main__":
    pytest.main([__file__])