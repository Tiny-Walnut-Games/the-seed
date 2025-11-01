#!/usr/bin/env python3
"""
Diagnostic script to verify test_concurrent_1000_clients is correctly defined
and can be identified by pytest.
"""

import subprocess
import sys

print("Verifying test_concurrent_1000_clients definition...")
print("=" * 60)

# List all tests in the file
print("\n1. Listing all concurrent client tests:")
print("-" * 60)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_websocket_load_stress.py", "--collect-only", "-q"],
    capture_output=True,
    text=True,
    cwd="E:/Tiny_Walnut_Games/the-seed"
)
lines = result.stdout.split('\n')
concurrent_tests = [l for l in lines if 'concurrent' in l.lower()]
for test in concurrent_tests:
    print(f"  {test}")

print("\n2. Tests containing '1000':")
print("-" * 60)
for line in lines:
    if '1000' in line:
        print(f"  FOUND: {line}")

print("\n3. Tests containing '500' (should NOT include 1000):")
print("-" * 60)
for line in lines:
    if '500' in line and '1000' not in line:
        print(f"  FOUND: {line}")

print("\nDiagnostic complete")