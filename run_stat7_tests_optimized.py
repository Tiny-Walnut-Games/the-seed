#!/usr/bin/env python3
"""
Optimized STAT7 Test Runner
Runs optimized tests with better performance and parallel execution.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_optimized_tests():
    """Run optimized STAT7 tests with better performance."""
    print("🚀 Running Optimized STAT7 E2E Tests")
    print("=" * 50)

    test_file = Path(__file__).parent / "tests" / "test_stat7_e2e_optimized.py"

    if not test_file.exists():
        print(f"❌ Optimized test file not found: {test_file}")
        return False

    # Run with optimized pytest settings
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",  # Verbose output
        "--tb=short",  # Short tracebacks
        "-x",  # Stop on first failure
        "--disable-warnings",  # Disable warnings
        "-n", "auto",  # Auto-detect parallel workers
        "--dist=loadscope",  # Load balancing for parallel tests
    ]

    print(f"📝 Running: {' '.join(cmd)}")
    print()

    start_time = time.time()

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n⏱️ Test Duration: {duration:.2f} seconds")

        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
            return False

    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_original_tests():
    """Run original (slower) tests for comparison."""
    print("🐌 Running Original STAT7 E2E Tests (for comparison)")
    print("=" * 50)

    test_file = Path(__file__).parent / "tests" / "test_stat7_e2e.py"

    if not test_file.exists():
        print(f"❌ Original test file not found: {test_file}")
        return False

    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "-x",
        "--disable-warnings"
    ]

    print(f"📝 Running: {' '.join(cmd)}")
    print()

    start_time = time.time()

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n⏱️ Test Duration: {duration:.2f} seconds")

        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
            return False

    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Optimized STAT7 Test Runner')
    parser.add_argument(
        '--optimized',
        action='store_true',
        default=True,
        help='Run optimized tests (default)'
    )
    parser.add_argument(
        '--original',
        action='store_true',
        help='Run original tests for comparison'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Run both and compare performance'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run only fast unit tests (no browser)'
    )

    args = parser.parse_args()

    if args.compare:
        print("🔄 Running both test suites for comparison...")
        print()

        print("📊 Running OPTIMIZED tests first:")
        optimized_success = run_optimized_tests()
        optimized_time = time.time()

        print("\n" + "=" * 50)
        print("📊 Running ORIGINAL tests for comparison:")
        original_success = run_original_tests()
        original_time = time.time()

        print("\n" + "=" * 50)
        print("📈 COMPARISON RESULTS:")
        print(f"   Optimized: {'✅ PASS' if optimized_success else '❌ FAIL'}")
        print(f"   Original:  {'✅ PASS' if original_success else '❌ FAIL'}")

    elif args.original:
        run_original_tests()
    elif args.quick:
        # Run only fast tests without browser
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_stat7_e2e_optimized.py::TestStat7Performance",
            "-v",
            "--tb=short"
        ]
        print(f"📝 Running quick tests: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=Path(__file__).parent)
    else:
        run_optimized_tests()


if __name__ == "__main__":
    main()
