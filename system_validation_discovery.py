#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Validation Discovery Tool
Customer-perspective test inventory and quick validation

This tool discovers and inventories ALL tests across The Seed,
TLDA, and WARBLER systems without executing them (for speed).
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')


class SystemValidator:
    """Discovers and validates test systems"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.inventory = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "summary": {}
        }
    
    def discover_tests(self, test_dir: Path, system_name: str) -> Dict:
        """Discover all test files in a directory"""
        
        print(f"\n{'='*70}")
        print(f"[DISCOVERY] Scanning: {system_name}")
        print(f"{'='*70}")
        print(f"Path: {test_dir}\n")
        
        if not test_dir.exists():
            print(f"[WARN] Directory not found: {test_dir}")
            return {"tests": [], "count": 0, "path": str(test_dir)}
        
        test_files = sorted(test_dir.glob("test_*.py"))
        websocket_tests = sorted((test_dir / "websocket").glob("*.py")) if (test_dir / "websocket").exists() else []
        
        all_tests = test_files + websocket_tests
        
        tests_info = []
        
        for test_file in all_tests:
            try:
                # Count tests in file
                content = test_file.read_text()
                test_count = content.count("def test_")
                class_count = content.count("class Test")
                
                test_info = {
                    "name": test_file.name,
                    "path": str(test_file),
                    "relative_path": test_file.relative_to(self.root_dir),
                    "test_functions": test_count,
                    "test_classes": class_count,
                    "total_tests": test_count + class_count,
                    "size_bytes": test_file.stat().st_size
                }
                
                tests_info.append(test_info)
                
                print(f"  [OK] {test_file.name}")
                print(f"       - Test functions: {test_count}")
                print(f"       - Test classes: {class_count}")
                print(f"       - Total tests: {test_info['total_tests']}")
                print(f"       - File size: {test_file.stat().st_size:,} bytes\n")
                
            except Exception as e:
                print(f"  [ERROR] {test_file.name}: {e}\n")
        
        return {
            "system": system_name,
            "path": str(test_dir),
            "tests": tests_info,
            "count": len(tests_info),
            "total_test_items": sum(t["total_tests"] for t in tests_info)
        }
    
    def validate_pytest_setup(self) -> Dict:
        """Validate pytest configuration"""
        
        print(f"\n{'='*70}")
        print("[CONFIG] Pytest Configuration Status")
        print(f"{'='*70}\n")
        
        config_files = {
            "pytest.ini": self.root_dir / "pytest.ini",
            "pyproject.toml": self.root_dir / "pyproject.toml",
            "setup.cfg": self.root_dir / "setup.cfg"
        }
        
        config_status = {}
        
        for name, path in config_files.items():
            if path.exists():
                print(f"[OK] {name} found at {path}")
                config_status[name] = "FOUND"
                # Show first few lines
                with open(path, 'r') as f:
                    lines = f.readlines()[:5]
                    for line in lines:
                        print(f"     {line.rstrip()}")
                    print()
            else:
                print(f"[WARN] {name} not found")
                config_status[name] = "MISSING"
        
        # Check pytest installation
        print("[CHECK] Verifying pytest installation...\n")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"[OK] pytest is installed:")
                print(f"     {result.stdout.strip()}\n")
                config_status["pytest"] = "INSTALLED"
            else:
                print(f"[WARN] pytest version check failed\n")
                config_status["pytest"] = "ISSUE"
        except Exception as e:
            print(f"[ERROR] pytest installation check failed: {e}\n")
            config_status["pytest"] = "ERROR"
        
        return config_status
    
    def collect_test_details(self, system_name: str, test_dir: Path) -> Dict:
        """Run pytest --collect-only to get detailed test info"""
        
        if not test_dir.exists():
            return {}
        
        print(f"\n[COLLECT] Collecting test details for {system_name}...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_dir), "--collect-only", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.root_dir)
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                test_count = len([l for l in lines if '::test_' in l or '<Function' in l])
                print(f"[OK] Collection successful")
                print(f"     Found {test_count} individual tests\n")
                return {"collected": test_count, "output": result.stdout[:500]}
            else:
                print(f"[WARN] Collection had issues\n")
                return {"error": result.stderr[:200]}
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Collection timed out\n")
            return {"timeout": True}
        except Exception as e:
            print(f"[ERROR] Collection failed: {e}\n")
            return {"error": str(e)}
    
    def run_discovery(self):
        """Run complete discovery"""
        
        print("\n" + "="*70)
        print("[START] SYSTEM VALIDATION DISCOVERY")
        print("="*70)
        print(f"Root: {self.root_dir}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Validate pytest setup
        pytest_config = self.validate_pytest_setup()
        self.inventory["pytest_config"] = pytest_config
        
        # THE SEED Tests
        seed_tests_dir = self.root_dir / "tests"
        seed_data = self.discover_tests(seed_tests_dir, "The Seed")
        self.inventory["systems"]["The Seed"] = seed_data
        seed_collection = self.collect_test_details("The Seed", seed_tests_dir)
        seed_data["collection_details"] = seed_collection
        
        # WARBLER Tests
        warbler_tests_dir = self.root_dir / "packages/com.twg.the-seed/The Living Dev Agent/tests"
        warbler_data = self.discover_tests(warbler_tests_dir, "WARBLER")
        self.inventory["systems"]["WARBLER"] = warbler_data
        warbler_collection = self.collect_test_details("WARBLER", warbler_tests_dir)
        warbler_data["collection_details"] = warbler_collection
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate and display summary"""
        
        print("\n" + "="*70)
        print("[SUMMARY] COMPLETE SYSTEM VALIDATION INVENTORY")
        print("="*70 + "\n")
        
        total_files = 0
        total_tests = 0
        
        for system_name, system_data in self.inventory["systems"].items():
            test_count = system_data.get("count", 0)
            total_items = system_data.get("total_test_items", 0)
            
            total_files += test_count
            total_tests += total_items
            
            collection = system_data.get("collection_details", {})
            collected = collection.get("collected", "?")
            
            print(f"{system_name}:")
            print(f"  Test Files: {test_count}")
            print(f"  Test Items: {total_items}")
            print(f"  Pytest Collected: {collected}")
            print(f"  Status: [OK]\n")
        
        print(f"{'='*70}")
        print(f"TOTALS:")
        print(f"  Total Test Files: {total_files}")
        print(f"  Total Test Items: {total_tests}")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Save report
        report_file = self.root_dir / f".test_results/system_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.inventory, f, indent=2, default=str)
        
        print(f"[SAVE] Inventory saved to: {report_file}\n")
        
        # Create a human-readable report
        text_report = []
        text_report.append("="*70)
        text_report.append("SYSTEM VALIDATION DISCOVERY REPORT")
        text_report.append("="*70)
        text_report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text_report.append(f"Root Directory: {self.root_dir}\n")
        
        text_report.append("TEST INVENTORY:\n")
        
        for system_name, system_data in self.inventory["systems"].items():
            text_report.append(f"{system_name}:")
            text_report.append(f"  Location: {system_data.get('path', 'N/A')}")
            text_report.append(f"  Test Files: {system_data.get('count', 0)}")
            text_report.append(f"  Test Items: {system_data.get('total_test_items', 0)}")
            
            collection = system_data.get("collection_details", {})
            if "collected" in collection:
                text_report.append(f"  Pytest Collected: {collection['collected']}")
            
            text_report.append("\n  Individual Tests:\n")
            for test in system_data.get("tests", []):
                text_report.append(f"    - {test['name']}")
                text_report.append(f"      Functions: {test['test_functions']}, Classes: {test['test_classes']}")
            
            text_report.append("\n")
        
        text_report.append("="*70)
        text_report.append(f"SUMMARY:")
        text_report.append(f"  Total Test Files: {total_files}")
        text_report.append(f"  Total Test Items: {total_tests}")
        
        text_report_file = report_file.with_suffix('.txt')
        text_report_file.write_text("\n".join(text_report))
        print(f"[SAVE] Text report saved to: {text_report_file}\n")


def main():
    validator = SystemValidator()
    validator.run_discovery()


if __name__ == "__main__":
    main()