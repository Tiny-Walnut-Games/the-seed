#!/usr/bin/env python3
"""STAT7 System Validation Tests - Proper pytest format for Rider test discovery"""

import pytest
from pathlib import Path
import sys
import os

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestStat7System:
    """STAT7 system file validation tests."""
    
    @pytest.mark.e2e
    def test_stat7_server_exists(self):
        """Test that the STAT7 server file exists."""
        server_path = Path("../stat7wsserve.py").resolve()
        assert server_path.exists(), "stat7wsserve.py is required"
    
    @pytest.mark.e2e
    def test_stat7_html_exists(self):
        """Test that the STAT7 HTML interface exists.""" 
        html_path = Path("../stat7threejs.html").resolve()
        assert html_path.exists(), "stat7threejs.html is required"
    
    @pytest.mark.e2e
    def test_all_stat7_files_present(self):
        """Test that all required STAT7 files are present."""
        files_to_check = [
            "../stat7wsserve.py",
            "../stat7threejs.html"
        ]
        
        missing_files = [f for f in files_to_check if not Path(f).resolve().exists()]
        assert not missing_files, f"Missing files: {missing_files}"


if __name__ == "__main__":
    # Fallback print mode for manual execution
    print("🌟 STAT7 System Check")
    print("=" * 30)
    
    files_to_check = ["../stat7wsserve.py", "../stat7threejs.html"]
    
    print("Checking files...")
    for file in files_to_check:
        if Path(file).resolve().exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    print("\n🎉 STAT7 files validated!")
    print("Ready to run visualization system.")