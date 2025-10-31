"""
Simple validation test without Unicode encoding issues
"""

import sys
sys.path.insert(0, 'seed/engine')

from exp06_entanglement_detection import (
    compute_entanglement_score,
    EntanglementDetector,
    compute_validation_metrics,
)
from exp06_test_data import generate_test_dataset
import time

print("Generating test dataset...")
bitchains, true_pair_indices, false_pair_indices = generate_test_dataset()
print(f"Generated {len(bitchains)} bit-chains")
print(f"True pairs: {len(true_pair_indices)}")
print(f"False pairs: {len(false_pair_indices)}")

# Sample scores
print("\nSampling scores...")
def normalize_pair(idx1, idx2):
    return tuple(sorted([bitchains[idx1]['id'], bitchains[idx2]['id']]))

# Get true pairs scores
true_scores = []
for idx1, idx2 in true_pair_indices[:3]:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
    true_scores.append(score.total_score)
    print(f"TRUE pair {idx1}-{idx2}: score={score.total_score:.4f}")

# Get false pairs scores
false_scores = []
for idx1, idx2 in false_pair_indices[:3]:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
    false_scores.append(score.total_score)
    print(f"FALSE pair {idx1}-{idx2}: score={score.total_score:.4f}")

# Test with different thresholds
print("\nTesting thresholds...")
thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]

true_pairs_set = set(normalize_pair(i, j) for i, j in true_pair_indices)
false_pairs_set = set(normalize_pair(i, j) for i, j in false_pair_indices)
total_pairs = len(bitchains) * (len(bitchains) - 1) // 2

for threshold in thresholds:
    detector = EntanglementDetector(threshold=threshold)
    detected = detector.detect(bitchains)
    detected_set = set((d[0], d[1]) for d in detected)
    
    metrics = compute_validation_metrics(true_pairs_set, detected_set, total_pairs)
    metrics.threshold = threshold
    
    status = "PASS" if metrics.passed else "FAIL"
    print(f"theta={threshold:.2f} | P={metrics.precision:.2%} | R={metrics.recall:.2%} | F1={metrics.f1_score:.4f} | {status}")

print("\nDone!")