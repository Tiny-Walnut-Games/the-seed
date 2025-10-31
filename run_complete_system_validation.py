#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete System Validation Runner
Customer-Perspective Test Execution with Real Metrics

This script runs ALL tests across The Seed, TLDA, and WARBLER systems,
providing comprehensive metrics and validation results.

Usage:
    python run_complete_system_validation.py              # Full validation
    python run_complete_system_validation.py --the-seed    # Only The Seed tests
    python run_complete_system_validation.py --warbler     # Only WARBLER tests
    python run_complete_system_validation.py --quick       # Quick validation (no slow tests)
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')


class TestRunner:
    """Manages execution of test suites with metrics collection"""
    
    def __init__(self, root_dir: Path, output_dir: Optional[Path] = None):
        self.root_dir = root_dir
        self.output_dir = output_dir or (root_dir / ".test_results")
        self.output_dir.mkdir(exist_ok=True)
        self.results: Dict = {
            "timestamp": datetime.now().isoformat(),
            "systems": {}
        }
        self.total_start_time = time.time()
        
    def run_test_suite(
        self,
        test_path: Path,
        suite_name: str,
        system_name: str,
        **pytest_args
    ) -> Dict:
        """Run a single pytest test suite and collect metrics"""
        
        print(f"\n{'='*70}")
        print(f"[TEST] Running: {suite_name}")
        print(f"   System: {system_name}")
        print(f"   Path: {test_path}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--co",  # Collect only first to show what tests exist
        ]
        
        # Add additional arguments
        for key, value in pytest_args.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            else:
                cmd.extend([f"--{key}", str(value)])
        
        result_data = {
            "name": suite_name,
            "system": system_name,
            "path": str(test_path),
            "status": "UNKNOWN",
            "duration": 0,
            "return_code": -1,
            "stdout": "",
            "stderr": "",
            "test_count": 0
        }
        
        try:
            # Run pytest with collection
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.root_dir)
            )
            
            stdout, stderr = process.communicate(timeout=120)
            end_time = time.time()
            
            result_data["return_code"] = process.returncode
            result_data["duration"] = end_time - start_time
            result_data["stdout"] = stdout
            result_data["stderr"] = stderr
            
            # Count tests from output
            test_count = stdout.count("<Function") + stdout.count("<Method")
            result_data["test_count"] = test_count
            
            if process.returncode == 0:
                result_data["status"] = "COLLECTED"
                print(f"[OK] Collected {test_count} tests in {result_data['duration']:.2f}s")
            else:
                result_data["status"] = "COLLECTION_FAILED"
                print(f"[WARN] Collection had issues (code {process.returncode})")
                if stderr:
                    print(f"   Error: {stderr[:200]}")
            
            # Now run the actual tests
            print(f"\n   Executing {test_count} tests...")
            cmd_exec = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=line",
                "--disable-warnings",
                "-q"
            ]
            
            exec_start = time.time()
            process_exec = subprocess.Popen(
                cmd_exec,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.root_dir)
            )
            
            stdout_exec, stderr_exec = process_exec.communicate(timeout=600)
            exec_duration = time.time() - exec_start
            
            result_data["return_code"] = process_exec.returncode
            result_data["duration"] = result_data["duration"] + exec_duration
            result_data["stdout"] = stdout_exec
            result_data["stderr"] = stderr_exec
            
            # Parse results
            if "passed" in stdout_exec:
                result_data["status"] = "PASSED"
                passed = stdout_exec.count(" passed")
                failed = stdout_exec.count(" failed")
                errors = stdout_exec.count(" error")
                print(f"[PASS] PASSED: {passed} tests passed in {exec_duration:.2f}s")
                if failed > 0:
                    print(f"[WARN] FAILED: {failed} tests failed")
                    result_data["status"] = "PARTIAL_PASS"
                if errors > 0:
                    print(f"[ERROR] ERRORS: {errors} tests had errors")
                    result_data["status"] = "ERRORS"
            else:
                result_data["status"] = "NO_TESTS"
                print(f"[INFO] No tests executed")
                
        except subprocess.TimeoutExpired:
            result_data["status"] = "TIMEOUT"
            result_data["duration"] = time.time() - start_time
            print(f"[TIMEOUT] Test suite timed out after {result_data['duration']:.2f}s")
        except Exception as e:
            result_data["status"] = "ERROR"
            result_data["duration"] = time.time() - start_time
            result_data["stderr"] = str(e)
            print(f"[ERROR] Error running test suite: {e}")
        
        return result_data
    
    def run_the_seed_tests(self, quick: bool = False) -> Dict:
        """Run all The Seed system tests"""
        print("\n" + "="*70)
        print("[SEED] THE SEED - Core Multidimensional System Tests")
        print("="*70)
        
        tests_dir = self.root_dir / "tests"
        suite_results = {}
        
        test_files = [
            ("test_stat7.py", "STAT7 Core System"),
            ("test_stat7_setup.py", "STAT7 Setup & Initialization"),
            ("test_stat7_files.py", "STAT7 File I/O"),
            ("test_stat7_server.py", "STAT7 Server"),
            ("test_stat7_e2e.py", "STAT7 E2E (Original)"),
            ("test_stat7_e2e_optimized.py", "STAT7 E2E (Optimized)"),
            ("test_simple.py", "Simple Unit Tests"),
            ("test_event_store.py", "Event Store"),
            ("test_server_data.py", "Server Data"),
            ("test_tick_engine.py", "Tick Engine"),
            ("test_api_contract.py", "API Contract"),
            ("test_e2e_scenarios.py", "E2E Scenarios"),
            ("test_complete_system.py", "Complete System Integration"),
            ("test_enhanced_visualization.py", "Enhanced Visualization"),
            ("test_governance_integration.py", "Governance Integration"),
            ("test_websocket_load_stress.py", "WebSocket Load/Stress"),
        ]
        
        if quick:
            # Only run non-slow tests
            test_files = [t for t in test_files if "stress" not in t[1].lower() and "load" not in t[1].lower()]
        
        for test_file, test_name in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                result = self.run_test_suite(
                    test_path,
                    test_name,
                    "The Seed"
                )
                suite_results[test_name] = result
            else:
                print(f"[WARN] Test file not found: {test_path}")
        
        return suite_results
    
    def run_warbler_tests(self, quick: bool = False) -> Dict:
        """Run all WARBLER system tests"""
        print("\n" + "="*70)
        print("[WARBLER] WARBLER - Living Dev Agent Tests")
        print("="*70)
        
        tests_dir = self.root_dir / "packages/com.twg.the-seed/The Living Dev Agent/tests"
        suite_results = {}
        
        test_files = [
            ("test_selfcare_system.py", "SelfCare System"),
            ("test_conservator.py", "Conservator"),
            ("test_dtt_vault.py", "DevTimeTravel Vault"),
            ("test_plugin_system.py", "Plugin System"),
            ("test_example_plugins.py", "Example Plugins"),
            ("test_template_system.py", "Template System"),
            ("test_wfc_firewall.py", "WFC Firewall"),
            ("test_wfc_integration.py", "WFC Integration"),
            ("test_badge_pet_system.py", "Badge Pet System"),
            ("test_privacy_hooks.py", "Privacy Hooks"),
            ("test_semantic_anchors.py", "Semantic Anchors"),
            ("test_claims_classification.py", "Claims Classification"),
            ("test_exp06_robustness.py", "EXP-06 Robustness"),
            ("test_exp06_entanglement_math.py", "EXP-06 Entanglement Math"),
            ("test_exp06_simple_validation.py", "EXP-06 Simple Validation"),
            ("test_exp06_final_validation.py", "EXP-06 Final Validation"),
            ("test_warbler_quote_integration.py", "Warbler Quote Integration"),
            ("test_behavioral_alignment.py", "Behavioral Alignment"),
            ("test_phase2_stat7_integration.py", "Phase2 STAT7 Integration"),
            ("test_companion_battle_system.py", "Companion Battle System"),
            ("test_baseline_set_validation.py", "Baseline Set Validation"),
            ("test_alchemist_report_synthesizer.py", "Alchemist Report Synthesizer"),
            ("test_geo_thermal_scaffold.py", "Geo Thermal Scaffold"),
            ("test_safety_policy_transparency.py", "Safety Policy Transparency"),
            ("test_recovery_gate_phase1.py", "Recovery Gate Phase1"),
        ]
        
        if quick:
            # Only run fast core tests
            test_files = [t for t in test_files if any(
                fast_keyword in t[1].lower() 
                for fast_keyword in ["simple", "unit", "system", "integration"]
            )]
        
        for test_file, test_name in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                result = self.run_test_suite(
                    test_path,
                    test_name,
                    "WARBLER"
                )
                suite_results[test_name] = result
            else:
                print(f"[WARN] Test file not found: {test_path}")
        
        return suite_results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.total_start_time
        
        report = []
        report.append("\n" + "="*70)
        report.append("[REPORT] COMPREHENSIVE SYSTEM VALIDATION REPORT")
        report.append("="*70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Duration: {total_duration:.2f} seconds")
        report.append("")
        
        # Summary by system
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for system_name, suite_results in self.results["systems"].items():
            report.append(f"\n{'─'*70}")
            report.append(f"System: {system_name}")
            report.append(f"{'─'*70}")
            
            system_tests = 0
            system_passed = 0
            system_failed = 0
            system_errors = 0
            system_duration = 0
            
            for suite_name, result in suite_results.items():
                system_tests += result.get("test_count", 0)
                system_duration += result.get("duration", 0)
                
                status = result.get("status", "UNKNOWN")
                icon = {
                    "PASSED": "[PASS]",
                    "PARTIAL_PASS": "[WARN]",
                    "ERRORS": "[ERROR]",
                    "TIMEOUT": "[TIMEOUT]",
                    "ERROR": "[ERROR]",
                    "NO_TESTS": "[INFO]",
                    "COLLECTION_FAILED": "[WARN]"
                }.get(status, "[?]")
                
                report.append(f"{icon} {suite_name}: {status}")
                report.append(f"   Tests: {result.get('test_count', 0)}")
                report.append(f"   Duration: {result.get('duration', 0):.2f}s")
                
                if result.get("stderr"):
                    report.append(f"   Error: {result['stderr'][:100]}")
            
            report.append(f"\n{system_name} Summary:")
            report.append(f"  Total Tests: {system_tests}")
            report.append(f"  Duration: {system_duration:.2f}s")
            
            total_tests += system_tests
            
        report.append(f"\n{'='*70}")
        report.append("OVERALL RESULTS")
        report.append(f"{'='*70}")
        report.append(f"Total Tests Collected: {total_tests}")
        report.append(f"Total Duration: {total_duration:.2f} seconds")
        report.append(f"Average Time per Test Suite: {total_duration / max(len(self.results['systems']), 1):.2f}s")
        
        return "\n".join(report)
    
    def run_all(self, quick: bool = False, systems: Optional[List[str]] = None):
        """Run all test suites"""
        if systems is None or "the-seed" in systems:
            self.results["systems"]["The Seed"] = self.run_the_seed_tests(quick=quick)
        
        if systems is None or "warbler" in systems:
            self.results["systems"]["WARBLER"] = self.run_warbler_tests(quick=quick)
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save report
        report_file = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.write_text(report)
        print(f"\n[SAVE] Report saved to: {report_file}")
        
        # Save JSON results
        json_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"[SAVE] JSON results saved to: {json_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Complete System Validation Runner"
    )
    parser.add_argument(
        "--the-seed",
        action="store_true",
        help="Run only The Seed tests"
    )
    parser.add_argument(
        "--warbler",
        action="store_true",
        help="Run only WARBLER tests"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick validation (skip slow tests)"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent
    runner = TestRunner(root_dir)
    
    systems = []
    if args.the_seed:
        systems.append("the-seed")
    if args.warbler:
        systems.append("warbler")
    
    runner.run_all(
        quick=args.quick,
        systems=systems if systems else None
    )


if __name__ == "__main__":
    main()