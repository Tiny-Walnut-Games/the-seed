#!/usr/bin/env python3
"""
Quick test to verify STAT7 visualization setup
"""

import os
import sys
import subprocess
import webbrowser
import time
import pytest
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
class TestStat7Setup:
    """STAT7 visualization setup tests."""

    @pytest.mark.integration
    def test_required_files_exist(self):
        """Test if all required files are present."""
        root_path = Path(__file__).parent.parent
        required_files = [
            "stat7wsserve.py",
            "stat7threejs.html",
            "start_stat7_visualization.py",
            "requirements-visualization.txt"
        ]

        missing_files = []
        for file in required_files:
            if not (root_path / file).exists():
                missing_files.append(file)

        assert not missing_files, f"Missing files: {missing_files}"

    @pytest.mark.e2e
    def test_python_dependencies_importable(self):
        """Test if required Python packages can be imported."""
        required_modules = [
            'asyncio',
            'websockets', 
            'json',
            'pathlib'
        ]

        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                pytest.fail(f"Required module {module} not available")

    @pytest.mark.e2e
    def test_websocket_server_importable(self):
        """Test if WebSocket server components can be imported."""
        try:
            from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer
        except ImportError as e:
            pytest.fail(f"Cannot import WebSocket server components: {e}")

    @pytest.mark.integration
    def test_file_permissions(self):
        """Test file permissions for executable scripts."""
        root_path = Path(__file__).parent.parent
        executable_files = [
            "stat7wsserve.py",
            "start_stat7_visualization.py"
        ]

        for file in executable_files:
            file_path = root_path / file
            if file_path.exists():
                assert file_path.is_file(), f"{file} is not a regular file"
                # On Windows, checking execution permission is different
                if os.name != 'nt':
                    assert os.access(file_path, os.X_OK), f"{file} is not executable"


if __name__ == "__main__":
    pytest.main([__file__])