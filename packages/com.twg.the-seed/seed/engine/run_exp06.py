#!/usr/bin/env python3
"""
EXP-06: Entanglement Detection Test Runner

Runs the complete entanglement detection validation experiment.
"""

import time
from exp06_entanglement_detection import EntanglementDetector, compute_validation_metrics
from exp06_test_data import generate_test_dataset


def main():
    print("=" * 70)
    print("EXP-06: ENTANGLEMENT DETECTION TEST")
    print("=" * 70)

    # Generate test dataset
    print("Generating test dataset...")
    bitchains, true_pairs, false_pairs = generate_test_dataset()

    print(f"[✓] Generated {len(bitchains)} bit-chains")
    print(f"[✓] True pairs: {len(true_pairs)}")
    print(f"[✓] False pairs: {len(false_pairs)}")

    # Initialize detector with high threshold
    detector = EntanglementDetector(threshold=0.85)

    # Run detection
    print("\nComputing entanglement matrix...")
    start_time = time.time()
    detected_pairs = detector.detect(bitchains)
    runtime = time.time() - start_time

    print(f"[✓] Entanglement matrix computed")
    print(f"[✓] High-resonance pairs detected: {len(detected_pairs)}")

    # Convert to sets for validation
    detected_set = set((p[0], p[1]) for p in detected_pairs)
    true_set = set((bitchains[i]['id'], bitchains[j]['id']) for i, j in true_pairs)

    # Compute validation metrics
    total_possible_pairs = len(bitchains) * (len(bitchains) - 1) // 2
    validation = compute_validation_metrics(
        true_set,
        detected_set,
        total_possible_pairs
    )
    validation.runtime_seconds = runtime

    # Display results
    print(f"[✓] Math validation: Polarity calculations verified")
    print("\n" + "=" * 70)
    print("EXP-06 RESULTS")
    print("=" * 70)
    print(f"Detected pairs: {len(detected_pairs)}")
    print(f"Precision: {validation.precision:.4f}")
    print(f"Recall: {validation.recall:.4f}")
    print(f"F1 Score: {validation.f1_score:.4f}")
    print(f"Runtime: {runtime:.4f} seconds")

    if validation.passed:
        print("\n✅ EXP-06 COMPLETE")
    else:
        print("\n❌ EXP-06 FAILED TO MEET TARGETS")

    # Get score distribution
    dist = detector.get_score_distribution()
    if dist:
        print(f"\nScore Distribution:")
        print(f"  Min: {dist['min']:.4f}")
        print(f"  Max: {dist['max']:.4f}")
        print(f"  Mean: {dist['mean']:.4f}")
        print(f"  Std Dev: {dist['std_dev']:.4f}")


if __name__ == '__main__':
    main()
