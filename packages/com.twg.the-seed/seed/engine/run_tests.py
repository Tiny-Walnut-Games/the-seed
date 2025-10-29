#!/usr/bin/env python3
"""
Quick Test Runner for Seed Test Suite
Simple interface for common testing scenarios

Usage:
    python run_tests.py                    # Quick validation
    python run_tests.py --full             # Complete test suite
    python run_tests.py --gui              # PyTest mode for GUI
    python run_tests.py --report html      # Generate HTML report
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"🚀 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Quick Test Runner")
    parser.add_argument("--full", action="store_true", help="Run complete test suite")
    parser.add_argument("--gui", action="store_true", help="Run in PyTest mode (GUI compatible)")
    parser.add_argument("--report", choices=["json", "html", "markdown"],
                       default="json", help="Report format")
    parser.add_argument("--quick", action="store_true", help="Quick validation only")

    args = parser.parse_args()

    # Determine test mode
    if args.gui:
        # PyTest mode - compatible with Rider/PyCrunch
        cmd = [sys.executable, "-m", "pytest", "test_seed_pytest.py", "-v"]

        if not args.full:
            cmd.extend(["-m", "not slow"])

        if args.report == "html":
            cmd.extend(["--html=pytest_report.html", "--self-contained-html"])

        success = run_command(cmd, "PyTest Test Suite")

    else:
        # Unified test suite mode
        cmd = [sys.executable, "seed_test_suite.py"]

        if args.quick:
            cmd.append("--quick")
        elif not args.full:
            cmd.append("--quick")  # Default to quick

        cmd.extend(["--report", args.report])

        success = run_command(cmd, "Unified Test Suite")

    if success:
        print("\n🎉 All tests completed successfully!")

        # Show report location
        results_dir = Path("results")
        if results_dir.exists():
            latest_report = max(results_dir.glob("*"), key=lambda p: p.stat().st_mtime)
            print(f"📄 Latest report: {latest_report}")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
