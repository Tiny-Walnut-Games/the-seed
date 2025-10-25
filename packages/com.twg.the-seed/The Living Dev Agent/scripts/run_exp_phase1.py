#!/usr/bin/env python3
"""
Quick runner for Phase 1 validation experiments.

Usage:
    python run_exp_phase1.py              # Run with defaults
    python run_exp_phase1.py --quick      # Run with small scale for quick testing
    python run_exp_phase1.py --full       # Run full scale validation
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add seed engine to path
seed_engine_path = Path(__file__).parent.parent / 'seed' / 'engine'
sys.path.insert(0, str(seed_engine_path))

from stat7_experiments import run_all_experiments


def main():
    parser = argparse.ArgumentParser(
        description='Run Phase 1 validation experiments (EXP-01, EXP-02, EXP-03)'
    )
    parser.add_argument('--quick', action='store_true',
                       help='Quick run with small sample sizes (fast)')
    parser.add_argument('--full', action='store_true',
                       help='Full validation with large sample sizes')
    parser.add_argument('--exp01-samples', type=int, default=1000,
                       help='Sample size for EXP-01 (default: 1000)')
    parser.add_argument('--exp01-iterations', type=int, default=10,
                       help='Iterations for EXP-01 (default: 10)')
    parser.add_argument('--exp02-queries', type=int, default=1000,
                       help='Queries for EXP-02 (default: 1000)')
    parser.add_argument('--exp03-samples', type=int, default=1000,
                       help='Sample size for EXP-03 (default: 1000)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file for results (default: VALIDATION_RESULTS_<timestamp>.json)')
    
    args = parser.parse_args()
    
    # Set scale based on flags
    if args.quick:
        exp01_samples = 100
        exp01_iterations = 3
        exp02_queries = 100
        exp03_samples = 100
        print("⚡ Quick mode: small sample sizes for rapid testing")
    elif args.full:
        exp01_samples = 10000
        exp01_iterations = 20
        exp02_queries = 5000
        exp03_samples = 10000
        print("🔬 Full mode: large sample sizes for comprehensive validation")
    else:
        exp01_samples = args.exp01_samples
        exp01_iterations = args.exp01_iterations
        exp02_queries = args.exp02_queries
        exp03_samples = args.exp03_samples
        print("📊 Default mode: standard validation scale")
    
    print(f"\n📝 Configuration:")
    print(f"   EXP-01: {exp01_samples} samples × {exp01_iterations} iterations")
    print(f"   EXP-02: {exp02_queries} queries per scale")
    print(f"   EXP-03: {exp03_samples} samples")
    
    # Run experiments
    print(f"\n🚀 Starting Phase 1 validation experiments...\n")
    start_time = datetime.now()
    results = run_all_experiments(
        exp01_samples=exp01_samples,
        exp01_iterations=exp01_iterations,
        exp02_queries=exp02_queries,
        exp03_samples=exp03_samples,
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n⏱️  Total time: {elapsed:.2f} seconds")
    
    # Save results
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'VALIDATION_RESULTS_{timestamp}.json'
    else:
        output_file = args.output
    
    output_path = Path(output_file)
    
    # Add metadata
    results['metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'elapsed_seconds': elapsed,
        'phase': 'Phase 1 Doctrine',
        'status': 'PASSED' if all(r['success'] for r in results.values()) else 'FAILED',
        'exp01_samples': exp01_samples,
        'exp01_iterations': exp01_iterations,
        'exp02_queries': exp02_queries,
        'exp03_samples': exp03_samples,
    }
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"FINAL STATUS")
    print(f"{'='*70}")
    
    for exp in ['EXP-01', 'EXP-02', 'EXP-03']:
        status = '✅ PASS' if results[exp]['success'] else '❌ FAIL'
        print(f"{exp}: {status}")
    
    overall = all(r['success'] for r in [results['EXP-01'], results['EXP-02'], results['EXP-03']])
    print(f"\n🎯 Phase 1 Ready: {'✅ YES' if overall else '❌ NO'}")
    
    return 0 if overall else 1


if __name__ == '__main__':
    sys.exit(main())