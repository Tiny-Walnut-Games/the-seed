"""
STAT7 STRESS TEST: Advanced Read/Write Performance Analysis

Push STAT7 addressing to breaking point and measure:
- Latency degradation as scale increases
- Collision rates at massive scales
- Concurrent R/W performance
- Memory consumption patterns
- Finding the exact breaking points

Status: Production-grade stress testing
"""

import json
import hashlib
import time
import uuid
import threading
import random
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import statistics
import psutil
import os


# ============================================================================
# CANONICAL SERIALIZATION (reuse from stat7_experiments.py)
# ============================================================================

def normalize_float(value: float, decimal_places: int = 8) -> str:
    """Normalize floating point to 8 decimal places using banker's rounding."""
    if isinstance(value, float):
        if value != value or value == float('inf') or value == float('-inf'):
            raise ValueError(f"NaN and Inf not allowed: {value}")
    
    d = Decimal(str(value))
    quantized = d.quantize(Decimal(10) ** -decimal_places, rounding=ROUND_HALF_EVEN)
    result = str(quantized)
    if '.' in result:
        result = result.rstrip('0')
        if result.endswith('.'):
            result += '0'
    return result


def sort_json_keys(obj: Any) -> Any:
    """Recursively sort all JSON object keys in ASCII order."""
    if isinstance(obj, dict):
        return {k: sort_json_keys(obj[k]) for k in sorted(obj.keys())}
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def canonical_serialize(data: Dict[str, Any]) -> str:
    """Serialize to canonical form for deterministic hashing."""
    sorted_data = sort_json_keys(data)
    canonical = json.dumps(sorted_data, separators=(',', ':'), ensure_ascii=True, sort_keys=False)
    return canonical


def compute_address_hash(data: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of canonical serialization."""
    canonical = canonical_serialize(data)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StressTestConfig:
    """Configuration for stress test runs."""
    scales: List[int] = field(default_factory=lambda: [1000, 10000, 100000, 1000000])
    queries_per_scale: int = 1000
    concurrent_threads: int = 8
    max_memory_mb: int = 4096
    print_interval: int = 100
    collision_check_enabled: bool = True


@dataclass
class LatencyMetrics:
    """Latency statistics for a test run."""
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    p99_9_ms: float
    stddev_ms: float


@dataclass
class StressTestResult:
    """Results from a single stress test scenario."""
    test_name: str
    scale: int
    operations: int
    total_time_seconds: float
    throughput_ops_per_second: float
    latency_metrics: LatencyMetrics
    collisions: int
    collision_rate: float
    memory_peak_mb: float
    memory_avg_mb: float
    success: bool
    error_message: Optional[str] = None


# ============================================================================
# RANDOM ENTITY GENERATION
# ============================================================================

REALMS = ['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void']
HORIZONS = ['genesis', 'emergence', 'peak', 'decay', 'crystallization']
ENTITY_TYPES = ['concept', 'artifact', 'agent', 'lineage', 'adjacency', 'horizon', 'fragment']


def generate_random_entity(entity_id: Optional[str] = None) -> Dict[str, Any]:
    """Generate a random entity for testing."""
    return {
        'id': entity_id or str(uuid.uuid4()),
        'entity_type': random.choice(ENTITY_TYPES),
        'realm': random.choice(REALMS),
        'stat7_coordinates': {
            'realm': random.choice(REALMS),
            'lineage': random.randint(1, 100),
            'adjacency': sorted([str(uuid.uuid4()) for _ in range(random.randint(0, 5))]),
            'horizon': random.choice(HORIZONS),
            'resonance': float(normalize_float(random.uniform(-1.0, 1.0))),
            'velocity': float(normalize_float(random.uniform(-1.0, 1.0))),
            'density': float(normalize_float(random.uniform(0.0, 1.0))),
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'value': random.randint(0, 1000)},
    }


# ============================================================================
# STRESS TEST: ADDRESS GENERATION PERFORMANCE
# ============================================================================

class StressTest_AddressGeneration:
    """Test addressing speed at increasing scales."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.results: List[StressTestResult] = []
    
    def run(self) -> List[StressTestResult]:
        """Run address generation stress tests."""
        print(f"\n{'='*80}")
        print(f"STRESS TEST 1: ADDRESS GENERATION PERFORMANCE")
        print(f"Testing addressing speed at scales: {self.config.scales}")
        print(f"{'='*80}\n")
        
        for scale in self.config.scales:
            print(f"Testing scale: {scale:,} entities...")
            result = self._test_scale(scale)
            self.results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} | Throughput: {result.throughput_ops_per_second:,.0f} ops/sec | "
                  f"Mean latency: {result.latency_metrics.mean_ms:.6f}ms | "
                  f"Peak memory: {result.memory_peak_mb:.1f}MB\n")
    
    def _test_scale(self, scale: int) -> StressTestResult:
        """Test addressing performance at a single scale."""
        process = psutil.Process(os.getpid())
        process.memory_info()  # Initialize
        
        entities = [generate_random_entity() for _ in range(scale)]
        
        latencies = []
        collision_set = set()
        collisions = 0
        memory_samples = []
        
        start_time = time.perf_counter()
        
        for i, entity in enumerate(entities):
            # Measure individual operation
            op_start = time.perf_counter()
            address = compute_address_hash(entity)
            op_end = time.perf_counter()
            
            latencies.append((op_end - op_start) * 1000)  # Convert to ms
            
            # Check for collisions
            if address in collision_set:
                collisions += 1
            collision_set.add(address)
            
            # Sample memory every 100 operations
            if i % 100 == 0:
                mem = process.memory_info().rss / (1024 * 1024)  # MB
                memory_samples.append(mem)
            
            # Progress
            if (i + 1) % self.config.print_interval == 0:
                print(f"    Processed {i+1:,}/{scale:,} ({(i+1)/scale*100:.1f}%)")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate metrics
        latency_metrics = self._calculate_latency_metrics(latencies)
        throughput = scale / total_time
        collision_rate = collisions / scale if collisions > 0 else 0.0
        
        memory_peak = max(memory_samples) if memory_samples else 0
        memory_avg = statistics.mean(memory_samples) if memory_samples else 0
        
        return StressTestResult(
            test_name="Address Generation",
            scale=scale,
            operations=scale,
            total_time_seconds=total_time,
            throughput_ops_per_second=throughput,
            latency_metrics=latency_metrics,
            collisions=collisions,
            collision_rate=collision_rate,
            memory_peak_mb=memory_peak,
            memory_avg_mb=memory_avg,
            success=(collisions == 0 and total_time > 0),
        )
    
    def _calculate_latency_metrics(self, latencies: List[float]) -> LatencyMetrics:
        """Calculate latency statistics."""
        sorted_lats = sorted(latencies)
        return LatencyMetrics(
            min_ms=min(sorted_lats),
            max_ms=max(sorted_lats),
            mean_ms=statistics.mean(sorted_lats),
            median_ms=statistics.median(sorted_lats),
            p95_ms=sorted_lats[int(len(sorted_lats) * 0.95)],
            p99_ms=sorted_lats[int(len(sorted_lats) * 0.99)],
            p99_9_ms=sorted_lats[int(len(sorted_lats) * 0.999)] if len(sorted_lats) > 1000 else sorted_lats[-1],
            stddev_ms=statistics.stdev(sorted_lats) if len(sorted_lats) > 1 else 0,
        )


# ============================================================================
# STRESS TEST: READ/WRITE SIMULTANEOUS OPERATIONS
# ============================================================================

class StressTest_ReadWriteSimultaneous:
    """Test simultaneous read and write operations at scale."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.results: List[StressTestResult] = []
        self.address_store: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def run(self) -> List[StressTestResult]:
        """Run simultaneous R/W stress tests."""
        print(f"\n{'='*80}")
        print(f"STRESS TEST 2: SIMULTANEOUS READ/WRITE OPERATIONS")
        print(f"Testing concurrent R/W at scales: {self.config.scales}")
        print(f"Concurrent threads: {self.config.concurrent_threads}")
        print(f"{'='*80}\n")
        
        for scale in self.config.scales:
            print(f"Testing scale: {scale:,} entities with {self.config.concurrent_threads} threads...")
            result = self._test_scale(scale)
            self.results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} | Throughput: {result.throughput_ops_per_second:,.0f} ops/sec | "
                  f"Mean latency: {result.latency_metrics.mean_ms:.6f}ms | "
                  f"Peak memory: {result.memory_peak_mb:.1f}MB\n")
    
    def _test_scale(self, scale: int) -> StressTestResult:
        """Test R/W performance at a single scale."""
        self.address_store.clear()
        process = psutil.Process(os.getpid())
        
        # Pre-populate store
        print(f"    Pre-populating store with {scale:,} entities...")
        for i in range(scale):
            entity = generate_random_entity()
            address = compute_address_hash(entity)
            self.address_store[address] = entity
            if (i + 1) % (scale // 10) == 0:
                print(f"      {i+1:,}/{scale:,}")
        
        # Run concurrent operations
        latencies = []
        operation_count = 0
        lock = threading.Lock()
        memory_samples = []
        
        def worker():
            nonlocal operation_count
            local_latencies = []
            
            for _ in range(self.config.queries_per_scale):
                # Randomly choose: read (70%) or write (30%)
                if random.random() < 0.7:
                    # READ operation
                    op_start = time.perf_counter()
                    address = random.choice(list(self.address_store.keys()))
                    _ = self.address_store.get(address)
                    op_end = time.perf_counter()
                else:
                    # WRITE operation
                    op_start = time.perf_counter()
                    entity = generate_random_entity()
                    address = compute_address_hash(entity)
                    with lock:
                        self.address_store[address] = entity
                    op_end = time.perf_counter()
                
                local_latencies.append((op_end - op_start) * 1000)
                
                with lock:
                    operation_count += 1
            
            with lock:
                latencies.extend(local_latencies)
        
        # Start threads
        start_time = time.perf_counter()
        threads = []
        
        for _ in range(self.config.concurrent_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # Monitor progress
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
            mem = process.memory_info().rss / (1024 * 1024)
            memory_samples.append(mem)
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate metrics
        latency_metrics = self._calculate_latency_metrics(latencies)
        throughput = operation_count / total_time
        
        memory_peak = max(memory_samples) if memory_samples else 0
        memory_avg = statistics.mean(memory_samples) if memory_samples else 0
        
        return StressTestResult(
            test_name="Simultaneous R/W",
            scale=scale,
            operations=operation_count,
            total_time_seconds=total_time,
            throughput_ops_per_second=throughput,
            latency_metrics=latency_metrics,
            collisions=0,
            collision_rate=0.0,
            memory_peak_mb=memory_peak,
            memory_avg_mb=memory_avg,
            success=(total_time > 0 and operation_count > 0),
        )
    
    def _calculate_latency_metrics(self, latencies: List[float]) -> LatencyMetrics:
        """Calculate latency statistics."""
        if not latencies:
            return LatencyMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        sorted_lats = sorted(latencies)
        return LatencyMetrics(
            min_ms=min(sorted_lats),
            max_ms=max(sorted_lats),
            mean_ms=statistics.mean(sorted_lats),
            median_ms=statistics.median(sorted_lats),
            p95_ms=sorted_lats[int(len(sorted_lats) * 0.95)] if len(sorted_lats) > 0 else 0,
            p99_ms=sorted_lats[int(len(sorted_lats) * 0.99)] if len(sorted_lats) > 0 else 0,
            p99_9_ms=sorted_lats[int(len(sorted_lats) * 0.999)] if len(sorted_lats) > 1000 else sorted_lats[-1] if sorted_lats else 0,
            stddev_ms=statistics.stdev(sorted_lats) if len(sorted_lats) > 1 else 0,
        )


# ============================================================================
# STRESS TEST: LOOKUP PERFORMANCE (HASH TABLE)
# ============================================================================

class StressTest_LookupPerformance:
    """Test lookup speed as scale increases (simulating real-world retrieval)."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.results: List[StressTestResult] = []
    
    def run(self) -> List[StressTestResult]:
        """Run lookup performance tests."""
        print(f"\n{'='*80}")
        print(f"STRESS TEST 3: LOOKUP PERFORMANCE (Finding entities by address)")
        print(f"Testing lookup speed at scales: {self.config.scales}")
        print(f"Queries per scale: {self.config.queries_per_scale:,}")
        print(f"{'='*80}\n")
        
        for scale in self.config.scales:
            print(f"Testing scale: {scale:,} entities...")
            result = self._test_scale(scale)
            self.results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} | Queries/sec: {result.throughput_ops_per_second:,.0f} | "
                  f"Mean lookup: {result.latency_metrics.mean_ms:.6f}ms | "
                  f"Max lookup: {result.latency_metrics.max_ms:.6f}ms\n")
    
    def _test_scale(self, scale: int) -> StressTestResult:
        """Test lookup performance at a single scale."""
        process = psutil.Process(os.getpid())
        
        # Generate and store entities
        print(f"    Generating and indexing {scale:,} entities...")
        store = {}
        entities_to_query = []
        
        for i in range(scale):
            entity = generate_random_entity()
            address = compute_address_hash(entity)
            store[address] = entity
            
            # Keep every Nth entity for queries
            if i % (scale // min(1000, self.config.queries_per_scale)) == 0:
                entities_to_query.append(address)
            
            if (i + 1) % (scale // 10) == 0:
                print(f"      {i+1:,}/{scale:,}")
        
        # Ensure we have queries
        if len(entities_to_query) < self.config.queries_per_scale:
            entities_to_query = list(store.keys())[:self.config.queries_per_scale]
        
        # Run lookups
        latencies = []
        memory_samples = []
        
        start_time = time.perf_counter()
        
        for i, address in enumerate(entities_to_query):
            op_start = time.perf_counter()
            _ = store.get(address)
            op_end = time.perf_counter()
            
            latencies.append((op_end - op_start) * 1000 * 1000)  # Convert to microseconds for precision
            
            if i % (len(entities_to_query) // 10) == 0 and i > 0:
                mem = process.memory_info().rss / (1024 * 1024)
                memory_samples.append(mem)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate metrics
        latency_metrics = self._calculate_latency_metrics(latencies)
        throughput = len(entities_to_query) / total_time
        
        memory_peak = max(memory_samples) if memory_samples else 0
        memory_avg = statistics.mean(memory_samples) if memory_samples else 0
        
        return StressTestResult(
            test_name="Lookup Performance",
            scale=scale,
            operations=len(entities_to_query),
            total_time_seconds=total_time,
            throughput_ops_per_second=throughput,
            latency_metrics=latency_metrics,
            collisions=0,
            collision_rate=0.0,
            memory_peak_mb=memory_peak,
            memory_avg_mb=memory_avg,
            success=(total_time > 0),
        )
    
    def _calculate_latency_metrics(self, latencies: List[float]) -> LatencyMetrics:
        """Calculate latency statistics."""
        if not latencies:
            return LatencyMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        sorted_lats = sorted(latencies)
        return LatencyMetrics(
            min_ms=min(sorted_lats) / 1000,  # Convert back to ms
            max_ms=max(sorted_lats) / 1000,
            mean_ms=statistics.mean(sorted_lats) / 1000,
            median_ms=statistics.median(sorted_lats) / 1000,
            p95_ms=sorted_lats[int(len(sorted_lats) * 0.95)] / 1000,
            p99_ms=sorted_lats[int(len(sorted_lats) * 0.99)] / 1000,
            p99_9_ms=(sorted_lats[int(len(sorted_lats) * 0.999)] if len(sorted_lats) > 1000 else sorted_lats[-1]) / 1000,
            stddev_ms=statistics.stdev(sorted_lats) / 1000 if len(sorted_lats) > 1 else 0,
        )


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_full_stress_test(quick: bool = False) -> Dict[str, Any]:
    """Run complete stress test suite."""
    
    config = StressTestConfig()
    
    if quick:
        print("\n🏃 QUICK MODE: Smaller scales for fast feedback\n")
        config.scales = [10000, 100000]
        config.queries_per_scale = 100
        config.concurrent_threads = 4
    else:
        print("\n🔥 FULL MODE: All scales from 1K to 10M\n")
        config.scales = [1000, 10000, 100000, 1000000, 10000000]
        config.queries_per_scale = 5000
        config.concurrent_threads = 8
    
    print(f"Configuration:")
    print(f"  Scales: {config.scales}")
    print(f"  Queries per scale: {config.queries_per_scale:,}")
    print(f"  Concurrent threads: {config.concurrent_threads}")
    print(f"  Collision checking: {config.collision_check_enabled}")
    print()
    
    # Run all stress tests
    all_results = []
    
    try:
        # Test 1: Address Generation
        test1 = StressTest_AddressGeneration(config)
        test1.run()
        all_results.extend(test1.results)
        
        # Test 2: Read/Write Simultaneous
        test2 = StressTest_ReadWriteSimultaneous(config)
        test2.run()
        all_results.extend(test2.results)
        
        # Test 3: Lookup Performance
        test3 = StressTest_LookupPerformance(config)
        test3.run()
        all_results.extend(test3.results)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        pass
    except MemoryError:
        print("\n\n❌ Out of memory - system hit memory limit")
        pass
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    return format_results(all_results)


def format_results(results: List[StressTestResult]) -> Dict[str, Any]:
    """Format results for output."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE",
        "total_tests": len(results),
        "results": [
            {
                "test_name": r.test_name,
                "scale": r.scale,
                "operations": r.operations,
                "total_time_seconds": round(r.total_time_seconds, 3),
                "throughput_ops_per_second": round(r.throughput_ops_per_second, 2),
                "latency_metrics": {
                    "min_ms": round(r.latency_metrics.min_ms, 6),
                    "max_ms": round(r.latency_metrics.max_ms, 6),
                    "mean_ms": round(r.latency_metrics.mean_ms, 6),
                    "median_ms": round(r.latency_metrics.median_ms, 6),
                    "p95_ms": round(r.latency_metrics.p95_ms, 6),
                    "p99_ms": round(r.latency_metrics.p99_ms, 6),
                    "p99_9_ms": round(r.latency_metrics.p99_9_ms, 6),
                    "stddev_ms": round(r.latency_metrics.stddev_ms, 6),
                },
                "collisions": r.collisions,
                "collision_rate": round(r.collision_rate, 6),
                "memory_peak_mb": round(r.memory_peak_mb, 2),
                "memory_avg_mb": round(r.memory_avg_mb, 2),
                "success": r.success,
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    quick_mode = "--quick" in sys.argv
    results = run_full_stress_test(quick=quick_mode)
    
    # Print summary
    print(f"\n\n{'='*80}")
    print(f"STRESS TEST COMPLETE")
    print(f"{'='*80}\n")
    
    # Find breaking points
    print("KEY FINDINGS:\n")
    
    # Group by test name
    by_test = defaultdict(list)
    for r in results["results"]:
        by_test[r["test_name"]].append(r)
    
    for test_name, test_results in by_test.items():
        print(f"📊 {test_name}:")
        
        # Find where latency degrades
        for i, result in enumerate(test_results):
            scale = result["scale"]
            mean_lat = result["latency_metrics"]["mean_ms"]
            
            degradation = ""
            if i > 0:
                prev_lat = test_results[i-1]["latency_metrics"]["mean_ms"]
                increase = (mean_lat - prev_lat) / prev_lat * 100
                if increase > 10:
                    degradation = f" ⚠️  Latency increased {increase:.1f}%"
                elif increase > 50:
                    degradation = f" 🔴 DEGRADATION {increase:.1f}%"
            
            print(f"  Scale {scale:>9,}: {mean_lat:>9.6f}ms mean latency{degradation}")
        
        print()
    
    # Save full results
    output_file = f"STRESS_TEST_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Full results saved to: {output_file}\n")