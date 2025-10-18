#!/usr/bin/env python3
"""
Runner for Phase 2 Validation Experiments (EXP-04+)

Phase 2 focuses on:
- EXP-04: Fractal Scaling (STAT7 consistency across 1K-1M scales)
- Potential future: EXP-05, EXP-06, etc.

Usage:
    python run_exp_phase2.py              # Run quick mode (1K, 10K, 100K)
    python run_exp_phase2.py --full       # Run full mode (1K, 10K, 100K, 1M)
    python run_exp_phase2.py --exp 04     # Run specific experiment
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# Add seed/engine to path
engine_path = Path(__file__).parent.parent / "seed" / "engine"
sys.path.insert(0, str(engine_path))

from exp04_fractal_scaling import run_fractal_scaling_test, save_results


def main():
    """Run Phase 2 experiments."""
    
    # Parse arguments
    quick_mode = '--full' not in sys.argv
    exp_number = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('--exp'):
            parts = arg.split('=')
            if len(parts) == 2:
                exp_number = parts[1]
    
    print("\n" + "=" * 70)
    print("PHASE 2 VALIDATION EXPERIMENTS")
    print("=" * 70)
    print(f"Mode: {'Quick (1K, 10K, 100K)' if quick_mode else 'Full (1K, 10K, 100K, 1M)'}")
    print(f"Starting at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # Run EXP-04
    if exp_number is None or exp_number == '04':
        print("Running EXP-04: Fractal Scaling...")
        print()
        
        results = run_fractal_scaling_test(quick_mode=quick_mode)
        
        # Save results in seed/engine directory for consistency
        output_dir = Path(__file__).parent.parent / "seed" / "engine" / "results"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"exp04_fractal_scaling_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        all_valid = all(r.is_valid() for r in results.scale_results)
        print(f"Status: {'✓ PASSED' if all_valid else '✗ FAILED'}")
        print(f"Scales tested: {len(results.scale_results)}")
        print(f"Is Fractal: {results.is_fractal}")
        
        for r in results.scale_results:
            print(f"  {r.scale:,}: {r.collision_count} collisions, {r.retrieval_mean_ms:.6f}ms mean latency")
        
        print()
        
        if not all_valid:
            sys.exit(1)
    
    else:
        print(f"Unknown experiment: {exp_number}")
        sys.exit(1)


if __name__ == '__main__':
    main()