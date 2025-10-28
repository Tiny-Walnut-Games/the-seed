#!/usr/bin/env python3
"""STAT7 file system and organization tests."""

import pytest
from pathlib import Path
import sys
import os

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStat7Files:
    """STAT7 file system and organization tests."""

    def test_core_files_exist(self):
        """Test that core STAT7 files exist."""
        root_path = Path(__file__).parent.parent
        core_files = [
            "stat7wsserve.py",
            "stat7threejs.html",
            "stat7-core.js",
            "stat7-main.js",
            "stat7-ui.js"
        ]
        
        missing_files = []
        for file in core_files:
            if not (root_path / file).exists():
                missing_files.append(file)
        
        assert not missing_files, f"Missing core files: {missing_files}"

    def test_websocket_files_organized(self):
        """Test that websocket files are properly organized."""
        websocket_path = Path(__file__).parent.parent / "websocket"
        
        # Check if websocket folder exists
        assert websocket_path.exists(), "websocket folder should exist"
        
        # Check if websocket files are present
        expected_files = [
            "stat7-websocket.js"
        ]
        
        for file in expected_files:
            file_path = websocket_path / file
            assert file_path.exists(), f"websocket/{file} should exist"

    def test_tests_folder_organized(self):
        """Test that tests folder is properly organized."""
        tests_path = Path(__file__).parent
        
        # Check if main test files exist
        expected_files = [
            "test_stat7.py",
            "test_complete_system.py",
            "test_enhanced_visualization.py"
        ]
        
        for file in expected_files:
            file_path = tests_path / file
            assert file_path.exists(), f"tests/{file} should exist"

    def test_websocket_tests_organized(self):
        """Test that websocket tests are organized."""
        websocket_tests_path = Path(__file__).parent / "websocket"
        
        if websocket_tests_path.exists():
            expected_files = [
                "test_websocket_fix.py",
                "debug_websocket_data.py",
                "__init__.py"
            ]
            
            for file in expected_files:
                file_path = websocket_tests_path / file
                assert file_path.exists(), f"tests/websocket/{file} should exist"

    def test_no_test_files_in_root(self):
        """Test that no test files remain in root directory."""
        root_path = Path(__file__).parent.parent
        
        # Check that test files don't exist in root (should be stubs or moved)
        test_pattern_files = [
            "test_stat7.py",
            "test_stat7_e2e.py", 
            "test_server_data.py",
            "test_stat7_setup.py",
            "test_complete_system.py",
            "test_enhanced_visualization.py",
            "test_websocket_fix.py",
            "simple_test.py"
        ]
        
        for file in test_pattern_files:
            file_path = root_path / file
            if file_path.exists():
                # Read content to ensure it's a stub
                content = file_path.read_text().strip()
                assert content.startswith("# MOVED TO"), f"{file} should be a stub file pointing to tests/ location"

    def test_all_test_files_in_tests_folder(self):
        """Test that all test files are properly located in tests folder."""
        tests_path = Path(__file__).parent
        
        # All main test files should be in tests/
        expected_main_tests = [
            "test_stat7.py",
            "test_complete_system.py", 
            "test_enhanced_visualization.py",
            "test_stat7_e2e.py",
            "test_server_data.py",
            "test_stat7_setup.py",
            "test_stat7_server.py",
            "test_stat7_files.py",
            "test_stat7_websocket.py",
            "test_simple.py"
        ]
        
        for file in expected_main_tests:
            file_path = tests_path / file
            assert file_path.exists(), f"tests/{file} should exist and contain actual test code"
            
            # Verify it's not a stub
            content = file_path.read_text()
            assert not content.startswith("# MOVED TO"), f"tests/{file} should not be a stub"
            assert not content.startswith("# DELETED"), f"tests/{file} should not be deleted"


if __name__ == "__main__":
    pytest.main([__file__])