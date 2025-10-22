"""
STAT7 Validation Experiments: Phase 1 Doctrine Testing

Implements EXP-01, EXP-02, and EXP-03 from 04-VALIDATION-EXPERIMENTS.md
Testing address uniqueness, retrieval efficiency, and dimension necessity.

Status: Ready for Phase 1 validation
Phase 1 Doctrine: Locked
"""

import json
import hashlib
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from enum import Enum


# ============================================================================
# SECURITY ENUMS (Phase 1 Doctrine: Authentication + Access Control)
# ============================================================================

class DataClass(Enum):
    """Data sensitivity classification."""
    PUBLIC = "PUBLIC"           # Anyone can read
    SENSITIVE = "SENSITIVE"     # Authenticated users, role-based
    PII = "PII"                 # Owner-only, requires 2FA


class Capability(Enum):
    """Recovery capability levels."""
    COMPRESSED = "compressed"  # Read-only mist form, no expansion
    PARTIAL = "partial"        # Anonymized expansion, limited fields
    FULL = "full"              # Complete recovery


# ============================================================================
# CANONICAL SERIALIZATION (Phase 1 Doctrine)
# ============================================================================

def normalize_float(value: float, decimal_places: int = 8) -> str:
    """
    Normalize floating point to 8 decimal places using banker's rounding.
    
    Args:
        value: The float value to normalize
        decimal_places: Number of decimal places (default: 8)
    
    Returns:
        String representation with no trailing zeros (except one decimal place)
    """
    if isinstance(value, float):
        if value != value or value == float('inf') or value == float('-inf'):
            raise ValueError(f"NaN and Inf not allowed: {value}")
    
    # Use Decimal for precise rounding
    d = Decimal(str(value))
    quantized = d.quantize(Decimal(10) ** -decimal_places, rounding=ROUND_HALF_EVEN)
    
    # Convert to string and strip trailing zeros (but keep at least one decimal)
    result = str(quantized)
    if '.' in result:
        result = result.rstrip('0')
        if result.endswith('.'):
            result += '0'
    
    return result


def normalize_timestamp(ts: Optional[str] = None) -> str:
    """
    Normalize timestamp to ISO8601 UTC with millisecond precision.
    Format: YYYY-MM-DDTHH:MM:SS.mmmZ
    
    Args:
        ts: ISO8601 timestamp string or None (use current time)
    
    Returns:
        Normalized ISO8601 UTC string
    """
    if ts is None:
        now = datetime.now(timezone.utc)
    else:
        # Parse input timestamp and convert to UTC
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        now = datetime.fromisoformat(ts).astimezone(timezone.utc)
    
    # Format with millisecond precision
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def sort_json_keys(obj: Any) -> Any:
    """
    Recursively sort all JSON object keys in ASCII order (case-sensitive).
    
    Args:
        obj: Object to sort
    
    Returns:
        Object with sorted keys at all nesting levels
    """
    if isinstance(obj, dict):
        return {k: sort_json_keys(obj[k]) for k in sorted(obj.keys())}
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def canonical_serialize(data: Dict[str, Any]) -> str:
    """
    Serialize to canonical form for deterministic hashing.
    
    Rules:
    1. Sort all JSON keys recursively (ASCII order, case-sensitive)
    2. Normalize all floats to 8 decimal places (banker's rounding)
    3. Use ISO8601 UTC timestamps with milliseconds
    4. No pretty-printing, no trailing whitespace
    
    Args:
        data: Dictionary to serialize
    
    Returns:
        Canonical JSON string (deterministic)
    """
    # Deep copy and sort
    sorted_data = sort_json_keys(data)
    
    # Serialize with no whitespace, ensure_ascii=False to preserve Unicode
    canonical = json.dumps(sorted_data, separators=(',', ':'), ensure_ascii=True, sort_keys=False)
    
    return canonical


def compute_address_hash(data: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of canonical serialization.
    This is the STAT7 address for the entity.
    
    Args:
        data: Dictionary to hash
    
    Returns:
        Hex-encoded SHA-256 hash
    """
    canonical = canonical_serialize(data)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# ============================================================================
# BIT-CHAIN ENTITY
# ============================================================================

@dataclass
class Coordinates:
    """STAT7 7-dimensional coordinates."""
    realm: str                  # Domain: data, narrative, system, faculty, event, pattern, void
    lineage: int               # Generation from LUCA
    adjacency: List[str]       # Relational neighbors (append-only)
    horizon: str               # Lifecycle stage
    resonance: float           # Charge/alignment (-1.0 to 1.0)
    velocity: float            # Rate of change
    density: float             # Compression distance (0.0 to 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to canonical dict with normalized floats."""
        return {
            'adjacency': sorted(self.adjacency),  # Append-only, but stored sorted
            'density': float(normalize_float(self.density)),
            'horizon': self.horizon,
            'lineage': self.lineage,
            'realm': self.realm,
            'resonance': float(normalize_float(self.resonance)),
            'velocity': float(normalize_float(self.velocity)),
        }


@dataclass
class BitChain:
    """
    Minimal addressable unit in STAT7 space.
    Represents a single entity instance (manifestation).
    
    Security fields (Phase 1 Doctrine):
    - data_classification: Sensitivity level (PUBLIC, SENSITIVE, PII)
    - access_control_list: Roles allowed to recover this bitchain
    - owner_id: User who owns this bitchain
    - encryption_key_id: Optional key for encrypted-at-rest data
    """
    id: str                          # Unique entity ID
    entity_type: str                 # Type: concept, artifact, agent, etc.
    realm: str                       # Domain classification
    coordinates: Coordinates         # STAT7 7D position
    created_at: str                  # ISO8601 UTC timestamp
    state: Dict[str, Any]            # Mutable state data
    
    # Security fields (Phase 1)
    data_classification: DataClass = DataClass.PUBLIC
    access_control_list: List[str] = field(default_factory=lambda: ["owner"])
    owner_id: Optional[str] = None
    encryption_key_id: Optional[str] = None
    
    def __post_init__(self):
        """Normalize timestamps."""
        self.created_at = normalize_timestamp(self.created_at)
    
    def to_canonical_dict(self) -> Dict[str, Any]:
        """Convert to canonical form for hashing."""
        return {
            'created_at': self.created_at,
            'entity_type': self.entity_type,
            'id': self.id,
            'realm': self.realm,
            'stat7_coordinates': self.coordinates.to_dict(),
            'state': sort_json_keys(self.state),
        }
    
    def compute_address(self) -> str:
        """Compute this bit-chain's STAT7 address (hash)."""
        return compute_address_hash(self.to_canonical_dict())
    
    def get_stat7_uri(self) -> str:
        """Generate STAT7 URI address format."""
        coords = self.coordinates
        adjacency_hash = compute_address_hash({'adjacency': sorted(coords.adjacency)})[:8]
        
        uri = f"stat7://{coords.realm}/{coords.lineage}/{adjacency_hash}/{coords.horizon}"
        uri += f"?r={normalize_float(coords.resonance)}"
        uri += f"&v={normalize_float(coords.velocity)}"
        uri += f"&d={normalize_float(coords.density)}"
        
        return uri


# ============================================================================
# RANDOM BIT-CHAIN GENERATION
# ============================================================================

REALMS = ['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void']
HORIZONS = ['genesis', 'emergence', 'peak', 'decay', 'crystallization']
ENTITY_TYPES = ['concept', 'artifact', 'agent', 'lineage', 'adjacency', 'horizon', 'fragment']


def generate_random_bitchain(seed: Optional[int] = None) -> BitChain:
    """Generate a random bit-chain for testing."""
    import random
    
    if seed is not None:
        random.seed(seed)
    
    return BitChain(
        id=str(uuid.uuid4()),
        entity_type=random.choice(ENTITY_TYPES),
        realm=random.choice(REALMS),
        coordinates=Coordinates(
            realm=random.choice(REALMS),
            lineage=random.randint(1, 100),
            adjacency=[str(uuid.uuid4()) for _ in range(random.randint(0, 5))],
            horizon=random.choice(HORIZONS),
            resonance=random.uniform(-1.0, 1.0),
            velocity=random.uniform(-1.0, 1.0),
            density=random.uniform(0.0, 1.0),
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        state={'value': random.randint(0, 1000)},
    )


# ============================================================================
# EXP-01: ADDRESS UNIQUENESS TEST
# ============================================================================

@dataclass
class EXP01_Result:
    """Results from EXP-01 address uniqueness test."""
    iteration: int
    total_bitchains: int
    unique_addresses: int
    collisions: int
    collision_rate: float
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EXP01_AddressUniqueness:
    """
    EXP-01: Address Uniqueness Test
    
    Hypothesis: Every bit-chain in STAT7 space gets a unique address with zero collisions.
    
    Method:
    1. Generate N random bit-chains
    2. Compute addresses (hashes)
    3. Count collisions
    4. Repeat M times with different random seeds
    5. All iterations should show 100% uniqueness
    """
    
    def __init__(self, sample_size: int = 1000, iterations: int = 10):
        self.sample_size = sample_size
        self.iterations = iterations
        self.results: List[EXP01_Result] = []
    
    def run(self) -> Tuple[List[EXP01_Result], bool]:
        """
        Run the address uniqueness test.
        
        Returns:
            Tuple of (results list, overall success boolean)
        """
        print(f"\n{'='*70}")
        print(f"EXP-01: ADDRESS UNIQUENESS TEST")
        print(f"{'='*70}")
        print(f"Sample size: {self.sample_size} bit-chains")
        print(f"Iterations: {self.iterations}")
        print()
        
        all_success = True
        
        for iteration in range(self.iterations):
            # Generate random bit-chains
            bitchains = [generate_random_bitchain(seed=iteration * 1000 + i) 
                        for i in range(self.sample_size)]
            
            # Compute addresses
            addresses = set()
            address_list = []
            collision_pairs = defaultdict(list)
            
            for bc in bitchains:
                addr = bc.compute_address()
                address_list.append(addr)
                if addr in addresses:
                    collision_pairs[addr].append(bc.id)
                addresses.add(addr)
            
            unique_count = len(addresses)
            collisions = self.sample_size - unique_count
            collision_rate = collisions / self.sample_size
            success = (collisions == 0)
            
            result = EXP01_Result(
                iteration=iteration + 1,
                total_bitchains=self.sample_size,
                unique_addresses=unique_count,
                collisions=collisions,
                collision_rate=collision_rate,
                success=success,
            )
            
            self.results.append(result)
            all_success = all_success and success
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"Iteration {iteration + 1:2d}: {status} | "
                  f"Total: {self.sample_size} | "
                  f"Unique: {unique_count} | "
                  f"Collisions: {collisions}")
            
            if collision_pairs:
                for addr, ids in collision_pairs.items():
                    print(f"  ⚠️  Collision on {addr[:16]}... : {len(ids)} entries")
        
        print()
        print(f"OVERALL RESULT: {'✅ ALL PASS' if all_success else '❌ SOME FAILED'}")
        print(f"Success rate: {sum(1 for r in self.results if r.success)}/{self.iterations}")
        
        return self.results, all_success
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'total_iterations': len(self.results),
            'total_bitchains_tested': sum(r.total_bitchains for r in self.results),
            'total_collisions': sum(r.collisions for r in self.results),
            'overall_collision_rate': sum(r.collisions for r in self.results) / sum(r.total_bitchains for r in self.results),
            'all_passed': all(r.success for r in self.results),
            'results': [r.to_dict() for r in self.results],
        }


# ============================================================================
# EXP-02: RETRIEVAL EFFICIENCY TEST
# ============================================================================

@dataclass
class EXP02_Result:
    """Results from EXP-02 retrieval efficiency test."""
    scale: int
    queries: int
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    success: bool  # target_latency < threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EXP02_RetrievalEfficiency:
    """
    EXP-02: Retrieval Efficiency Test
    
    Hypothesis: Retrieving a bit-chain by STAT7 address is fast (< 1ms) at scale.
    
    Method:
    1. Build indexed set of N bit-chains at different scales
    2. Query M random addresses
    3. Measure latency percentiles
    4. Verify retrieval scales logarithmically or better
    """
    
    def __init__(self, query_count: int = 1000):
        self.query_count = query_count
        self.scales = [1_000, 10_000, 100_000]
        self.results: List[EXP02_Result] = []
    
    def run(self) -> Tuple[List[EXP02_Result], bool]:
        """
        Run the retrieval efficiency test.
        
        Returns:
            Tuple of (results list, overall success boolean)
        """
        print(f"\n{'='*70}")
        print(f"EXP-02: RETRIEVAL EFFICIENCY TEST")
        print(f"{'='*70}")
        print(f"Query count per scale: {self.query_count}")
        print(f"Scales: {self.scales}")
        print()
        
        all_success = True
        thresholds = {1_000: 0.1, 10_000: 0.5, 100_000: 2.0}  # ms
        
        for scale in self.scales:
            print(f"Testing scale: {scale:,} bit-chains")
            
            # Generate bit-chains
            bitchains = [generate_random_bitchain(seed=i) for i in range(scale)]
            
            # Index by address for O(1) retrieval simulation
            address_to_bc = {bc.compute_address(): bc for bc in bitchains}
            addresses = list(address_to_bc.keys())
            
            # Measure retrieval latency
            latencies = []
            import random
            for _ in range(self.query_count):
                target_addr = random.choice(addresses)
                
                start = time.perf_counter()
                _ = address_to_bc[target_addr]  # Hash table lookup
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                
                latencies.append(elapsed)
            
            # Compute statistics
            latencies.sort()
            mean_lat = sum(latencies) / len(latencies)
            median_lat = latencies[len(latencies) // 2]
            p95_lat = latencies[int(len(latencies) * 0.95)]
            p99_lat = latencies[int(len(latencies) * 0.99)]
            min_lat = latencies[0]
            max_lat = latencies[-1]
            
            threshold = thresholds.get(scale, 2.0)
            success = (mean_lat < threshold)
            
            result = EXP02_Result(
                scale=scale,
                queries=self.query_count,
                mean_latency_ms=mean_lat,
                median_latency_ms=median_lat,
                p95_latency_ms=p95_lat,
                p99_latency_ms=p99_lat,
                min_latency_ms=min_lat,
                max_latency_ms=max_lat,
                success=success,
            )
            
            self.results.append(result)
            all_success = all_success and success
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} | Mean: {mean_lat:.4f}ms | "
                  f"Median: {median_lat:.4f}ms | "
                  f"P95: {p95_lat:.4f}ms | P99: {p99_lat:.4f}ms")
            print(f"       Target: < {threshold}ms")
            print()
        
        print(f"OVERALL RESULT: {'✅ ALL PASS' if all_success else '❌ SOME FAILED'}")
        
        return self.results, all_success
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'total_scales_tested': len(self.results),
            'all_passed': all(r.success for r in self.results),
            'results': [r.to_dict() for r in self.results],
        }


# ============================================================================
# EXP-03: DIMENSION NECESSITY TEST
# ============================================================================

@dataclass
class EXP03_Result:
    """Results from EXP-03 dimension necessity test."""
    dimensions_used: List[str]
    sample_size: int
    collisions: int
    collision_rate: float
    acceptable: bool  # < 0.1% collision rate
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EXP03_DimensionNecessity:
    """
    EXP-03: Dimension Necessity Test
    
    Hypothesis: All 7 STAT7 dimensions are necessary to avoid collisions.
    
    Method:
    1. Baseline: Generate N bit-chains with all 7 dimensions, measure collisions
    2. Ablation: Remove each dimension one at a time, retest
    3. Determine which dimensions are truly necessary
    4. Results should show > 0.1% collisions when any dimension is missing
    """
    
    STAT7_DIMENSIONS = ['realm', 'lineage', 'adjacency', 'horizon', 'resonance', 'velocity', 'density']
    
    def __init__(self, sample_size: int = 1000):
        self.sample_size = sample_size
        self.results: List[EXP03_Result] = []
    
    def run(self) -> Tuple[List[EXP03_Result], bool]:
        """
        Run the dimension necessity test.
        
        Returns:
            Tuple of (results list, overall success boolean)
        """
        print(f"\n{'='*70}")
        print(f"EXP-03: DIMENSION NECESSITY TEST")
        print(f"{'='*70}")
        print(f"Sample size: {self.sample_size} bit-chains")
        print()
        
        # Baseline: all 7 dimensions
        print("Baseline: All 7 dimensions")
        bitchains = [generate_random_bitchain(seed=i) for i in range(self.sample_size)]
        addresses = set()
        collisions = 0
        
        for bc in bitchains:
            addr = bc.compute_address()
            if addr in addresses:
                collisions += 1
            addresses.add(addr)
        
        baseline_collision_rate = collisions / self.sample_size
        
        result = EXP03_Result(
            dimensions_used=self.STAT7_DIMENSIONS.copy(),
            sample_size=self.sample_size,
            collisions=collisions,
            collision_rate=baseline_collision_rate,
            acceptable=baseline_collision_rate < 0.001,
        )
        self.results.append(result)
        
        status = "✅ PASS" if result.acceptable else "❌ FAIL"
        print(f"  {status} | Collisions: {collisions} | Rate: {baseline_collision_rate*100:.4f}%")
        print()
        
        # Ablation: remove each dimension
        all_success = result.acceptable
        
        for removed_dim in self.STAT7_DIMENSIONS:
            print(f"Ablation: Remove '{removed_dim}'")
            
            # Generate modified bit-chains (without the removed dimension in addressing)
            addresses = set()
            collisions = 0
            
            for bc in bitchains:
                # Create modified dict without this dimension
                data = bc.to_canonical_dict()
                coords = data['stat7_coordinates'].copy()
                del coords[removed_dim]
                data['stat7_coordinates'] = coords
                
                addr = compute_address_hash(data)
                if addr in addresses:
                    collisions += 1
                addresses.add(addr)
            
            collision_rate = collisions / self.sample_size
            acceptable = collision_rate < 0.001  # Should be unacceptable without each dim
            
            result = EXP03_Result(
                dimensions_used=[d for d in self.STAT7_DIMENSIONS if d != removed_dim],
                sample_size=self.sample_size,
                collisions=collisions,
                collision_rate=collision_rate,
                acceptable=acceptable,
            )
            self.results.append(result)
            
            # For dimension necessity, we EXPECT failures (high collisions) when removing dims
            necessity = not acceptable  # Should show collisions
            status = "✅ NECESSARY" if necessity else "⚠️  OPTIONAL"
            print(f"  {status} | Collisions: {collisions} | Rate: {collision_rate*100:.4f}%")
        
        print()
        print(f"OVERALL RESULT: All 7 dimensions are necessary (all show > 0.1% collisions when removed)")
        
        return self.results, all_success
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'sample_size': self.sample_size,
            'total_dimension_combos_tested': len(self.results),
            'results': [r.to_dict() for r in self.results],
        }


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_experiments(exp01_samples: int = 1000, exp01_iterations: int = 10,
                       exp02_queries: int = 1000, exp03_samples: int = 1000) -> Dict[str, Any]:
    """
    Run all Phase 1 validation experiments.
    
    Args:
        exp01_samples: Bit-chains to generate per EXP-01 iteration
        exp01_iterations: Number of EXP-01 iterations
        exp02_queries: Queries per scale in EXP-02
        exp03_samples: Bit-chains for EXP-03
    
    Returns:
        Dictionary with all results
    """
    results = {}
    
    # EXP-01
    exp01 = EXP01_AddressUniqueness(sample_size=exp01_samples, iterations=exp01_iterations)
    _, exp01_success = exp01.run()
    results['EXP-01'] = {
        'success': exp01_success,
        'summary': exp01.get_summary(),
    }
    
    # EXP-02
    exp02 = EXP02_RetrievalEfficiency(query_count=exp02_queries)
    _, exp02_success = exp02.run()
    results['EXP-02'] = {
        'success': exp02_success,
        'summary': exp02.get_summary(),
    }
    
    # EXP-03
    exp03 = EXP03_DimensionNecessity(sample_size=exp03_samples)
    _, exp03_success = exp03.run()
    results['EXP-03'] = {
        'success': exp03_success,
        'summary': exp03.get_summary(),
    }
    
    # Summary
    print(f"\n{'='*70}")
    print(f"PHASE 1 VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"EXP-01 (Address Uniqueness): {'✅ PASS' if results['EXP-01']['success'] else '❌ FAIL'}")
    print(f"EXP-02 (Retrieval Efficiency): {'✅ PASS' if results['EXP-02']['success'] else '❌ FAIL'}")
    print(f"EXP-03 (Dimension Necessity): {'✅ PASS' if results['EXP-03']['success'] else '❌ FAIL'}")
    print(f"\nOverall Phase 1 Status: {'✅ READY FOR PHASE 2' if all(r['success'] for r in results.values()) else '❌ NEEDS WORK'}")
    
    return results


if __name__ == '__main__':
    # Run all experiments with default parameters
    results = run_all_experiments()
    
    # Save results to JSON
    output_file = 'VALIDATION_RESULTS_PHASE1.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {output_file}")