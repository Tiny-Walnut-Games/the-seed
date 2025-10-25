#!/usr/bin/env python3
"""
RAG Stress Test Runner

Executes comprehensive RAG system stress tests with configurable modes.

Usage:
    python scripts/run_rag_stress_test.py --quick    # Fast 30-second test
    python scripts/run_rag_stress_test.py --full     # Complete 5-10 minute test
    python scripts/run_rag_stress_test.py             # Default (full)
    
    # Via pytest
    pytest tests/stress/test_rag_stress_suite.py -v -s
    
    # Specific test
    pytest tests/stress/test_rag_stress_suite.py::TestRAGStress::test_embedding_generation_scale -v

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add project root to path
seed_root = Path(__file__).parent.parent
sys.path.insert(0, str(seed_root))
os.chdir(seed_root)

# Import the test module directly
test_module_path = seed_root / "tests" / "stress" / "test_rag_stress_suite.py"
spec = importlib.util.spec_from_file_location("test_rag_stress_suite", test_module_path)
test_module = importlib.util.module_from_spec(spec)
sys.modules["test_rag_stress_suite"] = test_module
spec.loader.exec_module(test_module)

run_quick_test = test_module.run_quick_test
run_full_test = test_module.run_full_test

if __name__ == "__main__":
    quick = "--quick" in sys.argv
    
    print("\n" + "=" * 70)
    print("RAG SYSTEM STRESS TEST")
    print("=" * 70)
    print(f"Mode: {'QUICK (30 sec)' if quick else 'FULL (5-10 min)'}")
    print(f"Data: Warbler packs (core, wisdom-scrolls, faction-politics)")
    print("=" * 70 + "\n")
    
    if quick:
        success = run_quick_test()
    else:
        success = run_full_test()
    
    print("\n" + "=" * 70)
    if success:
        print("RESULT: ✅ ALL TESTS PASSED")
    else:
        print("RESULT: ❌ TESTS FAILED")
    print("=" * 70)
    
    sys.exit(0 if success else 1)