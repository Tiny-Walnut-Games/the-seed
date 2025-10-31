"""
Standardized Path Resolution for The Seed Project

This utility ensures consistent module importing across the entire project,
whether scripts are run from root, tests/, web/, or any other location.

Usage:
    from path_utils import ensure_project_paths
    ensure_project_paths()
    
    # Now you can import from any server module
    from stat7wsserve import STAT7EventStreamer
"""

import sys
import os
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    # Try multiple methods to find project root
    current = Path(__file__).resolve()
    
    # If we're in a subdirectory, search upward
    for parent in current.parents:
        if (parent / 'pytest.ini').exists() or (parent / 'the-seed.sln').exists():
            return parent
    
    # Fallback to the directory containing this file
    return current.parent


def get_web_server_path():
    """Get the web/server directory path."""
    return get_project_root() / 'web' / 'server'


def get_seed_engine_path():
    """Get the seed engine path for stat7_experiments."""
    return get_project_root() / 'packages' / 'com.twg.the-seed' / 'seed' / 'engine'


def ensure_project_paths():
    """
    Add all critical project paths to sys.path.
    
    This should be called at the top of any script that imports
    from web/server or other cross-module dependencies.
    
    Returns:
        dict: Information about paths added
    """
    root = get_project_root()
    web_server = get_web_server_path()
    seed_engine = get_seed_engine_path()
    
    paths_added = {
        'root': str(root),
        'web_server': str(web_server),
        'seed_engine': str(seed_engine),
    }
    
    # Add paths to sys.path in order of priority
    for path_str in [str(web_server), str(seed_engine), str(root)]:
        if path_str not in sys.path and os.path.exists(path_str):
            sys.path.insert(0, path_str)
    
    return paths_added


def verify_imports():
    """
    Verify that critical imports are available.
    
    Returns:
        dict: Status of each import
    """
    ensure_project_paths()
    
    results = {}
    
    # Test stat7wsserve imports
    try:
        from stat7wsserve import STAT7EventStreamer
        results['stat7wsserve.STAT7EventStreamer'] = 'OK'
    except ImportError as e:
        results['stat7wsserve.STAT7EventStreamer'] = f'FAIL: {e}'
    
    # Test stat7_experiments imports
    try:
        from stat7_experiments import generate_random_bitchain
        results['stat7_experiments.generate_random_bitchain'] = 'OK'
    except ImportError as e:
        results['stat7_experiments.generate_random_bitchain'] = f'FAIL: {e}'
    
    return results


if __name__ == '__main__':
    print("🔍 Project Path Configuration")
    print("=" * 60)
    
    paths = ensure_project_paths()
    print("\n📁 Paths added to sys.path:")
    for key, path in paths.items():
        print(f"  {key:20s}: {path}")
    
    print("\n🧪 Verifying imports...")
    results = verify_imports()
    for import_name, status in results.items():
        symbol = "✅" if status == 'OK' else "❌"
        print(f"  {symbol} {import_name:50s}: {status}")
    
    print("\n✓ Path configuration complete")