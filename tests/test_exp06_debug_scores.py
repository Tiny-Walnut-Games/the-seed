"""
Debug script: Analyze score distribution across all pair types
"""

import sys
sys.path.insert(0, 'seed/engine')

from exp06_entanglement_detection import compute_entanglement_score
from exp06_test_data import generate_test_dataset
import statistics

bitchains, true_indices, false_indices = generate_test_dataset()

# Get scores for each group
true_scores = []
false_scores = []
unrelated_scores = []

# True pairs (first 40 bit-chains form 20 pairs)
print("Sampling TRUE pairs:")
for idx1, idx2 in true_indices[:5]:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
    true_scores.append(score.total_score)
    print(f"  P={score.polarity_resonance:.3f}, R={score.realm_affinity:.3f}, "
          f"A={score.adjacency_overlap:.3f}, L={score.luminosity_proximity:.3f}, "
          f"ℓ={score.lineage_affinity:.3f} → Total={score.total_score:.3f}")

print(f"\nTrue pairs (n={len(true_indices)}): mean={statistics.mean(true_scores):.4f}")

# False pairs (next 40 bit-chains form 20 pairs)
print("\nSampling FALSE pairs:")
for idx1, idx2 in false_indices[:5]:
    score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
    false_scores.append(score.total_score)
    print(f"  P={score.polarity_resonance:.3f}, R={score.realm_affinity:.3f}, "
          f"A={score.adjacency_overlap:.3f}, L={score.luminosity_proximity:.3f}, "
          f"ℓ={score.lineage_affinity:.3f} → Total={score.total_score:.3f}")

print(f"\nFalse pairs (n={len(false_indices)}): mean={statistics.mean(false_scores):.4f}")

# Unrelated pairs (last 60 bit-chains)
print("\nSampling UNRELATED pairs:")
unrelated_start = 80
for i in range(unrelated_start, min(unrelated_start + 5, len(bitchains) - 1)):
    for j in range(i + 1, min(i + 2, len(bitchains))):
        score = compute_entanglement_score(bitchains[i], bitchains[j])
        unrelated_scores.append(score.total_score)
        print(f"  P={score.polarity_resonance:.3f}, R={score.realm_affinity:.3f}, "
              f"A={score.adjacency_overlap:.3f}, L={score.luminosity_proximity:.3f}, "
              f"ℓ={score.lineage_affinity:.3f} → Total={score.total_score:.3f}")

print(f"\nUnrelated pairs (sampled n={len(unrelated_scores)}): mean={statistics.mean(unrelated_scores):.4f}")

print("\n" + "="*70)
print("SCORE DISTRIBUTION SUMMARY")
print("="*70)
print(f"True pairs:     min={min(true_scores):.4f}, max={max(true_scores):.4f}, mean={statistics.mean(true_scores):.4f}")
print(f"False pairs:    min={min(false_scores):.4f}, max={max(false_scores):.4f}, mean={statistics.mean(false_scores):.4f}")
print(f"Unrelated (sample): min={min(unrelated_scores):.4f}, max={max(unrelated_scores):.4f}, mean={statistics.mean(unrelated_scores):.4f}")

print(f"\nSeparation (True - False): {statistics.mean(true_scores) - statistics.mean(false_scores):.4f}")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)
print("Problem: Even 'unrelated' pairs are scoring too high (overlap with true pairs)")
print("Likely cause: Weights on realm_affinity and adjacency_overlap are too high")
print("  - Many random pairs happen to share realms (same domain)")
print("  - Many random pairs happen to have Jaccard > 0.3")
print("\nSolution: Increase weight on polarity_resonance (strongest signal)")
print("         Decrease weight on realm_affinity (weakest separator)")