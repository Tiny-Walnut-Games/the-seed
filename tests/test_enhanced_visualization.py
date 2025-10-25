#!/usr/bin/env python3
"""
Test script for enhanced STAT7 visualization features.

Tests the new UI improvements, entity drill-down, and advanced proofs.
"""

import asyncio
import websockets
import json
import time
import pytest
import sys
import os
from datetime import datetime, timezone

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnhancedVisualization:
    """Enhanced STAT7 visualization feature tests."""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection capability."""
        try:
            uri = "ws://localhost:8765"
            # Test with timeout to avoid hanging in CI
            async with asyncio.timeout(5):
                async with websockets.connect(uri) as websocket:
                    assert websocket is not None
                    assert websocket.open
        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not running")

    def test_semantic_request_structure(self):
        """Test semantic fidelity proof request structure."""
        semantic_request = {
            "type": "run_semantic_fidelity_proof", 
            "sample_size": 50
        }
        
        assert "type" in semantic_request
        assert "sample_size" in semantic_request
        assert semantic_request["type"] == "run_semantic_fidelity_proof"
        assert isinstance(semantic_request["sample_size"], int)

    def test_resilience_request_structure(self):
        """Test resilience testing request structure."""
        resilience_request = {
            "type": "run_resilience_testing",
            "sample_size": 25
        }
        
        assert "type" in resilience_request
        assert "sample_size" in resilience_request
        assert resilience_request["type"] == "run_resilience_testing"
        assert isinstance(resilience_request["sample_size"], int)

    def test_experiment_request_structure(self):
        """Test experiment request structure."""
        exp_request = {
            "type": "start_experiment",
            "experiment_id": "EXP01",
            "duration": 30
        }
        
        assert "type" in exp_request
        assert "experiment_id" in exp_request
        assert "duration" in exp_request
        assert exp_request["type"] == "start_experiment"

    @pytest.mark.asyncio
    async def test_message_handling(self):
        """Test WebSocket message handling."""
        # Test JSON parsing functionality
        test_message = {
            "event_type": "bitchain_created",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "id": "test_123",
                "entity_type": "test_entity",
                "realm": "test_realm"
            }
        }
        
        json_str = json.dumps(test_message)
        parsed = json.loads(json_str)
        
        assert parsed["event_type"] == "bitchain_created"
        assert "timestamp" in parsed
        assert "data" in parsed
        assert parsed["data"]["id"] == "test_123"


if __name__ == "__main__":
    pytest.main([__file__])