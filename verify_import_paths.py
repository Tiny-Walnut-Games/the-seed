#!/usr/bin/env python3
"""
Path Verification Script for The Seed MMO Framework

This script validates that all critical imports can be resolved from any location,
ensuring the stress test framework can call tests from different contexts.

Run this BEFORE attempting to run the MMO population stress test.
"""

import sys
import os
from pathlib import Path
import subprocess

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")


def print_section(text):
    print(f"\n{BOLD}{text}{RESET}")
    print("-" * 70)


def print_pass(msg):
    print(f"{GREEN}✅ {msg}{RESET}")


def print_fail(msg):
    print(f"{RED}❌ {msg}{RESET}")


def print_warn(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")


def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def verify_path_utils():
    """Verify path_utils module works."""
    print_section("1. Testing path_utils Module")
    
    try:
        from path_utils import ensure_project_paths, verify_imports, get_project_root
        print_pass("path_utils module imported successfully")
        
        # Test functions
        root = get_project_root()
        print_info(f"Project root detected: {root}")
        
        paths = ensure_project_paths()
        print_pass("Project paths configured")
        for key, path in paths.items():
            print_info(f"  {key:20s}: {path}")
        
        return True
    except Exception as e:
        print_fail(f"path_utils error: {e}")
        return False


def verify_server_imports():
    """Verify web/server module imports work."""
    print_section("2. Testing Server Module Imports")
    
    try:
        from path_utils import ensure_project_paths
        ensure_project_paths()
        
        from stat7wsserve import STAT7EventStreamer, ExperimentVisualizer, generate_random_bitchain
        print_pass("STAT7EventStreamer imported")
        print_pass("ExperimentVisualizer imported")
        print_pass("generate_random_bitchain imported")
        
        # Test instantiation
        streamer = STAT7EventStreamer(host="localhost", port=9999)
        print_pass("STAT7EventStreamer instantiated successfully")
        
        bitchain = generate_random_bitchain(seed=42)
        print_pass("Random BitChain generated")
        print_info(f"  BitChain ID: {bitchain.id}")
        print_info(f"  Entity Type: {bitchain.entity_type}")
        print_info(f"  Realm: {bitchain.realm}")
        
        return True
    except Exception as e:
        print_fail(f"Server import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_test_files():
    """Verify test files can be discovered and imported."""
    print_section("3. Testing Test File Imports")
    
    test_files = [
        "tests/test_websocket_load_stress.py",
        "tests/test_stat7_server.py",
        "tests/test_complete_system.py",
        "tests/test_server_data.py",
        "tests/test_simple.py",
        "tests/test_stat7_setup.py",
    ]
    
    root = Path.cwd()
    if not (root / "pytest.ini").exists():
        # Try to find project root
        for parent in Path(__file__).parents:
            if (parent / "pytest.ini").exists():
                root = parent
                break
    
    all_ok = True
    for test_file in test_files:
        test_path = root / test_file
        if test_path.exists():
            print_info(f"Found: {test_file}")
        else:
            print_warn(f"Not found: {test_file}")
            all_ok = False
    
    return all_ok


def verify_pytest_discovery():
    """Verify pytest can discover tests."""
    print_section("4. Testing Pytest Discovery")
    
    try:
        # Find project root and run from there
        from path_utils import get_project_root
        project_root = get_project_root()
        
        # Run with verbose output to see collection results
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-v"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_root)  # Run from project root
        )
        
        # Parse output to count collected tests
        output = result.stdout + result.stderr
        
        # Look for "collected X items" pattern (from pytest output)
        import re
        match = re.search(r'collected\s+(\d+)\s+items?', output)
        
        if match:
            test_count = int(match.group(1))
            if test_count > 0:
                print_pass(f"Pytest discovered {test_count} tests")
                return True
            else:
                print_fail(f"Pytest collected 0 tests (no tests found in tests/ directory)")
                return False
        else:
            # Fallback: count test functions and classes in output
            test_count = output.count('<Function test_') + output.count('<Class Test')
            if test_count > 0:
                print_pass(f"Pytest discovered {test_count} tests")
                return True
            else:
                print_fail(f"Could not determine test count from pytest output")
                print_info(f"Raw output:\n{output[:500]}")
                return False
    except subprocess.TimeoutExpired:
        print_warn("Pytest discovery timed out (>10 seconds)")
        return False
    except Exception as e:
        print_fail(f"Pytest discovery error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_from_different_location():
    """Test imports work from a different working directory."""
    print_section("5. Testing Imports from Different Locations")
    
    original_cwd = os.getcwd()
    success = True
    
    # Test from tests directory
    try:
        test_dir = Path(original_cwd) / "tests"
        if test_dir.exists():
            os.chdir(test_dir)
            sys.path.insert(0, str(test_dir))
            
            try:
                # This should work with our path_utils setup
                from pathlib import Path as P
                root = P(original_cwd)
                sys.path.insert(0, str(root))
                
                from path_utils import ensure_project_paths
                ensure_project_paths()
                
                from stat7wsserve import STAT7EventStreamer
                print_pass("Successfully imported from tests/ directory")
            except Exception as e:
                print_fail(f"Import from tests/ failed: {e}")
                success = False
    finally:
        os.chdir(original_cwd)
        if str(test_dir) in sys.path:
            sys.path.remove(str(test_dir))
    
    return success


def verify_web_server_paths():
    """Verify web server paths are accessible."""
    print_section("6. Testing Web Server Paths")
    
    from path_utils import get_web_server_path, get_seed_engine_path
    
    web_server_path = get_web_server_path()
    if web_server_path.exists():
        print_pass(f"Web server path accessible: {web_server_path}")
        # List key files
        for file in ['stat7wsserve.py', 'admin_api_server.py', 'run_server.py']:
            file_path = web_server_path / file
            if file_path.exists():
                print_info(f"  ✓ {file}")
            else:
                print_warn(f"  ✗ {file} (missing)")
    else:
        print_fail(f"Web server path not found: {web_server_path}")
        return False
    
    seed_engine_path = get_seed_engine_path()
    if seed_engine_path.exists():
        print_pass(f"Seed engine path accessible: {seed_engine_path}")
    else:
        print_warn(f"Seed engine path not found (expected): {seed_engine_path}")
    
    return True


def main():
    """Run all verification tests."""
    print_header("The Seed MMO Framework - Import Path Verification")
    print_info(f"Current directory: {os.getcwd()}")
    print_info(f"Python version: {sys.version.split()[0]}")
    
    results = {
        "path_utils": verify_path_utils(),
        "server_imports": verify_server_imports(),
        "test_files": verify_test_files(),
        "pytest_discovery": verify_pytest_discovery(),
        "different_location": verify_from_different_location(),
        "web_server_paths": verify_web_server_paths(),
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:30s}: {status}")
    
    print(f"\n{BOLD}Total: {passed}/{total} checks passed{RESET}")
    
    if passed == total:
        print_pass("All path verification checks passed! 🎉")
        print_info("You're ready to launch the MMO stress test framework!")
        return 0
    else:
        print_fail(f"Some verification checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())