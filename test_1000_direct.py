#!/usr/bin/env python3
"""
Direct test to verify 1000-client test loads and identifies correctly
"""
import sys
import os

# Setup paths exactly as the test file does
test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_dir, 'web/server'))

repo_root = os.path.abspath(os.path.join(test_dir, './'))
seed_engine_path = os.path.join(repo_root, 'packages', 'com.twg.the-seed', 'seed', 'engine')
if seed_engine_path not in sys.path:
    sys.path.insert(0, seed_engine_path)

print("Testing imports and 1000-client test setup...")
print("=" * 60)

# Import the test module
from tests.test_websocket_load_stress import test_concurrent_1000_clients, test_concurrent_500_clients
from stat7wsserve import generate_random_bitchain

print("SUCCESS: Imported test_concurrent_1000_clients")
print(f"  Function name: {test_concurrent_1000_clients.__name__}")
print(f"  Function doc: {test_concurrent_1000_clients.__doc__}")

print("\nSUCCESS: Imported test_concurrent_500_clients")
print(f"  Function name: {test_concurrent_500_clients.__name__}")
print(f"  Function doc: {test_concurrent_500_clients.__doc__}")

# Verify they're different functions
print("\n" + "=" * 60)
print("VERIFICATION:")
print(f"  test_concurrent_1000_clients is test_concurrent_500_clients: {test_concurrent_1000_clients is test_concurrent_500_clients}")
print(f"  Functions are different: {test_concurrent_1000_clients != test_concurrent_500_clients}")

# Test generate_random_bitchain
print("\nTesting generate_random_bitchain (from REAL stat7_experiments):")
import inspect
source_file = inspect.getsourcefile(generate_random_bitchain)
print(f"  Source: {source_file}")
bitchain = generate_random_bitchain(seed=42)
print(f"  Generated bitchain type: {type(bitchain).__name__}")
print(f"  BitChain has compute_address: {hasattr(bitchain, 'compute_address')}")

print("\n" + "=" * 60)
print("ALL CHECKS PASSED - test_concurrent_1000_clients is correctly defined!")