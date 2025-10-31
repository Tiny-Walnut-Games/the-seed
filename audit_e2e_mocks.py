#!/usr/bin/env python3
"""
AUDIT E2E TESTS FOR MOCK VIOLATIONS

E2E tests (@pytest.mark.e2e) must NEVER use mocks.
This script finds any E2E tests that violate this rule.
"""

import re
from pathlib import Path
from typing import List, Dict


def scan_e2e_mocks(root_dir: Path) -> Dict[str, List[str]]:
    """Scan E2E tests for mock usage."""
    
    mock_patterns = [
        r'Mock\(',                      # Mock() constructor
        r'@mock\.',                     # @mock decorators
        r'patch\(',                     # patch() context manager
        r'MagicMock',                   # MagicMock class
        r'PropertyMock',                # PropertyMock class
        r'from unittest\.mock',         # Import from unittest.mock
        r'from unittest import mock',   # Import mock module
    ]
    
    violations = {}
    test_files = sorted(root_dir.rglob("test_*.py"))
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"ERROR reading {test_file}: {e}")
            continue
        
        # Find all @pytest.mark.e2e decorated items
        e2e_pattern = r'@pytest\.mark\.e2e\s+(def|class) (\w+)'
        for match in re.finditer(e2e_pattern, content):
            test_type = match.group(1)
            test_name = match.group(2)
            
            # Extract test body
            start = match.start()
            remaining = content[start:]
            next_def = re.search(r'\n\s*(def|class) ', remaining[50:])
            end = start + (next_def.start() + 50 if next_def else len(remaining))
            test_body = remaining[:end - start]
            
            # Check for mocks
            mock_count = sum(len(re.findall(p, test_body)) for p in mock_patterns)
            
            if mock_count > 0:
                file_key = test_file.name
                if file_key not in violations:
                    violations[file_key] = []
                violations[file_key].append(f"{test_name} ({test_type})")
    
    return violations


def main():
    """Audit E2E tests."""
    root = Path(__file__).parent
    
    print("\n" + "="*70)
    print("E2E TEST MOCK VIOLATION AUDIT")
    print("="*70)
    
    violations = scan_e2e_mocks(root / "tests")
    
    # Also check WARBLER tests
    warbler_tests = root / "packages/com.twg.the-seed/The Living Dev Agent/tests"
    if warbler_tests.exists():
        warbler_violations = scan_e2e_mocks(warbler_tests)
        violations.update(warbler_violations)
    
    if not violations:
        print("\n✅ NO VIOLATIONS FOUND")
        print("\nAll @pytest.mark.e2e tests are mock-free!")
        return
    
    print(f"\n⚠️  FOUND {sum(len(v) for v in violations.values())} VIOLATIONS:\n")
    
    for file_name, tests in sorted(violations.items()):
        print(f"📁 {file_name}")
        for test_name in tests:
            print(f"   ❌ {test_name}")
    
    print("\n" + "="*70)
    print("ACTION REQUIRED")
    print("="*70)
    print("\nFor each violation, either:")
    print("1. Remove the mocks and connect to real systems")
    print("2. Move the test to @pytest.mark.integration (if mixed)")
    print("3. Move the test to @pytest.mark.unit (if only mocks)")
    print("="*70)


if __name__ == "__main__":
    main()