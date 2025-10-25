import math
import random
from typing import List, Tuple

import pytest

from seed.engine.exp06_entanglement_detection import (
    EntanglementDetector,
    compute_entanglement_score,
    realm_affinity,
    adjacency_overlap,
    luminosity_proximity,
    lineage_affinity,
)
from seed.engine.exp06_test_data import generate_test_dataset


def _metrics_from_pairs(
    bitchains,
    true_pairs: List[Tuple[int, int]],
    false_pairs: List[Tuple[int, int]],
    threshold: float,
):
    # Score labeled pairs only to compute metrics
    y_true = []
    y_pred = []
    for i, j in true_pairs:
        sc = compute_entanglement_score(bitchains[i], bitchains[j]).total_score
        y_true.append(1)
        y_pred.append(1 if sc >= threshold else 0)
    for i, j in false_pairs:
        sc = compute_entanglement_score(bitchains[i], bitchains[j]).total_score
        y_true.append(0)
        y_pred.append(1 if sc >= threshold else 0)

    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }


@pytest.fixture(scope="module")
def dataset():
    bitchains, true_pairs, false_pairs = generate_test_dataset()
    return bitchains, true_pairs, false_pairs


def test_phase2a_cross_validation_variance(dataset):
    bitchains, true_pairs, false_pairs = dataset
    threshold = 0.85

    # 5-fold style repeated eval (deterministic dataset -> near-zero variance expected)
    runs = []
    for seed in [0, 1, 2, 3, 4]:
        random.seed(seed)
        # Shuffle order to simulate different folds influence (though pairs fixed)
        random.shuffle(true_pairs)
        random.shuffle(false_pairs)
        m = _metrics_from_pairs(bitchains, true_pairs, false_pairs, threshold)
        runs.append((m['precision'], m['recall']))

    precisions = [p for p, r in runs]
    recalls = [r for p, r in runs]

    def _variance(vals):
        mean = sum(vals) / len(vals)
        return sum((v - mean) ** 2 for v in vals) / len(vals)

    p_var = _variance(precisions)
    r_var = _variance(recalls)

    # Success criteria: within ±5% of 1.0 and variance <= 0.0004 (~2% squared)
    assert all(0.95 <= p <= 1.0 for p in precisions)
    assert all(0.95 <= r <= 1.0 for r in recalls)
    assert p_var <= 0.0004
    assert r_var <= 0.0004


def test_phase2b_threshold_plateau(dataset):
    bitchains, true_pairs, false_pairs = dataset
    thresholds = [0.85, 0.90]
    f1s = []
    for t in thresholds:
        m = _metrics_from_pairs(bitchains, true_pairs, false_pairs, t)
        f1s.append(m['f1'])

    # Expect stable plateau across tuned window (no brittleness)
    assert all(f >= 0.99 for f in f1s)


def test_phase2c_adversarial_noise(dataset):
    bitchains, true_pairs, false_pairs = dataset

    def _add_noise(bc, sigma=0.05):
        # small gaussian noise to resonance/velocity, clamped to [-1, 1]
        import random as rnd
        bc = {**bc, 'coordinates': {**bc['coordinates']}}
        for key in ('resonance', 'velocity'):
            val = bc['coordinates'].get(key, 0.0)
            noisy = max(-1.0, min(1.0, val + rnd.gauss(0.0, sigma)))
            bc['coordinates'][key] = noisy
        return bc

    # Build noisy copy
    noisy = [
        _add_noise(bc) for bc in bitchains
    ]

    base = _metrics_from_pairs(bitchains, true_pairs, false_pairs, 0.85)
    pert = _metrics_from_pairs(noisy, true_pairs, false_pairs, 0.85)

    # No degradation > 1%
    assert base['precision'] - pert['precision'] <= 0.01 + 1e-9
    assert base['recall'] - pert['recall'] <= 0.01 + 1e-9


def test_phase2d_stress_edge_cases():
    # Empty adjacency (both) -> jaccard 1.0
    bc_a = {'coordinates': {'adjacency': []}}
    bc_b = {'coordinates': {'adjacency': []}}
    assert math.isclose(adjacency_overlap(bc_a, bc_b), 1.0, rel_tol=0, abs_tol=1e-9)

    # Lineage extremes: monotonic decay
    x = {'coordinates': {'lineage': 0}}
    y = {'coordinates': {'lineage': 1}}
    z = {'coordinates': {'lineage': 100}}
    l_xy = lineage_affinity(x, y)
    l_xz = lineage_affinity(x, z)
    assert l_xy > l_xz > 0.0

    # Realm combinations
    d = {'coordinates': {'realm': 'data'}}
    f = {'coordinates': {'realm': 'faculty'}}
    assert realm_affinity(d, d) == 1.0
    assert realm_affinity(d, f) in (0.0, 0.7)

    # Luminosity bounds
    u = {'coordinates': {'density': 0.0}}
    v = {'coordinates': {'density': 1.0}}
    assert 0.0 <= luminosity_proximity(u, v) <= 1.0


def test_phase2e_label_leakage_audit(dataset):
    bitchains, true_pairs, false_pairs = dataset

    # Baseline (correct labels)
    base = _metrics_from_pairs(bitchains, true_pairs, false_pairs, 0.85)
    assert base['f1'] >= 0.99

    # Shuffled labels: swap the role of true and false labels randomly
    labels = [1] * len(true_pairs) + [0] * len(false_pairs)
    pairs = true_pairs + false_pairs

    rnd = random.Random(42)
    rnd.shuffle(labels)

    # Compute predictions with unchanged model
    scores = []
    for i, (a, b) in enumerate(pairs):
        sc = compute_entanglement_score(bitchains[a], bitchains[b]).total_score
        scores.append(1 if sc >= 0.85 else 0)

    # Compute F1 against shuffled labels
    tp = sum(1 for y, p in zip(labels, scores) if y == 1 and p == 1)
    fp = sum(1 for y, p in zip(labels, scores) if y == 0 and p == 1)
    fn = sum(1 for y, p in zip(labels, scores) if y == 1 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    # Expect strong degradation vs near-perfect baseline (don’t require specific absolute value)
    assert f1 <= 0.6
    assert (base['f1'] - f1) >= 0.3


def test_detector_threshold_and_distribution(dataset):
    # Extra sanity check on detector API used by reports
    bitchains, true_pairs, false_pairs = dataset
    det = EntanglementDetector(threshold=0.85)
    pairs = det.detect(bitchains)
    stats = det.get_score_distribution()

    assert isinstance(pairs, list)
    assert 'min' in stats and 'max' in stats and 'mean' in stats
    assert 0.0 <= stats['min'] <= stats['max'] <= 1.0
