"""
Pytest configuration and fixtures for The Seed project.

This file:
1. Enables IDE test discovery in JetBrains Rider
2. Sets up shared test fixtures
3. Configures logging for test output
4. Handles sys.path setup for imports
"""

import sys
import os
from pathlib import Path

# Add project root and seed/engine to sys.path so imports work
PROJECT_ROOT = Path(__file__).parent.parent
SEED_ENGINE = PROJECT_ROOT / "seed" / "engine"
SEED_DOCS = PROJECT_ROOT / "seed" / "docs"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SEED_ENGINE))
sys.path.insert(0, str(SEED_DOCS))

import pytest
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def project_root():
    """Fixture providing the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def seed_engine():
    """Fixture providing the seed/engine directory."""
    return SEED_ENGINE


@pytest.fixture(scope="session")
def seed_docs():
    """Fixture providing the seed/docs directory."""
    return SEED_DOCS


@pytest.fixture
def test_data_dir(tmp_path):
    """Fixture providing a temporary directory for test data."""
    return tmp_path


def pytest_configure(config):
    """Configure pytest at startup."""
    # Custom configuration can go here
    config.addinivalue_line(
        "markers", "exp: STAT7 experiments (EXP-01 through EXP-10)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to auto-mark experiments."""
    for item in items:
        # Auto-mark tests based on filename
        if "exp06" in item.nodeid:
            item.add_marker(pytest.mark.exp06)
        elif "exp05" in item.nodeid:
            item.add_marker(pytest.mark.exp05)
        elif "exp04" in item.nodeid:
            item.add_marker(pytest.mark.exp04)
        elif "robustness" in item.nodeid:
            item.add_marker(pytest.mark.robustness)
        elif "stress" in item.nodeid:
            item.add_marker(pytest.mark.slow)