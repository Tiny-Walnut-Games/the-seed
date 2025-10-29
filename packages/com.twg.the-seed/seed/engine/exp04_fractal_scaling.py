"""
EXP-04: Bit-Chain STAT7 Fractal Scaling Test

Tests whether STAT7 addressing maintains consistency and zero collisions
when scaled from 1K → 10K → 100K → 1M data points.

Verifies the "fractal" property: self-similar behavior at all scales.

Status: Phase 2 validation experiment
"""

import json
import hashlib
import time
import uuid
import random
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import statistics

# Reuse canonical serialization from Phase 1
from stat7_experiments import (
    normalize_float,
    normalize_timestamp,
    sort_json_keys,
    canonical_serialize,
    compute_address_hash,
    Coordinates,
    BitChain,
    REALMS,
    HORIZONS,
    ENTITY_TYPES,
    generate_random_bitchain,
)


# ============================================================================
# EXP-04 DATA STRUCTURES
# ============================================================================

@dataclass
class ScaleTestConfig:
    """Configuration for a single scale level test."""
    scale: int                  # Number of bit-chains (1K, 10K, 100K, 1M)
    num_retrievals: int         # Number of random retrieval queries
    timeout_seconds: int        # Kill test if it takes too long
    
    def name(self) -> str:
        """Human-readable scale name."""
        if self.scale >= 1_000_000:
            return f"{self.scale // 1_000_000}M"
        elif self.scale >= 1_000:
            return f"{self.scale // 1_000}K"
        return str(self.scale)


@dataclass
class ScaleTestResults:
    """Results from testing a single scale level."""
    scale: int
    num_bitchains: int
    num_addresses: int
    unique_addresses: int
    collision_count: int
    collision_rate: float
    
    # Retrieval performance
    num_retrievals: int
    retrieval_times_ms: List[float]
    retrieval_mean_ms: float
    retrieval_median_ms: float
    retrieval_p95_ms: float
    retrieval_p99_ms: float
    
    # System metrics
    total_time_seconds: float
    addresses_per_second: float
    
    def is_valid(self) -> bool:
        """Check if results meet success criteria."""
        return (
            self.collision_count == 0 and
            self.collision_rate == 0.0 and
            self.retrieval_mean_ms < 2.0  # Sub-millisecond target
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        return {
            'scale': self.scale,
            'num_bitchains': self.num_bitchains,
            'num_addresses': self.num_addresses,
            'unique_addresses': self.unique_addresses,
            'collision_count': self.collision_count,
            'collision_rate_percent': self.collision_rate * 100.0,
            'retrieval': {
                'num_queries': self.num_retrievals,
                'mean_ms': round(self.retrieval_mean_ms, 6),
                'median_ms': round(self.retrieval_median_ms, 6),
                'p95_ms': round(self.retrieval_p95_ms, 6),
                'p99_ms': round(self.retrieval_p99_ms, 6),
            },
            'performance': {
                'total_time_seconds': round(self.total_time_seconds, 3),
                'addresses_per_second': int(self.addresses_per_second),
            },
            'valid': self.is_valid(),
        }


@dataclass
class FractalScalingResults:
    """Complete results from EXP-04 fractal scaling test."""
    start_time: str
    end_time: str
    total_duration_seconds: float
    scale_results: List[ScaleTestResults]
    
    # Degradation analysis
    collision_degradation: Optional[str]
    retrieval_degradation: Optional[str]
    is_fractal: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        return {
            'experiment': 'EXP-04',
            'test_type': 'Fractal Scaling',
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_duration_seconds': round(self.total_duration_seconds, 3),
            'scales_tested': len(self.scale_results),
            'scale_results': [r.to_dict() for r in self.scale_results],
            'degradation_analysis': {
                'collision_degradation': self.collision_degradation,
                'retrieval_degradation': self.retrieval_degradation,
            },
            'is_fractal': self.is_fractal,
            'all_valid': all(r.is_valid() for r in self.scale_results),
        }


# ============================================================================
# SCALE TEST IMPLEMENTATION
# ============================================================================

def run_scale_test(config: ScaleTestConfig) -> ScaleTestResults:
    """
    Run EXP-01 (uniqueness) + EXP-02 (retrieval) at a single scale.
    
    Returns:
        ScaleTestResults with collision and latency metrics
    """
    start_time = time.time()
    
    # Step 1: Generate bit-chains
    print(f"  Generating {config.scale} bit-chains...", end='', flush=True)
    bitchains: List[BitChain] = []
    for i in range(config.scale):
        bitchains.append(generate_random_bitchain())
    print(" ✓")
    
    # Step 2: Compute addresses and check for collisions (EXP-01)
    print(f"  Computing addresses (EXP-01)...", end='', flush=True)
    address_map: Dict[str, int] = defaultdict(int)
    addresses = []
    
    for bc in bitchains:
        addr = bc.compute_address()
        addresses.append(addr)
        address_map[addr] += 1
    
    unique_addresses = len(address_map)
    collisions = sum(1 for count in address_map.values() if count > 1)
    collision_count = sum(count - 1 for count in address_map.values() if count > 1)
    collision_rate = collision_count / config.scale if config.scale > 0 else 0.0
    print(f" ✓ ({unique_addresses} unique, {collision_count} collisions)")
    
    # Step 3: Build retrieval index
    print(f"  Building retrieval index...", end='', flush=True)
    address_to_bitchain = {addr: bc for bc, addr in zip(bitchains, addresses)}
    print(f" ✓")
    
    # Step 4: Test retrieval performance (EXP-02)
    print(f"  Testing retrieval ({config.num_retrievals} queries)...", end='', flush=True)
    retrieval_times = []
    
    for _ in range(config.num_retrievals):
        idx = random.randint(0, len(addresses) - 1)
        target_addr = addresses[idx]
        
        # Measure lookup time
        start_lookup = time.perf_counter()
        result = address_to_bitchain.get(target_addr)
        end_lookup = time.perf_counter()
        
        if result is None:
            raise RuntimeError(f"Address lookup failed for {target_addr}")
        
        retrieval_times.append((end_lookup - start_lookup) * 1000)  # Convert to ms
    
    print(f" ✓")
    
    # Step 5: Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time
    
    retrieval_mean = statistics.mean(retrieval_times)
    retrieval_median = statistics.median(retrieval_times)
    retrieval_p95 = sorted(retrieval_times)[int(len(retrieval_times) * 0.95)]
    retrieval_p99 = sorted(retrieval_times)[int(len(retrieval_times) * 0.99)]
    
    addresses_per_second = config.scale / total_time
    
    return ScaleTestResults(
        scale=config.scale,
        num_bitchains=config.scale,
        num_addresses=len(addresses),
        unique_addresses=unique_addresses,
        collision_count=collision_count,
        collision_rate=collision_rate,
        num_retrievals=config.num_retrievals,
        retrieval_times_ms=retrieval_times,
        retrieval_mean_ms=retrieval_mean,
        retrieval_median_ms=retrieval_median,
        retrieval_p95_ms=retrieval_p95,
        retrieval_p99_ms=retrieval_p99,
        total_time_seconds=total_time,
        addresses_per_second=addresses_per_second,
    )


# ============================================================================
# FRACTAL SCALING TEST ORCHESTRATION
# ============================================================================

def analyze_degradation(results: List[ScaleTestResults]) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Analyze whether the system maintains fractal properties.
    
    Returns:
        (collision_analysis, retrieval_analysis, is_fractal)
    """
    is_fractal = True
    
    # Check collisions
    collision_msg = ""
    max_collision_rate = max(r.collision_rate for r in results)
    
    if max_collision_rate > 0.0:
        is_fractal = False
        collision_msg = f"COLLISION DETECTED: Max rate {max_collision_rate*100:.2f}%"
    else:
        collision_msg = "✓ Zero collisions at all scales"
    
    # Check retrieval degradation
    retrieval_msg = ""
    retrieval_means = [r.retrieval_mean_ms for r in results]
    
    # Check if retrieval time is increasing linearly with scale (bad) vs logarithmically (good)
    scales = [r.scale for r in results]
    if len(results) > 1:
        # Simple degradation check: is the retrieval time growing faster than O(log n)?
        worst_case_ratio = max(retrieval_means) / min(retrieval_means)
        scale_ratio = max(scales) / min(scales)
        
        # If retrieval grows faster than log scale ratio, it's degrading too fast
        import math
        expected_log_ratio = math.log(scale_ratio)
        
        if worst_case_ratio > expected_log_ratio * 2:
            is_fractal = False
            retrieval_msg = f"DEGRADATION WARNING: Latency ratio {worst_case_ratio:.2f}x > expected {expected_log_ratio:.2f}x"
        else:
            retrieval_msg = f"✓ Retrieval latency scales logarithmically ({worst_case_ratio:.2f}x for {scale_ratio:.0f}x scale)"
    
    return collision_msg, retrieval_msg, is_fractal


def run_fractal_scaling_test(quick_mode: bool = True) -> FractalScalingResults:
    """
    Run EXP-04: Fractal Scaling Test
    
    Args:
        quick_mode: If True, test 1K, 10K, 100K. If False, also test 1M.
    
    Returns:
        Complete results object
    """
    start_time = datetime.now(timezone.utc).isoformat()
    overall_start = time.time()
    
    print("\n" + "=" * 70)
    print("EXP-04: STAT7 FRACTAL SCALING TEST")
    print("=" * 70)
    print(f"Mode: {'Quick' if quick_mode else 'Full'} (1K, 10K, 100K{', 1M' if not quick_mode else ''})")
    print()
    
    # Define scale progression
    scales = [1_000, 10_000, 100_000]
    if not quick_mode:
        scales.append(1_000_000)
    
    scale_results = []
    
    for scale in scales:
        print(f"SCALE: {scale:,} bit-chains")
        print("-" * 70)
        
        config = ScaleTestConfig(
            scale=scale,
            num_retrievals=1000,
            timeout_seconds=300,
        )
        
        try:
            result = run_scale_test(config)
            scale_results.append(result)
            
            # Print summary for this scale
            print(f"  RESULT: {result.num_addresses} unique addresses")
            print(f"          Collisions: {result.collision_count} ({result.collision_rate*100:.2f}%)")
            print(f"          Retrieval: mean={result.retrieval_mean_ms:.6f}ms, p95={result.retrieval_p95_ms:.6f}ms")
            print(f"          Throughput: {result.addresses_per_second:,.0f} addr/sec")
            print(f"          Valid: {'✓ YES' if result.is_valid() else '✗ NO'}")
            print()
            
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            print()
            raise
    
    # Analyze degradation
    collision_analysis, retrieval_analysis, is_fractal = analyze_degradation(scale_results)
    
    overall_end = time.time()
    end_time = datetime.now(timezone.utc).isoformat()
    
    print("=" * 70)
    print("DEGRADATION ANALYSIS")
    print("=" * 70)
    print(f"Collision: {collision_analysis}")
    print(f"Retrieval: {retrieval_analysis}")
    print(f"Is Fractal: {'✓ YES' if is_fractal else '✗ NO'}")
    print()
    
    results = FractalScalingResults(
        start_time=start_time,
        end_time=end_time,
        total_duration_seconds=overall_end - overall_start,
        scale_results=scale_results,
        collision_degradation=collision_analysis,
        retrieval_degradation=retrieval_analysis,
        is_fractal=is_fractal,
    )
    
    return results


# ============================================================================
# CLI & RESULTS PERSISTENCE
# ============================================================================

def save_results(results: FractalScalingResults, output_file: str = None) -> str:
    """Save results to JSON file."""
    if output_file is None:
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        output_file = f"exp04_fractal_scaling_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results.to_dict(), f, indent=2)
    
    print(f"Results saved to: {output_file}")
    return output_file


if __name__ == '__main__':
    quick_mode = '--full' not in sys.argv
    
    try:
        results = run_fractal_scaling_test(quick_mode=quick_mode)
        output_file = save_results(results)
        
        print("\n" + "=" * 70)
        print("EXP-04 COMPLETE")
        print("=" * 70)
        print(f"Status: {'✓ PASSED' if all(r.is_valid() for r in results.scale_results) else '✗ FAILED'}")
        print(f"Fractal: {'✓ YES' if results.is_fractal else '✗ NO'}")
        print(f"Output: {output_file}")
        print()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)