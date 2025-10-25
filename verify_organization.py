#!/usr/bin/env python3
"""
STAT7 Project Organization Verification Script
Verifies that all test files and websocket components are properly organized.
"""

import os
import sys
from pathlib import Path

def main():
    """Main verification function."""
    root_path = Path(__file__).parent
    print("🔍 STAT7 Project Organization Verification")
    print("=" * 50)
    
    success = True
    
    # Check tests folder structure
    tests_path = root_path / "tests"
    if not tests_path.exists():
        print("❌ tests/ folder does not exist")
        success = False
    else:
        print("✅ tests/ folder exists")
        
        # Check main test files
        expected_test_files = [
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
        
        for test_file in expected_test_files:
            file_path = tests_path / test_file
            if file_path.exists():
                print(f"✅ tests/{test_file} exists")
            else:
                print(f"❌ tests/{test_file} missing")
                success = False
    
    # Check websocket organization
    websocket_path = root_path / "websocket"
    if not websocket_path.exists():
        print("❌ websocket/ folder does not exist")
        success = False
    else:
        print("✅ websocket/ folder exists")
        
        # Check websocket files
        expected_websocket_files = [
            "stat7-websocket.js"
        ]
        
        for ws_file in expected_websocket_files:
            file_path = websocket_path / ws_file
            if file_path.exists():
                print(f"✅ websocket/{ws_file} exists")
            else:
                print(f"❌ websocket/{ws_file} missing")
                success = False
    
    # Check websocket tests organization
    websocket_tests_path = tests_path / "websocket"
    if not websocket_tests_path.exists():
        print("❌ tests/websocket/ folder does not exist")
        success = False
    else:
        print("✅ tests/websocket/ folder exists")
        
        expected_websocket_test_files = [
            "test_websocket_fix.py",
            "debug_websocket_data.py",
            "__init__.py"
        ]
        
        for ws_test_file in expected_websocket_test_files:
            file_path = websocket_tests_path / ws_test_file
            if file_path.exists():
                print(f"✅ tests/websocket/{ws_test_file} exists")
            else:
                print(f"❌ tests/websocket/{ws_test_file} missing")
                success = False
    
    # Check that root stub files exist and contain proper stubs
    stub_files = [
        "test_stat7.py",
        "test_stat7_e2e.py", 
        "test_server_data.py",
        "test_stat7_setup.py",
        "test_complete_system.py",
        "test_enhanced_visualization.py",
        "test_websocket_fix.py",
        "simple_test.py",
        "debug_websocket_data.py",
        "stat7-websocket.js"
    ]
    
    print("\n🔄 Checking root directory stubs...")
    for stub_file in stub_files:
        file_path = root_path / stub_file
        if file_path.exists():
            content = file_path.read_text().strip()
            if content.startswith("# MOVED TO"):
                print(f"✅ {stub_file} is properly stubbed")
            else:
                print(f"❌ {stub_file} exists but is not a proper stub")
                success = False
        else:
            print(f"⚠️  {stub_file} stub file not found (may be OK)")
    
    # Check core STAT7 files
    print("\n🎯 Checking core STAT7 files...")
    core_files = [
        "stat7wsserve.py",
        "stat7threejs.html",
        "stat7-core.js",
        "stat7-main.js",
        "stat7-ui.js"
    ]
    
    for core_file in core_files:
        file_path = root_path / core_file
        if file_path.exists():
            print(f"✅ {core_file} exists")
        else:
            print(f"❌ {core_file} missing")
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PROJECT ORGANIZATION VERIFICATION PASSED!")
        print("All test files and websocket components are properly organized.")
    else:
        print("💥 PROJECT ORGANIZATION VERIFICATION FAILED!")
        print("Some files are missing or improperly organized.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())