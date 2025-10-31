"""
EXP-06: Entanglement Detection — Mathematical Validation

Tests that prove:
1. Score function is deterministic
2. Score function is symmetric
3. Score function is bounded [0, 1]
4. True pairs score higher than false pairs
5. Component functions are mathematically sound
6. Test dataset achieves precision/recall targets

Status: Mathematical proof phase (before full test harness)
"""

import pytest
import sys
import time
import json
from typing import List, Tuple, Dict
from datetime import datetime, timezone

# Add to path for imports
sys.path.insert(0, 'seed/engine')
sys.path.insert(0, 'seed/docs')

from exp06_entanglement_detection import (
    compute_entanglement_score,
    EntanglementDetector,
    compute_validation_metrics,
    polarity_resonance,
    realm_affinity,
    adjacency_overlap,
    luminosity_proximity,
    lineage_affinity,
)
from exp06_test_data import generate_test_dataset


# ============================================================================
# MATHEMATICAL PROPERTIES TESTS
# ============================================================================

@pytest.mark.integration
def test_determinism():
    """
    Test Claim 1: Score function is deterministic.
    
    Hypothesis: E(B1, B2) always returns the same value for identical inputs.
    """
    print("\n" + "="*70)
    print("TEST 1: DETERMINISM")
    print("="*70)
    
    bitchains, _, _ = generate_test_dataset()
    bc1, bc2 = bitchains[0], bitchains[1]
    
    # Compute score multiple times
    scores = []
    for i in range(10):
        score = compute_entanglement_score(bc1, bc2)
        scores.append(score.total_score)
    
    # All should be identical
    is_deterministic = len(set(scores)) == 1
    
    print(f"Computed 10 scores: {scores[:3]}... (showing first 3)")
    print(f"Unique values: {len(set(scores))}")
    print(f"✅ PASS: Deterministic" if is_deterministic else f"❌ FAIL: Non-deterministic")
    
    assert is_deterministic, "Score function is not deterministic"


@pytest.mark.integration
def test_symmetry():
    """
    Test Claim 2: Score function is symmetric.
    
    Hypothesis: E(B1, B2) = E(B2, B1)
    """
    print("\n" + "="*70)
    print("TEST 2: SYMMETRY")
    print("="*70)
    
    bitchains, _, _ = generate_test_dataset()
    
    all_symmetric = True
    failures = []
    
    # Test on first 20 pairs
    for i in range(10):
        for j in range(i + 1, 20):
            bc1, bc2 = bitchains[i], bitchains[j]
            
            score_12 = compute_entanglement_score(bc1, bc2).total_score
            score_21 = compute_entanglement_score(bc2, bc1).total_score
            
            if abs(score_12 - score_21) > 1e-10:
                all_symmetric = False
                failures.append((i, j, score_12, score_21))
    
    print(f"Tested {10 * 9 // 2} pairs")
    print(f"Failures: {len(failures)}")
    
    if failures:
        for i, j, s12, s21 in failures[:3]:
            print(f"  Pair ({i},{j}): E(B1,B2)={s12:.8f} vs E(B2,B1)={s21:.8f}")
    
    print(f"✅ PASS: Symmetric" if all_symmetric else f"❌ FAIL: Not symmetric")
    
    assert all_symmetric, f"Score function is not symmetric: {len(failures)} failures"


@pytest.mark.integration
def test_boundedness():
    """
    Test Claim 3: Score function is bounded [0, 1].
    
    Hypothesis: For all valid bit-chains, E(B1, B2) ∈ [0.0, 1.0]
    """
    print("\n" + "="*70)
    print("TEST 3: BOUNDEDNESS")
    print("="*70)
    
    bitchains, _, _ = generate_test_dataset()
    
    scores = []
    out_of_bounds = 0
    
    # Compute all pairs
    for i in range(len(bitchains)):
        for j in range(i + 1, len(bitchains)):
            score = compute_entanglement_score(bitchains[i], bitchains[j])
            total = score.total_score
            scores.append(total)
            
            if not (0.0 <= total <= 1.0):
                out_of_bounds += 1
    
    min_score = min(scores)
    max_score = max(scores)
    
    print(f"Total pairs tested: {len(scores)}")
    print(f"Score range: [{min_score:.8f}, {max_score:.8f}]")
    print(f"Out of bounds: {out_of_bounds}")
    print(f"✅ PASS: All scores in [0,1]" if out_of_bounds == 0 else f"❌ FAIL: {out_of_bounds} out of bounds")
    
    assert out_of_bounds == 0, f"Found {out_of_bounds} scores out of bounds [0, 1]"
    assert min_score >= 0.0, f"Min score {min_score} < 0.0"
    assert max_score <= 1.0, f"Max score {max_score} > 1.0"


@pytest.mark.integration
def test_component_boundedness():
    """
    Test: Each component function is bounded [0, 1].
    """
    print("\n" + "="*70)
    print("TEST 4: COMPONENT BOUNDEDNESS")
    print("="*70)
    
    bitchains, _, _ = generate_test_dataset()
    
    def check_component(name, func, bc1, bc2):
        score = func(bc1, bc2)
        if not (0.0 <= score <= 1.0):
            print(f"  ❌ {name}: {score} (out of bounds)")
            return False
        return True
    
    all_ok = True
    sample_size = min(20, len(bitchains) // 2)
    
    for i in range(sample_size):
        bc1 = bitchains[i]
        bc2 = bitchains[i + 1]
        
        ok = True
        ok &= check_component("P (polarity)", polarity_resonance, bc1, bc2)
        ok &= check_component("R (realm)", realm_affinity, bc1, bc2)
        ok &= check_component("A (adjacency)", adjacency_overlap, bc1, bc2)
        ok &= check_component("L (luminosity)", luminosity_proximity, bc1, bc2)
        ok &= check_component("ℓ (lineage)", lineage_affinity, bc1, bc2)
        
        all_ok &= ok
    
    print(f"Tested {sample_size} pairs, all components")
    print(f"✅ PASS: All components bounded" if all_ok else f"❌ FAIL: Some components out of bounds")
    
    assert all_ok, "Some component functions produced out-of-bounds values"


@pytest.mark.integration
def test_separation():
    """
    Test Claim 4: True pairs score higher than false pairs (on average).
    
    Hypothesis: E[score_true] > E[score_false]
    """
    print("\n" + "="*70)
    print("TEST 5: SEPARATION")
    print("="*70)
    
    bitchains, true_pair_indices, false_pair_indices = generate_test_dataset()
    
    # Score all true pairs
    true_scores = []
    for idx1, idx2 in true_pair_indices:
        score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
        true_scores.append(score.total_score)
    
    # Score all false pairs
    false_scores = []
    for idx1, idx2 in false_pair_indices:
        score = compute_entanglement_score(bitchains[idx1], bitchains[idx2])
        false_scores.append(score.total_score)
    
    true_mean = sum(true_scores) / len(true_scores)
    false_mean = sum(false_scores) / len(false_scores)
    
    print(f"True pairs (n={len(true_scores)}): mean={true_mean:.4f}, range=[{min(true_scores):.4f}, {max(true_scores):.4f}]")
    print(f"False pairs (n={len(false_scores)}): mean={false_mean:.4f}, range=[{min(false_scores):.4f}, {max(false_scores):.4f}]")
    print(f"Separation: {true_mean - false_mean:.4f}")
    
    is_separated = true_mean > false_mean
    print(f"✅ PASS: True pairs score higher" if is_separated else f"❌ FAIL: Poor separation")
    
    assert is_separated, f"True mean {true_mean} should be > false mean {false_mean}"
    assert true_mean > 0.85, f"True mean {true_mean} should be > 0.85"
    assert false_mean < 0.30, f"False mean {false_mean} should be < 0.30"



# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_mathematical_tests():
    """
    Run all mathematical validation tests (5 core tests).
    
    Note: Threshold sweep and full validation are in test_exp06_final_validation.py
    
    Returns:
        Dictionary with test results
    """
    print("\n" + "█"*70)
    print("EXP-06 MATHEMATICAL VALIDATION SUITE")
    print("█"*70)
    print("(5 core mathematical property tests)")
    print("█"*70)
    
    results = {
        'determinism': test_determinism(),
        'symmetry': test_symmetry(),
        'boundedness': test_boundedness(),
        'components': test_component_boundedness(),
        'separation': test_separation(),
    }
    
    print("\n" + "="*70)
    print("MATHEMATICAL PROOFS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL PASS' if all_passed else '❌ SOME FAILED'}")
    
    if all_passed:
        print("\n🎯 Mathematical framework validated. Proceeding to precision/recall tests...")
        
        # Threshold sweep
        threshold_results = test_threshold_sweep()
        
        # Full validation
        full_result = test_full_validation()
        
        # Save results
        print("\n" + "="*70)
        print("SAVING RESULTS")
        print("="*70)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        results_file = f'seed/engine/results/exp06_math_validation_{timestamp}.json'
        
        output = {
            'experiment': 'EXP-06',
            'phase': 'mathematical_validation',
            'timestamp': timestamp,
            'mathematical_proofs': results,
            'full_validation': {
                'threshold': full_result.threshold,
                'confusion_matrix': {
                    'true_positives': full_result.true_positives,
                    'false_positives': full_result.false_positives,
                    'false_negatives': full_result.false_negatives,
                    'true_negatives': full_result.true_negatives,
                },
                'metrics': {
                    'precision': round(full_result.precision, 4),
                    'recall': round(full_result.recall, 4),
                    'f1_score': round(full_result.f1_score, 4),
                    'accuracy': round(full_result.accuracy, 4),
                },
                'runtime_seconds': round(full_result.runtime_seconds, 4),
                'passed': full_result.passed,
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Results saved to: {results_file}")
        
        return output
    else:
        print("\n❌ Mathematical framework has issues. Fix before proceeding.")
        return results


if __name__ == '__main__':
    run_all_mathematical_tests()