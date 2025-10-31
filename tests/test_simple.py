#!/usr/bin/env python3
"""
Simple STAT7 Test - No subprocess calls
Direct Python execution to avoid IDE PowerShell issues
"""

import os
import sys
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


@pytest.mark.unit
class TestSimple:
    """Simple STAT7 system tests."""

    @pytest.mark.unit
    def test_current_directory(self):
        """Test current directory accessibility."""
        current_dir = Path.cwd()
        assert current_dir.exists()
        assert current_dir.is_dir()

    @pytest.mark.unit
    def test_required_files_exist(self):
        """Test that required files exist."""
        root_path = Path(__file__).parent.parent
        required_files = [
            "web/server/stat7wsserve.py",
            "web/stat7threejs.html",
        ]
        
        missing_files = []
        for file in required_files:
            if not (root_path / file).exists():
                missing_files.append(file)
        
        assert not missing_files, f"Missing required files: {missing_files}"

    @pytest.mark.unit
    def test_module_imports(self):
        """Test basic module imports."""
        try:
            import asyncio
            import json
            import pathlib
            assert True  # All imports successful
        except ImportError as e:
            pytest.fail(f"Basic module import failed: {e}")

    @pytest.mark.unit
    def test_stat7_server_import(self):
        """Test STAT7 server module import."""
        try:
            # Paths already configured at module level
            from stat7wsserve import STAT7EventStreamer
            assert STAT7EventStreamer is not None
        except ImportError as e:
            pytest.fail(f"STAT7 server import failed: {e}")

    @pytest.mark.unit
    def test_pathlib_functionality(self):
        """Test pathlib functionality for file operations."""
        test_path = Path(__file__)
        assert test_path.exists()
        assert test_path.is_file()
        assert test_path.suffix == '.py'
        assert test_path.parent.name == 'tests'


if __name__ == "__main__":
    pytest.main([__file__])