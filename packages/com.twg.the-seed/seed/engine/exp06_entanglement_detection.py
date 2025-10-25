"""
EXP-06: Entanglement Detection

Implements the mathematical framework for detecting semantic entanglement between bit-chains.
All algorithms are formally proven in EXP-06-MATHEMATICAL-FRAMEWORK.md

Core Score Function (Version 2 — Tuned Weights):
E(B1, B2) = 0.5·P + 0.15·R + 0.2·A + 0.1·L + 0.05·ℓ

Where:
  P = Polarity Resonance (cosine similarity)
  R = Realm Affinity (categorical)
  A = Adjacency Overlap (Jaccard)
  L = Luminosity Proximity (density distance)
  ℓ = Lineage Affinity (exponential decay)

Status: Phase 1 Mathematical Validation COMPLETE; proceeding with Phase 2 robustness
"""

import math
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import json


# ============================================================================
# COMPONENT 1: POLARITY RESONANCE
# ============================================================================

def compute_polarity_vector(bitchain: Dict) -> List[float]:
    """
    Extract 7-dimensional polarity vector from bit-chain coordinates.
    
    Vector components (normalized to [0, 1] or [-1, 1] range):
    [realm_ord, lineage_norm, adjacency_density, horizon_ord, 
     resonance, velocity, density]
    
    Args:
        bitchain: BitChain dict with coordinates
        
    Returns:
        7-element list representing polarity direction in coordinate space
    """
    coords = bitchain.get('coordinates', {})
    
    # Realm: ordinal encoding
    realm_map = {'data': 0, 'narrative': 1, 'system': 2, 
                 'faculty': 3, 'event': 4, 'pattern': 5, 'void': 6}
    realm_ord = realm_map.get(coords.get('realm', 'void'), 6) / 6.0
    
    # Lineage: normalize to [0, 1]
    lineage_norm = min(coords.get('lineage', 0) / 100.0, 1.0)
    
    # Adjacency: density of neighbor set
    adjacency = coords.get('adjacency', [])
    adjacency_density = min(len(adjacency) / 5.0, 1.0)  # Max 5 neighbors normalized
    
    # Horizon: ordinal encoding
    horizon_map = {'genesis': 0, 'emergence': 1, 'peak': 2, 
                   'decay': 3, 'crystallization': 4}
    horizon_ord = horizon_map.get(coords.get('horizon', 'genesis'), 0) / 4.0
    
    # Direct coordinate values (already in proper ranges)
    resonance = coords.get('resonance', 0.0)  # [-1, 1]
    velocity = coords.get('velocity', 0.0)    # [-1, 1]
    density = coords.get('density', 0.5)      # [0, 1]
    
    return [realm_ord, lineage_norm, adjacency_density, horizon_ord, 
            resonance, velocity, density]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Formula: cos(θ) = (u·v) / (|u| × |v|)
    
    Args:
        vec1, vec2: Lists of floats (same length)
        
    Returns:
        Float in [-1.0, 1.0] where 1.0 = identical, 0.0 = orthogonal, -1.0 = opposite
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vector length mismatch: {len(vec1)} vs {len(vec2)}")
    
    # Dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Magnitudes
    mag1 = math.sqrt(sum(a ** 2 for a in vec1))
    mag2 = math.sqrt(sum(b ** 2 for b in vec2))
    
    # Handle zero vectors
    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0
    
    # Clamp to [-1, 1] to avoid floating-point errors
    result = dot_product / (mag1 * mag2)
    return max(-1.0, min(1.0, result))


def polarity_resonance(bc1: Dict, bc2: Dict) -> float:
    """
    Compute polarity resonance between two bit-chains.
    
    This is the PRIMARY signal in entanglement detection (weight: 0.3).
    
    Mathematical property: Symmetric, bounded [-1, 1]
    
    Args:
        bc1, bc2: BitChain dictionaries
        
    Returns:
        Polarity resonance score in [0.0, 1.0] (shifted from [-1, 1])
    """
    vec1 = compute_polarity_vector(bc1)
    vec2 = compute_polarity_vector(bc2)
    
    # Cosine similarity returns [-1, 1], shift to [0, 1] for consistency
    raw_score = cosine_similarity(vec1, vec2)
    
    # Shift from [-1, 1] to [0, 1]
    shifted_score = (raw_score + 1.0) / 2.0
    
    return shifted_score


# ============================================================================
# COMPONENT 2: REALM AFFINITY
# ============================================================================

# Realm adjacency graph (symmetric)
REALM_ADJACENCY = {
    'data': {'data', 'narrative', 'system', 'event', 'pattern'},
    'narrative': {'data', 'narrative', 'system', 'faculty', 'event', 'pattern'},
    'system': {'data', 'system', 'faculty', 'pattern', 'void'},
    'faculty': {'narrative', 'system', 'faculty', 'event'},
    'event': {'data', 'narrative', 'faculty', 'event', 'pattern'},
    'pattern': {'data', 'narrative', 'system', 'event', 'pattern', 'void'},
    'void': {'system', 'pattern', 'void'},
}


def realm_affinity(bc1: Dict, bc2: Dict) -> float:
    """
    Compute realm affinity between two bit-chains.
    
    Formula:
      1.0 if same realm
      0.7 if adjacent realm
      0.0 if orthogonal
    
    Mathematical property: Symmetric, bounded [0, 1]
    
    Args:
        bc1, bc2: BitChain dictionaries
        
    Returns:
        Realm affinity score in {0.0, 0.7, 1.0}
    """
    realm1 = bc1.get('coordinates', {}).get('realm', 'void')
    realm2 = bc2.get('coordinates', {}).get('realm', 'void')
    
    if realm1 == realm2:
        return 1.0
    
    # Check adjacency (symmetric)
    if realm2 in REALM_ADJACENCY.get(realm1, set()):
        return 0.7
    
    return 0.0


# ============================================================================
# COMPONENT 3: ADJACENCY OVERLAP
# ============================================================================

def jaccard_similarity(set1: Set, set2: Set) -> float:
    """
    Compute Jaccard similarity between two sets.
    
    Formula: J(A,B) = |A∩B| / |A∪B|
    
    Edge cases:
      - Both empty: return 1.0 (both isolated, thus similar)
      - One empty: return 0.0 (one isolated, one connected)
    
    Args:
        set1, set2: Sets of hashable elements
        
    Returns:
        Jaccard similarity in [0.0, 1.0]
    """
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        # Both sets empty
        return 1.0
    
    return intersection / union


def adjacency_overlap(bc1: Dict, bc2: Dict) -> float:
    """
    Compute adjacency overlap (Jaccard similarity of neighbor sets).
    
    This is a STRONG signal in entanglement detection (weight: 0.25).
    "Guilt by association" — shared neighbors = strong relationship indicator.
    
    Mathematical property: Symmetric, bounded [0, 1]
    
    Args:
        bc1, bc2: BitChain dictionaries
        
    Returns:
        Adjacency overlap score in [0.0, 1.0]
    """
    adj1 = set(bc1.get('coordinates', {}).get('adjacency', []))
    adj2 = set(bc2.get('coordinates', {}).get('adjacency', []))
    
    return jaccard_similarity(adj1, adj2)


# ============================================================================
# COMPONENT 4: LUMINOSITY PROXIMITY
# ============================================================================

def luminosity_proximity(bc1: Dict, bc2: Dict) -> float:
    """
    Compute luminosity proximity (compression state similarity).
    
    Formula: L = 1.0 - |density1 - density2|
    
    Interpretation:
      - 1.0 = same compression state
      - 0.5 = 0.5 density difference
      - 0.0 = opposite compression (raw vs. mist)
    
    Mathematical property: Symmetric, bounded [0, 1]
    
    Args:
        bc1, bc2: BitChain dictionaries
        
    Returns:
        Luminosity proximity score in [0.0, 1.0]
    """
    density1 = bc1.get('coordinates', {}).get('density', 0.5)
    density2 = bc2.get('coordinates', {}).get('density', 0.5)
    
    distance = abs(density1 - density2)
    score = 1.0 - distance
    
    return max(0.0, min(1.0, score))


# ============================================================================
# COMPONENT 5: LINEAGE AFFINITY
# ============================================================================

def lineage_affinity(bc1: Dict, bc2: Dict, decay_base: float = 0.9) -> float:
    """
    Compute lineage affinity (generational closeness).
    
    Formula: ℓ = decay_base ^ |lineage1 - lineage2|
    
    Decay analysis:
      Distance 0: 1.00 (siblings, strongest)
      Distance 1: 0.90 (parent-child)
      Distance 2: 0.81 (grandparent-grandchild)
      Distance 5: 0.59 (distant ancestor)
      Distance 10: 0.35 (very distant)
    
    Mathematical property: Symmetric, bounded (0, 1]
    
    Args:
        bc1, bc2: BitChain dictionaries
        decay_base: Exponential decay base (default 0.9)
        
    Returns:
        Lineage affinity score in (0.0, 1.0]
    """
    lineage1 = bc1.get('coordinates', {}).get('lineage', 0)
    lineage2 = bc2.get('coordinates', {}).get('lineage', 0)
    
    distance = abs(lineage1 - lineage2)
    score = decay_base ** distance
    
    return max(0.0, min(1.0, score))


# ============================================================================
# MAIN ENTANGLEMENT SCORE FUNCTION
# ============================================================================

@dataclass
class EntanglementScore:
    """Results of entanglement score computation with breakdown."""
    bitchain1_id: str
    bitchain2_id: str
    total_score: float
    polarity_resonance: float
    realm_affinity: float
    adjacency_overlap: float
    luminosity_proximity: float
    lineage_affinity: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'bitchain1_id': self.bitchain1_id,
            'bitchain2_id': self.bitchain2_id,
            'total_score': round(self.total_score, 8),
            'components': {
                'polarity_resonance': round(self.polarity_resonance, 8),
                'realm_affinity': round(self.realm_affinity, 8),
                'adjacency_overlap': round(self.adjacency_overlap, 8),
                'luminosity_proximity': round(self.luminosity_proximity, 8),
                'lineage_affinity': round(self.lineage_affinity, 8),
            }
        }


def compute_entanglement_score(bc1: Dict, bc2: Dict) -> EntanglementScore:
    """
    Compute entanglement score between two bit-chains.
    
    Formula (V2 — Tuned for separation):
    E(B1, B2) = 0.5·P + 0.15·R + 0.2·A + 0.1·L + 0.05·ℓ
    
    Where:
      P = Polarity Resonance (cosine similarity) [weight: 0.5 — PRIMARY, STRONGEST]
      R = Realm Affinity [weight: 0.15 — SECONDARY]
      A = Adjacency Overlap (Jaccard) [weight: 0.2 — STRONG]
      L = Luminosity Proximity [weight: 0.1 — TERTIARY]
      ℓ = Lineage Affinity [weight: 0.05 — WEAK]
    
    Changes from V1:
      - Increased P weight: 0.3 → 0.5 (strongest signal for separation)
      - Decreased R weight: 0.2 → 0.15 (realm overlap is too common)
      - Decreased A weight: 0.25 → 0.2 (Jaccard similarity too generous)
      - Kept L: 0.15 → 0.1 (minor adjustment)
      - Decreased ℓ: 0.1 → 0.05 (lineage distance rarely separates)
    
    Mathematical properties:
      - Deterministic: same input always gives same output
      - Symmetric: E(B1, B2) = E(B2, B1)
      - Bounded: E ∈ [0.0, 1.0] for all valid inputs
    
    Args:
        bc1, bc2: BitChain dictionaries
        
    Returns:
        EntanglementScore object with total score and component breakdown
    """
    # Compute component scores
    p_score = polarity_resonance(bc1, bc2)
    r_score = realm_affinity(bc1, bc2)
    a_score = adjacency_overlap(bc1, bc2)
    l_score = luminosity_proximity(bc1, bc2)
    lineage_score = lineage_affinity(bc1, bc2)
    
    # Weighted sum (weights sum to 1.0) — TUNED FOR SEPARATION
    total = (0.5 * p_score + 
             0.15 * r_score + 
             0.2 * a_score + 
             0.1 * l_score + 
             0.05 * lineage_score)
    
    # Clamp to [0, 1]
    total = max(0.0, min(1.0, total))
    
    bc1_id = bc1.get('id', 'unknown')
    bc2_id = bc2.get('id', 'unknown')
    
    return EntanglementScore(
        bitchain1_id=bc1_id,
        bitchain2_id=bc2_id,
        total_score=total,
        polarity_resonance=p_score,
        realm_affinity=r_score,
        adjacency_overlap=a_score,
        luminosity_proximity=l_score,
        lineage_affinity=lineage_score,
    )


# ============================================================================
# ENTANGLEMENT DETECTION
# ============================================================================

class EntanglementDetector:
    """
    Main detector class for finding entangled bit-chains.
    
    Usage:
        detector = EntanglementDetector(threshold=0.85)
        entangled = detector.detect(bitchains)
    """
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize detector with threshold.
        
        Args:
            threshold: Score threshold for declaring entanglement (default 0.85)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be in [0.0, 1.0], got {threshold}")
        
        self.threshold = threshold
        self.scores: List[EntanglementScore] = []
    
    def detect(self, bitchains: List[Dict]) -> List[Tuple[str, str, float]]:
        """
        Find all entangled pairs above threshold.
        
        Args:
            bitchains: List of BitChain dictionaries
            
        Returns:
            List of (bitchain1_id, bitchain2_id, score) tuples where score >= threshold
        """
        self.scores = []
        entangled_pairs = []
        
        # All-pairs comparison (O(N²))
        for i in range(len(bitchains)):
            for j in range(i + 1, len(bitchains)):
                score = compute_entanglement_score(bitchains[i], bitchains[j])
                self.scores.append(score)
                
                if score.total_score >= self.threshold:
                    entangled_pairs.append((
                        score.bitchain1_id,
                        score.bitchain2_id,
                        score.total_score
                    ))
        
        return entangled_pairs
    
    def get_score_distribution(self) -> Dict:
        """
        Get statistics on score distribution.
        
        Returns:
            Dictionary with min, max, mean, median, std dev
        """
        if not self.scores:
            return {}
        
        scores = [s.total_score for s in self.scores]
        scores.sort()
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = math.sqrt(variance)
        median = scores[len(scores) // 2]
        
        return {
            'count': len(scores),
            'min': round(min(scores), 8),
            'max': round(max(scores), 8),
            'mean': round(mean, 8),
            'median': round(median, 8),
            'std_dev': round(std_dev, 8),
        }
    
    def get_all_scores(self) -> List[Dict]:
        """Get all computed scores as list of dicts."""
        return [s.to_dict() for s in self.scores]
    
    def score(self, bitchain1: Dict, bitchain2: Dict) -> float:
        """
        Convenience method to score a single pair without detection.
        
        Args:
            bitchain1, bitchain2: BitChain dictionaries
            
        Returns:
            Total entanglement score (float between 0.0 and 1.0)
        """
        result = compute_entanglement_score(bitchain1, bitchain2)
        return result.total_score


# ============================================================================
# VALIDATION METRICS
# ============================================================================

@dataclass
class ValidationResult:
    """Results of validation experiment."""
    threshold: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    runtime_seconds: float
    
    @property
    def passed(self) -> bool:
        """Check if validation passed targets."""
        return self.precision >= 0.90 and self.recall >= 0.85
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'threshold': self.threshold,
            'confusion_matrix': {
                'true_positives': self.true_positives,
                'false_positives': self.false_positives,
                'false_negatives': self.false_negatives,
                'true_negatives': self.true_negatives,
            },
            'metrics': {
                'precision': round(self.precision, 4),
                'recall': round(self.recall, 4),
                'f1_score': round(self.f1_score, 4),
                'accuracy': round(self.accuracy, 4),
            },
            'runtime_seconds': round(self.runtime_seconds, 4),
            'passed': self.passed,
        }


def compute_validation_metrics(
    true_pairs: Set[Tuple[str, str]],
    detected_pairs: Set[Tuple[str, str]],
    total_possible_pairs: int,
) -> ValidationResult:
    """
    Compute precision/recall metrics from true and detected pairs.
    
    Args:
        true_pairs: Set of (id1, id2) that are truly entangled
        detected_pairs: Set of (id1, id2) that algorithm detected
        total_possible_pairs: Total number of pairs in dataset
        
    Returns:
        ValidationResult with all metrics
    """
    # Normalize pairs (always smaller ID first)
    def normalize(pair):
        return tuple(sorted(pair))
    
    true_set = set(normalize(p) for p in true_pairs)
    detected_set = set(normalize(p) for p in detected_pairs)
    
    # Confusion matrix
    true_positives = len(true_set & detected_set)
    false_positives = len(detected_set - true_set)
    false_negatives = len(true_set - detected_set)
    true_negatives = total_possible_pairs - true_positives - false_positives - false_negatives
    
    # Metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    accuracy = (true_positives + true_negatives) / total_possible_pairs if total_possible_pairs > 0 else 0.0
    
    # F1 score
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    return ValidationResult(
        threshold=0.0,  # Will be set by caller
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        true_negatives=true_negatives,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        accuracy=accuracy,
        runtime_seconds=0.0,  # Will be set by caller
    )