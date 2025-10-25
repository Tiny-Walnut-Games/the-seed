#!/usr/bin/env python3
"""
STAT7 Stress Test Runner

Usage:
    python run_stress_test.py --quick    # Fast 30-second test
    python run_stress_test.py --full     # Complete 3-5 minute test
    python run_stress_test.py             # Default (full)
"""

import sys
import os

# Add seed engine to path
seed_engine_path = os.path.join(os.path.dirname(__file__), '..', 'seed', 'engine')
sys.path.insert(0, seed_engine_path)

from stat7_stress_test import run_full_stress_test

if __name__ == "__main__":
    quick = "--quick" in sys.argv
    run_full_stress_test(quick=quick)