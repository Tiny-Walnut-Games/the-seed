"""
EXP-06: Final Validation with Threshold Sweep

Tests:
- Threshold sweep across [0.30-0.95]
- Confusion matrix at optimal threshold (0.85)
- Score distribution analysis
- Full audit logging with artifact generation
"""

import sys
import pytest

sys.path.insert(0, 'seed/engine')

from exp06_entanglement_detection import (
    EntanglementDetector,
    compute_validation_metrics,
    compute_entanglement_score,
)
from exp06_test_data import generate_test_dataset
from exp06_audit_logger import AuditLogger


@pytest.fixture(scope="module")
def audit_logger():
    """Create audit logger for this test session."""
    return AuditLogger()


@pytest.fixture(scope="module")
def test_dataset(audit_logger):
    """Generate test dataset once per module"""
    print("\nGenerating dataset...")
    bitchains, true_indices, false_indices = generate_test_dataset()
    
    def normalize_pair(idx1, idx2):
        return tuple(sorted([bitchains[idx1]['id'], bitchains[idx2]['id']]))
    
    true_pairs_set = set(normalize_pair(i, j) for i, j in true_indices)
    false_pairs_set = set(normalize_pair(i, j) for i, j in false_indices)
    total_pairs = len(bitchains) * (len(bitchains) - 1) // 2
    
    print(f"Total pairs: {total_pairs}")
    print(f"True pairs: {len(true_pairs_set)}")
    print(f"False pairs: {len(false_pairs_set)}")
    
    audit_logger.log_section("DATASET GENERATION")
    audit_logger.log_lines.append(f"\nBit-chains generated: {len(bitchains)}")
    audit_logger.log_lines.append(f"True pairs: {len(true_pairs_set)}")
    audit_logger.log_lines.append(f"False pairs: {len(false_pairs_set)}")
    audit_logger.log_lines.append(f"Total possible pairs: {total_pairs}")
    
    # Log all scores for transparency
    audit_logger.log_section("ALL PAIR SCORES")
    
    # True pairs
    audit_logger.log_lines.append("\nTRUE PAIRS (expected high scores ~0.91):")
    for idx1, idx2 in sorted(true_indices):
        score_obj = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
        audit_logger.log_calculation(
            'true',
            bitchains[idx1]['id'],
            bitchains[idx2]['id'],
            {
                'P': score_obj.polarity_resonance,
                'R': score_obj.realm_affinity,
                'A': score_obj.adjacency_overlap,
                'L': score_obj.luminosity_proximity,
                'l': score_obj.lineage_affinity,
            },
            score_obj.total_score
        )
    
    # False pairs
    audit_logger.log_lines.append("\nFALSE PAIRS (expected low scores ~0.19):")
    for idx1, idx2 in sorted(false_indices):
        score_obj = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
        audit_logger.log_calculation(
            'false',
            bitchains[idx1]['id'],
            bitchains[idx2]['id'],
            {
                'P': score_obj.polarity_resonance,
                'R': score_obj.realm_affinity,
                'A': score_obj.adjacency_overlap,
                'L': score_obj.luminosity_proximity,
                'l': score_obj.lineage_affinity,
            },
            score_obj.total_score
        )
    
    # Log statistics
    audit_logger.log_statistics()
    
    return {
        'bitchains': bitchains,
        'true_pairs_set': true_pairs_set,
        'false_pairs_set': false_pairs_set,
        'total_pairs': total_pairs,
        'true_indices': true_indices,
        'false_indices': false_indices,
    }


def test_threshold_sweep(test_dataset, audit_logger):
    """
    Test: Threshold sweep across [0.30-0.95] to find optimal.
    
    Expected: At threshold 0.85:
      - Precision ≥ 90%
      - Recall ≥ 85%
      - TP=20, FP=0
    """
    bitchains = test_dataset['bitchains']
    true_pairs_set = test_dataset['true_pairs_set']
    total_pairs = test_dataset['total_pairs']
    
    print("\n" + "="*80)
    print("THRESHOLD SWEEP")
    print("="*80)
    
    audit_logger.log_section("THRESHOLD SWEEP ANALYSIS")
    
    best_threshold = None
    best_metrics = None
    
    for threshold in [0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]:
        detector = EntanglementDetector(threshold=threshold)
        detected = detector.detect(bitchains)
        detected_set = set((d[0], d[1]) for d in detected)
        
        metrics = compute_validation_metrics(true_pairs_set, detected_set, total_pairs)
        
        status = "✓" if (metrics.precision >= 0.90 and metrics.recall >= 0.85) else "✗"
        
        print(f"\nthreshold={threshold:.2f}: {status}")
        print(f"  Detected: {len(detected_set)}")
        print(f"  TP: {metrics.true_positives}, FP: {metrics.false_positives}")
        print(f"  Precision: {metrics.precision:.4f} ({metrics.precision*100:.1f}%)")
        print(f"  Recall: {metrics.recall:.4f} ({metrics.recall*100:.1f}%)")
        print(f"  F1: {metrics.f1_score:.4f}")
        
        # Log to audit
        audit_logger.log_threshold_sweep(
            threshold,
            len(detected_set),
            {
                'true_positives': metrics.true_positives,
                'false_positives': metrics.false_positives,
                'false_negatives': metrics.false_negatives,
                'true_negatives': metrics.true_negatives,
                'precision': metrics.precision,
                'recall': metrics.recall,
                'f1_score': metrics.f1_score,
                'accuracy': metrics.accuracy,
                'passed': metrics.passed,
            }
        )
        
        if metrics.passed and best_threshold is None:
            best_threshold = threshold
            best_metrics = metrics
            print(f"  >>> OPTIMAL FOUND <<<")
    
    # Verify optimal threshold meets targets
    assert best_threshold is not None, "No threshold met target criteria"
    assert best_metrics.precision >= 0.90, f"Precision {best_metrics.precision} < 0.90"
    assert best_metrics.recall >= 0.85, f"Recall {best_metrics.recall} < 0.85"
    assert best_metrics.true_positives == 20, f"TP {best_metrics.true_positives} != 20"
    assert best_metrics.false_positives == 0, f"FP {best_metrics.false_positives} != 0"
    
    print(f"\n*** TARGETS MET at threshold {best_threshold:.2f} ***")


def test_confusion_matrix(test_dataset, audit_logger):
    """
    Test: Confusion matrix at optimal threshold (0.85).
    
    Expected:
      - TP = 20 (true positives)
      - FP = 0  (false positives)
      - FN = 0  (false negatives)
      - TN ≈ 7100 (true negatives)
    """
    bitchains = test_dataset['bitchains']
    true_pairs_set = test_dataset['true_pairs_set']
    total_pairs = test_dataset['total_pairs']
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX (Threshold 0.85)")
    print("="*80)
    
    threshold = 0.85
    detector = EntanglementDetector(threshold=threshold)
    detected = detector.detect(bitchains)
    detected_set = set((d[0], d[1]) for d in detected)
    
    metrics = compute_validation_metrics(true_pairs_set, detected_set, total_pairs)
    
    print(f"\nConfusion Matrix:")
    print(f"  True Positives:  {metrics.true_positives}")
    print(f"  False Positives: {metrics.false_positives}")
    print(f"  False Negatives: {metrics.false_negatives}")
    print(f"  True Negatives:  {metrics.true_negatives}")
    
    print(f"\nMetrics:")
    print(f"  Precision: {metrics.precision:.4f} ({metrics.precision*100:.1f}%)")
    print(f"  Recall:    {metrics.recall:.4f} ({metrics.recall*100:.1f}%)")
    print(f"  F1 Score:  {metrics.f1_score:.4f}")
    print(f"  Accuracy:  {metrics.accuracy:.4f} ({metrics.accuracy*100:.1f}%)")
    
    # Log confusion matrix
    audit_logger.log_section("CONFUSION MATRIX (Threshold 0.85)")
    audit_logger.log_confusion_matrix(threshold, {
        'true_positives': metrics.true_positives,
        'false_positives': metrics.false_positives,
        'false_negatives': metrics.false_negatives,
        'true_negatives': metrics.true_negatives,
        'precision': metrics.precision,
        'recall': metrics.recall,
        'f1_score': metrics.f1_score,
        'accuracy': metrics.accuracy,
    })
    
    # Verify perfect separation
    assert metrics.true_positives == 20, f"TP: expected 20, got {metrics.true_positives}"
    assert metrics.false_positives == 0, f"FP: expected 0, got {metrics.false_positives}"
    assert metrics.false_negatives == 0, f"FN: expected 0, got {metrics.false_negatives}"
    assert metrics.precision == 1.0, f"Precision: expected 1.0, got {metrics.precision}"
    assert metrics.recall == 1.0, f"Recall: expected 1.0, got {metrics.recall}"
    assert metrics.f1_score == 1.0, f"F1: expected 1.0, got {metrics.f1_score}"
    
    print(f"\n✓ Perfect separation achieved!")


def test_score_distribution(test_dataset):
    """
    Test: Score distribution - true pairs vs false pairs.
    
    Expected:
      - True pair scores centered around 0.91
      - False pair scores centered around 0.19
      - Clear separation (4.67× ratio)
    """
    from exp06_entanglement_detection import compute_entanglement_score
    import statistics
    
    bitchains = test_dataset['bitchains']
    true_indices = [i for i, bc in enumerate(bitchains) if bc.get('label') == 'true'][:10]
    false_indices = [i for i, bc in enumerate(bitchains) if bc.get('label') == 'false'][:10]
    
    print("\n" + "="*80)
    print("SCORE DISTRIBUTION")
    print("="*80)
    
    # Compute true pair scores
    true_scores = []
    for i in range(len(true_indices)):
        for j in range(i + 1, len(true_indices)):
            score = compute_entanglement_score(
                bitchains[true_indices[i]],
                bitchains[true_indices[j]]
            )
            true_scores.append(score.total_score)
    
    # Compute false pair scores
    false_scores = []
    for i in range(len(false_indices)):
        for j in range(i + 1, len(false_indices)):
            score = compute_entanglement_score(
                bitchains[false_indices[i]],
                bitchains[false_indices[j]]
            )
            false_scores.append(score.total_score)
    
    if true_scores and false_scores:
        true_mean = statistics.mean(true_scores)
        false_mean = statistics.mean(false_scores)
        separation_ratio = true_mean / false_mean if false_mean > 0 else 0
        
        print(f"\nTrue pair scores:")
        print(f"  Mean: {true_mean:.4f}")
        print(f"  Min:  {min(true_scores):.4f}")
        print(f"  Max:  {max(true_scores):.4f}")
        print(f"  Count: {len(true_scores)}")
        
        print(f"\nFalse pair scores:")
        print(f"  Mean: {false_mean:.4f}")
        print(f"  Min:  {min(false_scores):.4f}")
        print(f"  Max:  {max(false_scores):.4f}")
        print(f"  Count: {len(false_scores)}")
        
        print(f"\nSeparation ratio: {separation_ratio:.2f}×")
        
        # Verify separation
        assert true_mean > 0.85, f"True pair mean {true_mean} should be > 0.85"
        assert false_mean < 0.30, f"False pair mean {false_mean} should be < 0.30"
        assert separation_ratio > 2.0, f"Separation {separation_ratio}× should be > 2.0×"
        
        print(f"\n✓ Score distribution validated!")
    else:
        print(f"\nNote: Skipped distribution test (limited sample size)")


def test_save_artifacts(test_dataset, audit_logger):
    """
    Final test: Save all audit logs and artifacts.
    
    This runs after all other tests to ensure complete data capture.
    """
    print("\n" + "="*80)
    print("SAVING ARTIFACTS")
    print("="*80)
    
    # Save log file
    log_file = audit_logger.save_log()
    print(f"\n✅ Log saved: {log_file}")
    
    # Save confusion matrix JSON
    cm_file = audit_logger.save_confusion_matrix_json(0.85)
    print(f"✅ Confusion matrix saved: {cm_file}")
    
    # Save threshold sweep JSON
    ts_file = audit_logger.save_threshold_sweep_json()
    print(f"✅ Threshold sweep saved: {ts_file}")
    
    # Save plots
    try:
        plot_files = audit_logger.save_plots()
        if plot_files:
            for plot_file in plot_files:
                print(f"✅ Plot saved: {plot_file}")
        else:
            print("⚠️  Plots not generated (matplotlib not available)")
    except Exception as e:
        print(f"⚠️  Error generating plots: {e}")
    
    print("\n" + "="*80)
    print("ARTIFACT GENERATION COMPLETE")
    print("="*80)
    print(f"\nAll artifacts saved to:")
    print(f"  Logs:      seed/logs/")
    print(f"  Artifacts: seed/artifacts/")
    print(f"\nFor full reproducibility, examine:")
    print(f"  1. {log_file} (all calculations)")
    print(f"  2. {cm_file} (confusion matrix with raw scores)")
    print(f"  3. seed/artifacts/*_histogram_*.png (score distribution)")
    print(f"  4. seed/artifacts/*_threshold_*.png (threshold analysis)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])