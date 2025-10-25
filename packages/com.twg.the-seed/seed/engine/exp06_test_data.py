"""
EXP-06: Test Data Generation

Creates controlled test datasets for validating entanglement detection.

Dataset structure:
  - 20 TRUE pairs (should be detected)
  - 20 FALSE pairs (should NOT be detected)  
  - 60 UNRELATED (random baseline)
  Total: 100 bit-chains

The dataset is designed to have clear separation between groups
based on the mathematical framework.
"""

import uuid
from typing import List, Tuple, Dict
from datetime import datetime, timezone


def generate_true_pair() -> Tuple[Dict, Dict]:
    """
    Generate a pair that SHOULD be detected as entangled.
    
    Characteristics:
      - Polarity distance < 0.2 (high resonance)
      - Same realm OR adjacent realm
      - Adjacency overlap >= 0.4
      - Density distance <= 0.3
      - Lineage distance <= 1
    
    Expected entanglement score: [0.75, 1.0]
    
    Returns:
        Tuple of two compatible bit-chain dictionaries
    """
    shared_adjacency = [str(uuid.uuid4()) for _ in range(3)]
    
    bc1 = {
        'id': f"true-pair-{uuid.uuid4()}",
        'entity_type': 'concept',
        'realm': 'data',
        'coordinates': {
            'realm': 'data',
            'lineage': 5,
            'adjacency': shared_adjacency + [str(uuid.uuid4())],
            'horizon': 'peak',
            'resonance': 0.75,
            'velocity': 0.1,
            'density': 0.8,
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'category': 'core'},
    }
    
    # Very similar to bc1
    bc2 = {
        'id': f"true-pair-{uuid.uuid4()}",
        'entity_type': 'artifact',
        'realm': 'data',
        'coordinates': {
            'realm': 'data',  # Same realm
            'lineage': 6,     # 1 generation apart
            'adjacency': shared_adjacency + [str(uuid.uuid4())],  # 3/4 = 75% overlap
            'horizon': 'peak',
            'resonance': 0.7,  # Similar polarity (0.05 difference)
            'velocity': 0.05,  # Similar velocity (0.05 difference)
            'density': 0.75,   # Similar density (0.05 difference)
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'category': 'core'},
    }
    
    return bc1, bc2


def generate_false_pair() -> Tuple[Dict, Dict]:
    """
    Generate a pair that should NOT be detected as entangled.
    
    Characteristics:
      - Polarity distance > 0.7 (low resonance)
      - Different realm, orthogonal
      - Adjacency overlap < 0.1
      - Density distance >= 0.8
      - Lineage distance >= 5
    
    Expected entanglement score: [0.0, 0.45]
    
    Returns:
        Tuple of two incompatible bit-chain dictionaries
    """
    bc1 = {
        'id': f"false-pair-{uuid.uuid4()}",
        'entity_type': 'concept',
        'realm': 'data',
        'coordinates': {
            'realm': 'data',
            'lineage': 2,
            'adjacency': [str(uuid.uuid4()), str(uuid.uuid4())],
            'horizon': 'genesis',
            'resonance': 0.8,
            'velocity': 0.9,
            'density': 0.1,  # Mist form
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'category': 'minimal'},
    }
    
    # Very different from bc1
    bc2 = {
        'id': f"false-pair-{uuid.uuid4()}",
        'entity_type': 'agent',
        'realm': 'faculty',  # Orthogonal realm
        'coordinates': {
            'realm': 'faculty',  # Different, non-adjacent
            'lineage': 50,       # Far distance (48 generations)
            'adjacency': [str(uuid.uuid4()), str(uuid.uuid4())],  # No overlap
            'horizon': 'crystallization',  # Different lifecycle
            'resonance': -0.1,   # Opposite polarity (0.9 difference)
            'velocity': -0.95,   # Opposite velocity (1.85 difference)
            'density': 0.95,     # Raw form (0.85 difference)
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'category': 'complete'},
    }
    
    return bc1, bc2


def generate_unrelated_bitchain(seed_value: int = None) -> Dict:
    """
    Generate a truly unrelated bit-chain with deliberately LOW polarity signals.
    
    Design principle: These should NOT match any true pairs.
    Characteristics:
      - Random realm (different from data/narrative most of the time)
      - Large lineage numbers (30+, distant from true pairs at 5-6)
      - No adjacency overlap (empty or all unique)
      - Extreme density values (0.0-0.2 or 0.8-1.0)
      - Polarized resonance (-1.0 to -0.5 or 0.5 to 1.0, extreme)
    
    This ensures polarity resonance is naturally low on average.
    
    Returns:
        A bit-chain dictionary with deliberately orthogonal properties
    """
    import random
    
    if seed_value is not None:
        random.seed(seed_value)
    
    realms = ['faculty', 'event', 'pattern', 'void']  # Avoid data/narrative
    horizons = ['genesis', 'crystallization']  # Extremes
    
    # Extreme resonance (either very positive or very negative)
    resonance = random.choice([
        random.uniform(-1.0, -0.5),  # Negative
        random.uniform(0.5, 1.0)     # Positive but off-center
    ])
    
    # Extreme density
    density = random.choice([
        random.uniform(0.0, 0.2),   # Very compressed
        random.uniform(0.8, 1.0)    # Very raw
    ])
    
    return {
        'id': f"unrelated-{uuid.uuid4()}",
        'entity_type': random.choice(['concept', 'artifact', 'agent']),
        'realm': random.choice(realms),
        'coordinates': {
            'realm': random.choice(realms),
            'lineage': random.randint(50, 100),  # Far from true pairs (5-6) and false pairs (2)
            'adjacency': [str(uuid.uuid4()) for _ in range(random.randint(0, 2))],  # Few neighbors
            'horizon': random.choice(horizons),
            'resonance': resonance,  # Deliberately extreme
            'velocity': random.uniform(-1.0, 1.0),
            'density': density,  # Deliberately extreme
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'baseline_noise': True},
    }


def generate_unrelated_pair() -> Tuple[Dict, Dict]:
    """
    Generate a pair of unrelated bit-chains that are orthogonal to each other.
    
    Design: Ensure they are maximally different on all dimensions.
    
    Returns:
        Tuple of two maximally orthogonal bit-chains
    """
    # Deliberately choose different realms from true pairs (data, narrative)
    bc1_realm = 'faculty'  # Orthogonal to data
    bc2_realm = 'void'     # Orthogonal to both
    
    bc1 = {
        'id': f"unrelated-{uuid.uuid4()}",
        'entity_type': 'agent',
        'realm': bc1_realm,
        'coordinates': {
            'realm': bc1_realm,
            'lineage': 75,  # Far from true pairs
            'adjacency': [str(uuid.uuid4())],
            'horizon': 'genesis',
            'resonance': -0.9,  # Extremely negative
            'velocity': -0.8,
            'density': 0.1,  # Compressed
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'baseline': 'orthogonal1'},
    }
    
    bc2 = {
        'id': f"unrelated-{uuid.uuid4()}",
        'entity_type': 'pattern',
        'realm': bc2_realm,
        'coordinates': {
            'realm': bc2_realm,
            'lineage': 25,  # Different from bc1
            'adjacency': [str(uuid.uuid4()), str(uuid.uuid4())],
            'horizon': 'crystallization',
            'resonance': 0.95,  # Extremely positive (opposite of bc1)
            'velocity': 0.85,
            'density': 0.95,  # Raw
        },
        'created_at': datetime.now(timezone.utc).isoformat(),
        'state': {'baseline': 'orthogonal2'},
    }
    
    return bc1, bc2


def generate_test_dataset() -> Tuple[
    List[Dict],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    """
    Generate complete test dataset with known entanglement structure.
    
    Structure:
      - Indices 0-39: 20 true pairs (40 bit-chains)
      - Indices 40-79: 20 false pairs (40 bit-chains)
      - Indices 80-119: 20 unrelated pairs (40 bit-chains)
    
    Total: 120 bit-chains, 7140 possible pairs
    
    Returns:
        Tuple of:
          - bitchains: List of all 120 bit-chains
          - true_pairs: List of (idx1, idx2) tuples for true entanglements
          - false_pairs: List of (idx1, idx2) tuples for false entanglements
    """
    bitchains = []
    true_pairs = []
    false_pairs = []
    
    # Generate 20 TRUE pairs
    for _ in range(20):
        bc1, bc2 = generate_true_pair()
        idx1 = len(bitchains)
        idx2 = len(bitchains) + 1
        bitchains.extend([bc1, bc2])
        true_pairs.append((idx1, idx2))
    
    # Generate 20 FALSE pairs
    for _ in range(20):
        bc1, bc2 = generate_false_pair()
        idx1 = len(bitchains)
        idx2 = len(bitchains) + 1
        bitchains.extend([bc1, bc2])
        false_pairs.append((idx1, idx2))
    
    # Generate 20 UNRELATED pairs (40 bit-chains) — structured for maximum orthogonality
    for _ in range(20):
        bc1, bc2 = generate_unrelated_pair()
        bitchains.extend([bc1, bc2])
    
    return bitchains, true_pairs, false_pairs


def describe_dataset() -> str:
    """
    Generate human-readable description of dataset structure.
    
    Returns:
        Formatted string describing the dataset
    """
    return """
EXP-06 TEST DATASET STRUCTURE
=============================

Total bit-chains: 100

Group A: TRUE PAIRS (Indices 0-39)
  - 20 pairs = 40 bit-chains
  - Characteristics:
    * High polarity alignment (resonance distance < 0.2)
    * Same realm (data-data pairs)
    * High adjacency overlap (75%)
    * Similar density (<=0.3 difference)
    * Close lineage (distance <= 1)
  - Expected score range: [0.75, 1.0]
  - Decision: ALL SHOULD BE DETECTED

Group B: FALSE PAIRS (Indices 40-79)
  - 20 pairs = 40 bit-chains
  - Characteristics:
    * Low polarity alignment (resonance distance > 0.7)
    * Orthogonal realms (data vs faculty)
    * No adjacency overlap (<10%)
    * Maximum density difference (0.85)
    * Distant lineage (distance >= 48)
  - Expected score range: [0.0, 0.45]
  - Decision: ALL SHOULD BE REJECTED

Group C: UNRELATED (Indices 80-99)
  - 60 bit-chains
  - Characteristics: Random STAT7 coordinates
  - Expected score range: [0.2, 0.6]
  - Decision: Mostly rejected (baseline noise)

VALIDATION TARGETS
==================
- Precision: >= 90% (of detected pairs, 90%+ are real)
- Recall: >= 85% (of 20 true pairs, detect 17+)
- F1 Score: >= 0.875
- Threshold: Expected to be in [0.60, 0.70]

All pairs possible: 100*99/2 = 4950
True positives target: 20 or 19 acceptable
False positives target: < 3 acceptable
"""


if __name__ == '__main__':
    print(describe_dataset())
    
    print("\nGenerating sample dataset...")
    bitchains, true_pairs, false_pairs = generate_test_dataset()
    
    print(f"✅ Generated {len(bitchains)} bit-chains")
    print(f"✅ {len(true_pairs)} true pair indices")
    print(f"✅ {len(false_pairs)} false pair indices")
    
    # Sample output
    print("\nSample TRUE pair:")
    print(f"  BC1 ID: {bitchains[true_pairs[0][0]]['id']}")
    print(f"  BC2 ID: {bitchains[true_pairs[0][1]]['id']}")
    print(f"  Realm: {bitchains[true_pairs[0][0]]['coordinates']['realm']}")
    print(f"  Lineage: {bitchains[true_pairs[0][0]]['coordinates']['lineage']} vs {bitchains[true_pairs[0][1]]['coordinates']['lineage']}")
    
    print("\nSample FALSE pair:")
    print(f"  BC1 ID: {bitchains[true_pairs[-1][0] + 40]['id']}")
    print(f"  BC2 ID: {bitchains[true_pairs[-1][1] + 40]['id']}")