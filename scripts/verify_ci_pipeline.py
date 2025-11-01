#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI Pipeline Verification Script
================================

Validates that your comprehensive test discovery pipeline is properly configured.

Usage:
    python verify_ci_pipeline.py          # Full verification
    python verify_ci_pipeline.py --quick  # Quick check
    python verify_ci_pipeline.py --fix    # Auto-fix issues
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Enable UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class PipelineVerifier:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.issues = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_failed = 0
    
    @staticmethod
    def _find_project_root() -> Path:
        """Find the project root by looking for marker files."""
        current = Path.cwd()
        
        # Look for marker files that indicate project root
        markers = ['pytest.ini', 'pyproject.toml', '.git', 'the-seed.sln', 'packages']
        
        # Search up the directory tree
        for _ in range(10):  # Limit search depth
            if any((current / marker).exists() for marker in markers):
                return current
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        # If no markers found, return cwd
        return Path.cwd()
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("\n" + "=" * 80)
        print("🔍 CI PIPELINE VERIFICATION")
        print("=" * 80)
        print(f"\n📁 Project Root: {self.project_root}\n")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("pytest Installation", self.check_pytest_installed),
            ("pytest Configuration", self.check_pytest_config),
            ("Test Paths Accessible", self.check_test_paths),
            ("Test Discovery", self.check_test_discovery),
            ("GitHub Actions Workflows", self.check_workflows),
            ("Dependencies", self.check_dependencies),
            ("Test Markers", self.check_markers),
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}...", end=" ")
            try:
                result = check_func()
                if result:
                    print("✅")
                    self.checks_passed += 1
                else:
                    print("❌")
                    self.checks_failed += 1
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.checks_failed += 1
                self.issues.append((check_name, str(e)))
        
        return self.print_summary()
    
    def check_python_version(self) -> bool:
        """Verify Python 3.9+ is installed."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            print(f"Python {version.major}.{version.minor}")
            return True
        else:
            self.issues.append(("Python Version", f"Need 3.9+, got {version.major}.{version.minor}"))
            return False
    
    def check_pytest_installed(self) -> bool:
        """Verify pytest is installed."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(version)
                return True
            else:
                self.issues.append(("pytest", "Not properly installed"))
                return False
        except Exception as e:
            self.issues.append(("pytest", str(e)))
            return False
    
    def check_pytest_config(self) -> bool:
        """Verify pytest.ini is properly configured."""
        pytest_ini = self.project_root / 'pytest.ini'
        if not pytest_ini.exists():
            self.issues.append(("pytest.ini", "File not found"))
            return False
        
        content = pytest_ini.read_text()
        
        # Check for required sections
        required = ['testpaths', 'python_files', 'markers']
        for req in required:
            if req not in content:
                self.warnings.append(f"pytest.ini missing '{req}' section")
        
        # Check for Living Dev Agent path (check for the escaped version)
        if 'Living' not in content or 'Agent' not in content:
            self.warnings.append("pytest.ini may not include Living Dev Agent tests")
        
        print("OK")
        return True
    
    def check_test_paths(self) -> bool:
        """Verify test directories exist and are accessible."""
        paths = [
            self.project_root / 'tests',
            self.project_root / 'packages' / 'com.twg.the-seed' / 'The Living Dev Agent' / 'tests'
        ]
        
        all_exist = True
        for path in paths:
            rel_path = path.relative_to(self.project_root)
            if path.exists():
                test_files = list(path.glob('test_*.py'))
                print(f"\n    ✓ {rel_path}: {len(test_files)} test files")
            else:
                print(f"\n    ❌ {rel_path}: NOT FOUND")
                print(f"       Checked: {path}")
                # Check if parent exists
                if path.parent.exists():
                    print(f"       Parent exists with: {[d.name for d in path.parent.iterdir() if d.is_dir()][:5]}")
                all_exist = False
        
        return all_exist
    
    def check_test_discovery(self) -> bool:
        """Run pytest discovery to find all tests."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Look for the "collected N items" line
            output_lines = result.stdout.split('\n')
            collected_line = next((line for line in output_lines if 'collected' in line), None)
            
            count = 0
            if collected_line:
                try:
                    # Extract number from "collected 171 items"
                    count = int(collected_line.split('collected')[1].split('item')[0].strip())
                except (ValueError, IndexError):
                    pass
            
            # Also count test markers
            tests = [line for line in output_lines if '::test_' in line or '<Function test_' in line]
            
            if count > 0 or len(tests) > 0:
                final_count = max(count, len(tests))
                print(f"{final_count} tests discovered")
                
                if final_count >= 30:  # Expect at least 30 tests
                    return True
                else:
                    self.warnings.append(f"Only found {final_count} tests, expected 40+")
                    return True  # Still pass but warn
            else:
                self.issues.append(("Test Discovery", "No tests found - check pytest.ini"))
                return False
        
        except subprocess.TimeoutExpired:
            self.issues.append(("Test Discovery", "Timeout during discovery"))
            return False
        except Exception as e:
            self.issues.append(("Test Discovery", str(e)))
            return False
    
    def check_workflows(self) -> bool:
        """Verify GitHub Actions workflows exist."""
        workflows_dir = self.project_root / '.github' / 'workflows'
        
        required_workflows = [
            'comprehensive-test-suite.yml',
            'mmo-load-test-validation.yml'
        ]
        
        all_exist = True
        for workflow in required_workflows:
            workflow_path = workflows_dir / workflow
            if workflow_path.exists():
                print(f"\n    ✓ {workflow}")
            else:
                print(f"\n    ❌ {workflow}: NOT FOUND")
                all_exist = False
        
        return all_exist
    
    def check_dependencies(self) -> bool:
        """Verify required test dependencies are installed."""
        packages = [
            'pytest',
            'pytest-cov',
            'pytest-xdist',
            'pytest-asyncio'
        ]
        
        missing = []
        for package in packages:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                missing.append(package)
        
        if missing:
            print(f"\n    Missing: {', '.join(missing)}")
            self.warnings.append(f"Missing packages: {', '.join(missing)}")
            print(f"\n    Install with: pip install {' '.join(missing)}")
            return False
        else:
            print("All required packages installed")
            return True
    
    def check_markers(self) -> bool:
        """Verify test markers are properly defined."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--markers'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            markers_found = result.stdout.count('mark.')
            print(f"{markers_found} markers defined")
            
            # Check for key markers
            key_markers = ['exp01', 'integration', 'load', 'slow']
            for marker in key_markers:
                if marker in result.stdout:
                    print(f"    ✓ {marker}")
                else:
                    print(f"    ❌ {marker} not defined")
                    self.warnings.append(f"Marker '{marker}' not defined")
            
            return markers_found > 0
        
        except Exception as e:
            self.issues.append(("Markers", str(e)))
            return False
    
    def print_summary(self) -> bool:
        """Print verification summary."""
        total = self.checks_passed + self.checks_failed
        success_rate = (self.checks_passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Passed: {self.checks_passed}/{total} ({success_rate:.0f}%)")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.issues:
            print(f"\n❌ Issues ({len(self.issues)}):")
            for check_name, error in self.issues:
                print(f"   • {check_name}: {error}")
        
        success = self.checks_failed == 0
        
        if success:
            print("\n" + "=" * 80)
            print("✅ PIPELINE VERIFICATION PASSED")
            print("=" * 80)
            print("\n🚀 Your CI/CD pipeline is ready!")
            print("\nNext steps:")
            print("  1. Push to main/develop to trigger comprehensive-test-suite workflow")
            print("  2. Check Actions tab for results")
            print("  3. Review aggregated test report")
        else:
            print("\n" + "=" * 80)
            print("❌ PIPELINE VERIFICATION FAILED")
            print("=" * 80)
            print("\n🔧 Please fix the issues above and try again")
        
        return success
    
    def print_report(self) -> Dict:
        """Generate JSON report."""
        return {
            'timestamp': None,
            'checks_passed': self.checks_passed,
            'checks_failed': self.checks_failed,
            'total_checks': self.checks_passed + self.checks_failed,
            'success_rate': f"{(self.checks_passed / (self.checks_passed + self.checks_failed) * 100):.1f}%" if (self.checks_passed + self.checks_failed) > 0 else "0%",
            'warnings': self.warnings,
            'issues': [{'check': name, 'error': error} for name, error in self.issues],
            'status': 'PASS' if self.checks_failed == 0 else 'FAIL'
        }


def main():
    parser = argparse.ArgumentParser(description='Verify CI Pipeline Configuration')
    parser.add_argument('--quick', action='store_true', help='Quick verification only')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--json', action='store_true', help='Output JSON report')
    
    args = parser.parse_args()
    
    verifier = PipelineVerifier()
    
    # Run verification
    success = verifier.run_all_checks()
    
    # Output JSON if requested
    if args.json:
        report = verifier.print_report()
        print(json.dumps(report, indent=2))
    
    # Try to auto-fix if requested
    if args.fix and not success:
        print("\n🔧 Attempting to auto-fix issues...")
        
        # Install missing dependencies
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-q',
             'pytest', 'pytest-cov', 'pytest-xdist', 'pytest-asyncio'],
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Installed missing dependencies")
        
        # Re-verify
        print("\n🔄 Re-verifying...")
        verifier = PipelineVerifier()
        success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()