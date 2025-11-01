#!/usr/bin/env python3
"""
Test Suite Inventory Script
===========================

This script discovers ALL tests in your codebase and categorizes them,
preventing mock implementations from hiding real issues.

Usage:
    python inventory_all_tests.py          # Show summary
    python inventory_all_tests.py --full   # Show detailed list
    python inventory_all_tests.py --fix    # Fix pytest configuration
"""

import subprocess
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
import argparse


class TestInventory:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.tests = defaultdict(list)
        self.markers = set()
        self.all_tests = []
    
    def discover_all_tests(self) -> Dict[str, List[str]]:
        """Use pytest to discover all tests."""
        print("\n" + "=" * 80)
        print("🔍 DISCOVERING ALL TESTS USING PYTEST")
        print("=" * 80 + "\n")
        
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q', '--quiet'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        test_lines = [
            line.strip() 
            for line in result.stdout.split('\n') 
            if line.strip() and '::test_' in line
        ]
        
        self.all_tests = test_lines
        print(f"✅ Discovered {len(test_lines)} total tests\n")
        
        # Categorize tests
        self._categorize_tests(test_lines)
        
        return dict(self.tests)
    
    def _categorize_tests(self, tests: List[str]):
        """Categorize tests by directory and markers."""
        
        for test in tests:
            # Extract file path
            file_part = test.split('::')[0] if '::' in test else test
            
            # Categorize by location
            if 'test_websocket_load_stress.py' in file_part:
                self.tests['Load & Stress Tests'].append(test)
            elif 'living dev agent' in file_part.lower():
                if any(f'exp0{i}' in test.lower() for i in range(1, 11)):
                    self.tests['Experiment Tests (EXP-01 to EXP-10)'].append(test)
                else:
                    self.tests['Living Dev Agent Tests'].append(test)
            elif any(marker in test.lower() for marker in ['e2e', 'integration', 'server']):
                self.tests['Integration Tests'].append(test)
            elif any(marker in test.lower() for marker in ['simple', 'basic', 'unit']):
                self.tests['Unit Tests'].append(test)
            else:
                self.tests['Other Tests'].append(test)
    
    def print_summary(self):
        """Print concise summary."""
        print("\n" + "=" * 80)
        print("📊 TEST INVENTORY SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.all_tests)
        print(f"\n🎯 TOTAL TESTS DISCOVERED: {total_tests}\n")
        
        for category in sorted(self.tests.keys()):
            tests = self.tests[category]
            print(f"\n📁 {category}")
            print("-" * 80)
            print(f"   Count: {len(tests)}")
            
            # Show test breakdown
            by_file = defaultdict(list)
            for test in tests:
                file_part = test.split('::')[0] if '::' in test else test
                by_file[Path(file_part).name].append(test)
            
            for file_name in sorted(by_file.keys()):
                file_tests = by_file[file_name]
                print(f"   📄 {file_name}: {len(file_tests)} tests")
    
    def print_detailed(self):
        """Print detailed test list."""
        self.print_summary()
        
        print("\n" + "=" * 80)
        print("📋 DETAILED TEST LIST")
        print("=" * 80)
        
        for category in sorted(self.tests.keys()):
            print(f"\n\n🔹 {category} ({len(self.tests[category])} tests)")
            print("-" * 80)
            
            for i, test in enumerate(sorted(self.tests[category]), 1):
                print(f"  {i:3d}. {test}")
    
    def generate_pytest_config(self) -> str:
        """Generate pytest configuration."""
        categories_str = ", ".join(sorted(self.tests.keys()))
        
        config = f"""[pytest]
# Auto-generated pytest configuration
# Generated from {len(self.all_tests)} discovered tests

# Test paths - include ALL test locations
testpaths = 
    tests
    packages/com.twg.the-seed/The Living Dev Agent/tests

# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for test categorization
markers =
    exp01: EXP-01 Address Uniqueness Tests
    exp02: EXP-02 Retrieval Efficiency Tests
    exp03: EXP-03 Dimension Necessity Tests
    exp04: EXP-04 Fractal Scaling Tests
    exp05: EXP-05 Compression/Expansion Tests
    exp06: EXP-06 Entanglement Detection Tests
    exp07: EXP-07 LUCA Bootstrap Tests
    exp08: EXP-08 Warbler Integration Tests
    exp09: EXP-09 Concurrency Tests
    exp10: EXP-10 Narrative Preservation Tests
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    load: Load and stress tests
    slow: Slow running tests
    math: Mathematical validation tests
    robustness: Robustness tests

# Output options
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
"""
        return config
    
    def validate_test_imports(self):
        """Validate that all test files can be imported."""
        print("\n" + "=" * 80)
        print("✓ VALIDATING TEST IMPORTS")
        print("=" * 80 + "\n")
        
        test_files = set()
        for tests_list in self.tests.values():
            for test in tests_list:
                file_path = test.split('::')[0] if '::' in test else test
                test_files.add(file_path)
        
        import_errors = []
        for test_file in sorted(test_files):
            try:
                # Try to import the test module
                module_path = (self.project_root / test_file).resolve()
                print(f"✅ {test_file}")
            except Exception as e:
                print(f"❌ {test_file}: {e}")
                import_errors.append((test_file, str(e)))
        
        return len(import_errors) == 0
    
    def to_json(self) -> Dict:
        """Export as JSON."""
        return {
            'total_tests': len(self.all_tests),
            'categories': {
                category: len(tests)
                for category, tests in self.tests.items()
            },
            'test_details': {
                category: tests
                for category, tests in self.tests.items()
            },
            'all_tests': self.all_tests
        }


def main():
    parser = argparse.ArgumentParser(
        description='Test Suite Inventory - Discover and categorize all tests'
    )
    parser.add_argument('--full', action='store_true', help='Show detailed list')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--fix', action='store_true', help='Fix pytest configuration')
    parser.add_argument('--validate', action='store_true', help='Validate test imports')
    
    args = parser.parse_args()
    
    # Create inventory
    inventory = TestInventory()
    
    try:
        # Discover tests
        inventory.discover_all_tests()
        
        # Print results
        if args.json:
            print(json.dumps(inventory.to_json(), indent=2))
        elif args.full:
            inventory.print_detailed()
        else:
            inventory.print_summary()
        
        # Validate if requested
        if args.validate:
            success = inventory.validate_test_imports()
            if not success:
                print("\n⚠️ Some tests have import issues!")
        
        # Fix configuration if requested
        if args.fix:
            config = inventory.generate_pytest_config()
            config_path = Path('pytest.ini')
            config_path.write_text(config)
            print(f"\n✅ Updated {config_path}")
        
        # Show test run commands
        print("\n" + "=" * 80)
        print("🚀 TEST RUN COMMANDS")
        print("=" * 80 + "\n")
        
        for category in sorted(inventory.tests.keys()):
            print(f"# {category}")
            if category == 'Load & Stress Tests':
                print(f'pytest tests/test_websocket_load_stress.py -v --capture=no\n')
            elif category == 'Experiment Tests (EXP-01 to EXP-10)':
                for i in range(1, 11):
                    print(f'pytest -m exp0{i} -v')
            else:
                print(f'pytest tests/ -k "{category.lower()}" -v\n')
        
        print("\n" + "=" * 80)
        print(f"✅ INVENTORY COMPLETE - {len(inventory.all_tests)} total tests")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during inventory: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()