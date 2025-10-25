"""
Analyze full score distribution across all pairs
"""

import sys
sys.path.insert(0, 'seed/engine')

from exp06_entanglement_detection import compute_entanglement_score
from exp06_test_data import generate_test_dataset

print("Generating dataset...")
bitchains, true_indices, false_indices = generate_test_dataset()

print(f"Computing all pair scores...")
scores = []
true_scores = []
false_scores = []

# All true pairs
for idx1, idx2 in true_indices:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2]).total_score
    scores.append(score)
    true_scores.append(score)

# All false pairs
for idx1, idx2 in false_indices:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2]).total_score
    scores.append(score)
    false_scores.append(score)

# Sample of remaining pairs (too many to compute all)
remaining_count = 0
remaining_scores = []
for i in range(80, len(bitchains)):
    for j in range(i+1, min(i+3, len(bitchains))):  # Just 2 per i
        score = compute_entanglement_score(bitchains[i], bitchains[j]).total_score
        remaining_scores.append(score)
        remaining_count += 1

# Histogram
print("\nScore Distribution:")
print("="*60)

def histogram_bar(score_min, score_max, scores_list):
    count = len([s for s in scores_list if score_min <= s < score_max])
    bar = '*' * (count // 5 + 1) if count > 0 else ''
    return f"{score_min:.2f}-{score_max:.2f}: {count:4d} {bar}"

all_scores = true_scores + false_scores + remaining_scores
bins = [(i*0.1, (i+1)*0.1) for i in range(10)]

for lo, hi in bins:
    print(histogram_bar(lo, hi, all_scores))

print("\nStatistics:")
print(f"True pairs:     {len(true_scores)} items, all = {true_scores[0]:.4f}")
print(f"False pairs:    {len(false_scores)} items, all = {false_scores[0]:.4f}")
print(f"Remaining sampled: {len(remaining_scores)} items")
print(f"  Min: {min(remaining_scores):.4f}")
print(f"  Max: {max(remaining_scores):.4f}")
print(f"  Mean: {sum(remaining_scores)/len(remaining_scores):.4f}")

# Count how many scores are >= threshold
print("\nFalse positive counts by threshold:")
for threshold in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
    count = len([s for s in remaining_scores if s >= threshold])
    print(f"  theta>={threshold:.2f}: {count} scores")

print("\nConclusion:")
print("If remaining scores span 0.5-0.9, we'll get ~80 FP at any reasonable threshold.")
print("This makes 90% precision impossible with current dataset design.")
print("\nSolution: Unrelated pairs need to score < 0.3, well below false pairs (0.19).")