"""Pytest configuration for Warbler CDA tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data():
    """Provide test data for use in tests."""
    return {
        "sample_texts": [
            "The quick brown fox jumps over the lazy dog",
            "Semantic embeddings enable efficient document retrieval",
            "Machine learning models learn from data",
            "Performance optimization techniques improve speed",
            "Philosophy explores fundamental questions",
        ],
        "sample_documents": [
            ("doc_1", "Document about performance optimization"),
            ("doc_2", "Document about semantic embeddings"),
            ("doc_3", "Document about machine learning"),
            ("doc_4", "Document about philosophy and wisdom"),
            ("doc_5", "Document about distributed systems"),
        ],
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "embedding: tests for embedding providers")
    config.addinivalue_line("markers", "retrieval: tests for retrieval API")
    config.addinivalue_line("markers", "fractalstat: tests for FractalStat integration")
    config.addinivalue_line("markers", "e2e: end-to-end integration tests")
    config.addinivalue_line("markers", "slow: tests that take longer to run")
