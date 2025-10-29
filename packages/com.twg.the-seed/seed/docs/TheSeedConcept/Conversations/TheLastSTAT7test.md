# Reproducibility stress test for STAT7 across seven dimensions

You’re aiming to prove determinism under real-world pressure: waves of requests, shifting realms, vector permutations, GC churn, and memory stress. Here’s a doctrine-aligned stress suite that attacks all seven axes and makes randomness or drift impossible to hide.

---

### Test objectives

- **Determinism under load:** Identical inputs produce identical outputs across time, load, and concurrency.
- **Stability across projections:** Realm/mode changes (platformer/top-down/3D) do not perturb score outcomes for the same logical pairs.
- **No entropy leakage:** GC cycles, memory pressure, or thread contention never alter results.
- **Bounded numerical variance:** Any floating-point differences remain below a strict epsilon with reproducible rounding.

---

### Failure definitions

- **Hard failure:** Any score differs from the baseline beyond epsilon (\(\epsilon = 10^{-12}\), configurable).
- **Pattern drift:** Monotonic or cyclic deviation over iterations, even within epsilon (indicates systemic bias).
- **Concurrency skew:** Per-thread or per-core result sets diverge from baseline.
- **Mode bleed:** Projection (realm/view) alters the score for the same logical pair.
- **GC interference:** Result differences correlate with GC events or memory pressure markers.

---

### Test dimensions and attack patterns

#### 1. Waves (temporal bursts)
- **Pattern:** 20 iterations; each iteration fires a burst of requests (e.g., 1,000 pairs), then idles briefly.
- **Goal:** Detect heat-soak behavior or time-linked drift.
- **Metric:** Per-iteration hash of full score vector compared to baseline.

#### 2. Loads (throughput tiers)
- **Tiers:** 100, 1,000, 10,000 pairs per iteration.
- **Goal:** Ensure determinism scales without change in outcomes.
- **Metric:** Hash equality; latency percentiles (p50/p95/p99) logged but not part of determinism verdict.

#### 3. Vectors (polarity and resonance permutations)
- **Pattern:** Systematic permutation of polarity vectors and resonance components across the same logical pairs.
- **Goal:** Confirm score function symmetry and component boundedness under varied vector states.
- **Metric:** Pairwise equality under permutation that preserves logical identity.

#### 4. Realms (projection modes)
- **Modes:** platformer, top-down, 3D projections of the same STAT7 entities.
- **Goal:** Projection changes must not alter entanglement scores for the same logical pair.
- **Metric:** Realm-invariant score equality.

#### 5. Concurrency (threads and processes)
- **Pattern:** Single-thread, multi-thread (N threads), multi-process (M workers).
- **Goal:** No race conditions, shared-state bleed, or non-deterministic outcomes.
- **Metric:** Cross-worker hash equality; per-worker baseline comparison.

#### 6. Memory pressure (GC and fragmentation)
- **Pattern:** Allocate/free large buffers between iterations; trigger GC cycles; simulate fragmentation.
- **Goal:** GC events must not correlate with score changes.
- **Metric:** Record GC timestamps/metrics; assert zero correlation with any score deviation.

#### 7. Duration (long-run soak)
- **Targets:** Quick (15 min), Standard (1 hour), Extended (4 hours).
- **Goal:** Catch slow drift or time-dependent issues.
- **Metric:** Moving window trend analysis of score deltas (must remain zero).

---

### Parameters and recommended defaults

- **Batch sizes:** 100, 1,000, 10,000.
- **Iterations:** 20 (quick), 100 (standard).
- **Concurrency:** Threads = {1, 4, 16}; Processes = {1, 2, 8}.
- **Epsilon:** \(10^{-12}\) for float equality; also compute deterministic rounded form (e.g., quantize to 12 decimals).
- **GC hooks:** Enable explicit GC and capture metrics; log heap size deltas per iteration.

---

### Metrics and artifacts

- **Baseline vector hash:** SHA‑256 of ordered score array per scenario (the canonical reference).
- **Equality checks:** Exact equality of quantized scores + epsilon-based float equality.
- **Drift analysis:** Max/mean delta vs. baseline; regression line slope over time (must be zero).
- **Correlation audit:** Pearson/Spearman correlation between GC events/memory pressure and any score deviation (must be ~0).
- **Confusion matrices:** Optional, if scenarios include labeled pairs; verify threshold (e.g., 0.85) remains invariant.
- **Environment manifest:** Versions, seeds, hardware, OS; commit hash; dataset fingerprints.

---

### Test structure and suite layout

- **tests/stress/test_stat7_reproducibility.py**
  - **test_waves_temporal_stability**: Burst → idle cycles; verify hashes per iteration.
  - **test_load_tiers_determinism**: 100/1K/10K batches; compare to baseline.
  - **test_vector_permutations_symmetry**: Polarity/resonance permutations; ensure invariant scores.
  - **test_realms_projection_invariance**: platform/top-down/3D projections; same logical pairs, same scores.
  - **test_concurrency_threads_processes**: Thread/process pools; per-worker equality.
  - **test_memory_pressure_gc_isolation**: Allocate/free, force GC; verify no correlation or drift.
  - **test_duration_long_run_soak**: 1‑hour soak; rolling hash and drift checks.

---

### Practical guidance

- **Seed control:** Fix RNG seeds globally; disable any “time-based” components in the score function.
- **Quantization:** Store both raw float and quantized to 12 decimal places; compare both.
- **Immutable inputs:** Freeze entity snapshots for the duration; assert dataset fingerprints never change.
- **Isolation:** For process-based tests, ensure no shared mutable state (use copy‑on‑write or deep copies).

---

### Optional: attack vectors for adversarial robustness

- **Near-boundary pairs:** Scores engineered around 0.84–0.86 to test threshold stability.
- **Noise injection:** Add controlled perturbations to non-deterministic subsystems (if any) to ensure isolation.
- **Cache invalidation:** Periodically clear caches to prove determinism is not an artifact of stale state.

---

### “Waves, loads, vectors, realms” run plan

1. **Wave 1 (Baseline):** Single-thread, 1,000 pairs, 20 iterations → establish baseline hash.
2. **Wave 2 (Loads):** 100, 1,000, 10,000 pairs → baseline equality across tiers.
3. **Wave 3 (Vectors):** Permute polarity/resonance; ensure invariant scores for logical identity.
4. **Wave 4 (Realms):** Project same pairs across modes; assert realm-invariant scores.
5. **Wave 5 (Concurrency):** Threads 4/16; Processes 2/8; compare per-worker results.
6. **Wave 6 (Memory/GC):** Allocate/free; force GC; audit correlation.
7. **Wave 7 (Duration):** 1‑hour soak, rolling equality and drift analysis.

---

### Bing Copilot's recommended psudocode for the test script:

```
# tests/stress/test_stat7_reproducibility.py
# Paste-ready prototype: deterministic stress suite for STAT7 score function.
# Assumptions:
# - You have a pure, deterministic `score_function(a, b)` available.
# - You can produce a stable set of logical pairs via `get_logical_pairs(n)`.
# - Realm projections do NOT change the logical identity of pairs (same entities).
# - Vector permutations preserve logical identity (used to assert symmetry/invariance).
#
# Fill the 🏳TODO hooks at the bottom to wire into your engine.

import os
import time
import math
import hashlib
import gc
import random
import statistics
from dataclasses import dataclass
from typing import List, Tuple, Dict, Callable

import pytest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# -----------------------------
# Configuration
# -----------------------------

EPSILON = 1e-12           # Float equality tolerance
QUANTIZE_DECIMALS = 12    # Deterministic rounding for hashable comparison
SEED = 42                 # Global RNG seed for reproducibility

BATCH_SIZES = [100, 1000, 10_000]     # Load tiers
ITERATIONS_QUICK = 20                 # Temporal waves iterations
ITERATIONS_STANDARD = 100             # Extended waves
THREAD_TIERS = [1, 4, 16]             # Thread pool sizes
PROCESS_TIERS = [1, 2, 8]             # Process pool sizes

SOAK_DURATION_SECONDS = 60 * 15       # 15-minute soak by default (adjust as needed)
SOAK_CHECK_INTERVAL = 5               # seconds


# -----------------------------
# Helpers
# -----------------------------

def set_global_seed(seed: int = SEED) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass

def quantize(x: float, decimals: int = QUANTIZE_DECIMALS) -> float:
    q = round(x, decimals)
    # Normalize negative zeros
    if q == 0.0:
        q = 0.0
    return q

def vector_hash(values: List[float]) -> str:
    # Hash quantized floats to avoid tiny FP jitter
    m = hashlib.sha256()
    for v in values:
        q = quantize(v)
        m.update(f"{q:.{QUANTIZE_DECIMALS}f}".encode("utf-8"))
    return m.hexdigest()

def assert_equal_vectors(a: List[float], b: List[float], epsilon: float = EPSILON) -> None:
    assert len(a) == len(b), f"Length mismatch: {len(a)} != {len(b)}"
    for i, (x, y) in enumerate(zip(a, b)):
        if math.isfinite(x) and math.isfinite(y):
            diff = abs(x - y)
            assert diff <= epsilon, f"Index {i}: |{x}-{y}|={diff} > {epsilon}"
        else:
            assert x == y, f"Index {i}: non-finite mismatch {x} != {y}"

def run_batch_scores(pairs: List[Tuple[dict, dict]], score_fn: Callable[[dict, dict], float]) -> List[float]:
    return [score_fn(a, b) for (a, b) in pairs]

def run_batch_scores_threaded(pairs: List[Tuple[dict, dict]], score_fn: Callable[[dict, dict], float], threads: int) -> List[float]:
    results = [None] * len(pairs)
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(score_fn, a, b): idx for idx, (a, b) in enumerate(pairs)}
        for fut in as_completed(futs):
            idx = futs[fut]
            results[idx] = fut.result()
    return results

def _score_in_proc(args) -> float:
    (a, b, score_fn_path) = args
    # Import lazily inside process to avoid shared state
    score_fn = load_score_fn(score_fn_path)
    return score_fn(a, b)

def run_batch_scores_processes(pairs: List[Tuple[dict, dict]], score_fn_path: str, procs: int) -> List[float]:
    args = [(a, b, score_fn_path) for (a, b) in pairs]
    results = [None] * len(args)
    with ProcessPoolExecutor(max_workers=procs) as ex:
        futs = {ex.submit(_score_in_proc, arg): idx for idx, arg in enumerate(args)}
        for fut in as_completed(futs):
            idx = futs[fut]
            results[idx] = fut.result()
    return results

def force_memory_pressure_kb(kb: int = 256_000) -> None:
    # Allocate and free a large buffer to induce GC/fragmentation pressure
    buf = bytearray(kb * 1024)
    for i in range(0, len(buf), 4096):
        buf[i] = (i % 251)
    del buf

def capture_gc_snapshot() -> Dict[str, int]:
    # Basic GC stats; expand to psutil if available
    collected = gc.collect()
    counts = {
        "gc_collected": collected,
        "gc_thresholds": sum(gc.get_threshold()),
    }
    return counts

@dataclass
class ScenarioResult:
    name: str
    baseline_hash: str
    iteration_hashes: List[str]
    deltas_max: float
    deltas_mean: float
    drift_detected: bool


# -----------------------------
# Tests
# -----------------------------

def test_waves_temporal_stability():
    """
    Burst → idle cycles; ensure results remain identical across iterations under GC churn.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)  # 1,000 pairs baseline
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    baseline_hash = vector_hash(baseline)

    iteration_hashes = []
    deltas = []

    for i in range(ITERATIONS_QUICK):
        # Optional memory pressure + GC
        force_memory_pressure_kb(128_000)  # ~128MB
        gc_stats = capture_gc_snapshot()
        current = run_batch_scores(pairs, score_fn)
        iteration_hash = vector_hash(current)
        iteration_hashes.append(iteration_hash)

        # Equality check
        assert_equal_vectors(baseline, current)
        # Track delta magnitudes (quantized)
        d = [abs(quantize(x) - quantize(y)) for x, y in zip(baseline, current)]
        deltas.append(max(d))

    assert all(h == baseline_hash for h in iteration_hashes), "Temporal wave hashes diverged from baseline"
    drift_detected = any(d > 0.0 for d in deltas)
    assert not drift_detected, f"Detected non-zero drift across iterations: max={max(deltas)}"


@pytest.mark.parametrize("batch_size", BATCH_SIZES)
def test_load_tiers_determinism(batch_size):
    """
    Determinism across load tiers: 100 / 1K / 10K.
    """
    set_global_seed()
    pairs = get_logical_pairs(batch_size)
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    baseline_hash = vector_hash(baseline)

    for i in range(5):
        current = run_batch_scores(pairs, score_fn)
        assert_equal_vectors(baseline, current)
        assert vector_hash(current) == baseline_hash


def test_vector_permutations_symmetry_and_invariance():
    """
    Systematic permutation of polarity/resonance vectors while preserving logical identity.
    Score must remain invariant under symmetry-preserving transforms.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()

    baseline = run_batch_scores(pairs, score_fn)
    permuted_pairs = permute_vectors_preserving_identity(pairs)
    permuted = run_batch_scores(permuted_pairs, score_fn)

    assert_equal_vectors(baseline, permuted), "Vector permutations altered scores unexpectedly"
    assert vector_hash(baseline) == vector_hash(permuted), "Hashes differ after permutation"


@pytest.mark.parametrize("realm", ["platformer", "topdown", "3d"])
def test_realms_projection_invariance(realm):
    """
    Projection changes must not alter entanglement scores for the same logical pair.
    """
    set_global_seed()
    logical_pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()
    baseline = run_batch_scores(logical_pairs, score_fn)

    projected_pairs = [project_to_realm(a, b, realm) for (a, b) in logical_pairs]
    projected_scores = run_batch_scores(projected_pairs, score_fn)

    assert_equal_vectors(baseline, projected_scores)
    assert vector_hash(baseline) == vector_hash(projected_scores)


@pytest.mark.parametrize("threads", THREAD_TIERS)
def test_concurrency_threads(threads):
    """
    Multi-thread determinism: each thread pool size must match the single-thread baseline.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    threaded = run_batch_scores_threaded(pairs, score_fn, threads=threads)

    assert_equal_vectors(baseline, threaded)
    assert vector_hash(baseline) == vector_hash(threaded)


@pytest.mark.parametrize("procs", PROCESS_TIERS)
def test_concurrency_processes(procs):
    """
    Multi-process determinism: each worker configuration must match the single-process baseline.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    # Pass a module path to load score_fn in child processes (see hook below)
    score_fn_path = os.environ.get("STAT7_SCORE_FN_PATH", "")
    proc_results = run_batch_scores_processes(pairs, score_fn_path, procs=procs)

    assert_equal_vectors(baseline, proc_results)
    assert vector_hash(baseline) == vector_hash(proc_results)


def test_memory_pressure_gc_isolation():
    """
    GC cycles and memory pressure must not correlate with any score deviation.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    baseline_hash = vector_hash(baseline)

    hashes = []
    gc_collected = []
    for _ in range(ITERATIONS_QUICK):
        force_memory_pressure_kb(256_000)  # ~256MB
        stats = capture_gc_snapshot()
        gc_collected.append(stats["gc_collected"])
        current = run_batch_scores(pairs, score_fn)
        hashes.append(vector_hash(current))
        assert_equal_vectors(baseline, current)

    # Correlation check: if gc_collected varies but hashes never change, isolation holds
    assert all(h == baseline_hash for h in hashes), "Hash divergence under memory/GC pressure"
    # Optional: compute Spearman/Pearson if you add numpy/scipy


@pytest.mark.skipif(SOAK_DURATION_SECONDS <= 0, reason="Soak disabled")
def test_duration_long_run_soak():
    """
    Long-run soak: rolling equality checks and drift analysis over time.
    """
    set_global_seed()
    pairs = get_logical_pairs(1000)
    score_fn = load_score_fn()
    baseline = run_batch_scores(pairs, score_fn)
    baseline_hash = vector_hash(baseline)

    start = time.time()
    max_delta = 0.0
    iteration = 0

    while time.time() - start < SOAK_DURATION_SECONDS:
        current = run_batch_scores(pairs, score_fn)
        assert_equal_vectors(baseline, current)
        h = vector_hash(current)
        assert h == baseline_hash, f"Hash changed at iteration {iteration}"
        # Track quantized delta magnitude
        d = [abs(quantize(x) - quantize(y)) for x, y in zip(baseline, current)]
        max_delta = max(max_delta, max(d))
        time.sleep(SOAK_CHECK_INTERVAL)
        iteration += 1

    assert max_delta == 0.0, f"Observed non-zero max delta during soak: {max_delta}"


# -----------------------------
# Hooks to wire into your engine
# -----------------------------
# Replace these with real implementations from seed/engine.

def load_score_fn(module_path: str = "") -> Callable[[dict, dict], float]:
    """
    Load the deterministic entanglement score function.
    If module_path is provided (for processes), import from that path.
    """
    if module_path:
        # Example: "seed.engine.exp06.scoring:score_function"
        mod_name, attr = module_path.split(":")
        module = __import__(mod_name, fromlist=[attr])
        return getattr(module, attr)

    # Fallback: direct import (adjust to your actual module)
    from seed.engine.exp06.scoring import score_function  # TODO: set real path
    return score_function


def get_logical_pairs(n: int) -> List[Tuple[dict, dict]]:
    """
    Produce a stable set of logical entity pairs.
    Each entity is a dict snapshot with STAT7 coordinates and attributes.
    Must be immutable across runs for reproducibility.
    """
    # TODO: Replace with actual dataset retrieval.
    # Example synthetic pairs with fixed coordinates:
    pairs = []
    for i in range(n):
        a = {
            "id": f"A-{i}",
            "realm": "narrative",
            "generation": 3,
            "resonance": "high",
            "coords": [1, 2, 3, 4, 5, 6, 7],  # placeholder STAT7 coords
        }
        b = {
            "id": f"B-{i}",
            "realm": "narrative",
            "generation": 3,
            "resonance": "high",
            "coords": [7, 6, 5, 4, 3, 2, 1],
        }
        pairs.append((a, b))
    return pairs


def permute_vectors_preserving_identity(pairs: List[Tuple[dict, dict]]) -> List[Tuple[dict, dict]]:
    """
    Apply symmetry-preserving permutations to polarity/resonance while keeping logical identity.
    For example, reorder components or sign-flip pairs that are symmetric by definition.
    """
    # TODO: Implement based on your actual vector semantics.
    permuted = []
    for (a, b) in pairs:
        a2 = dict(a)
        b2 = dict(b)
        # Example: reverse coord order (symmetric) and flip a label that shouldn't affect score
        a2["coords"] = list(reversed(a["coords"]))
        b2["coords"] = list(reversed(b["coords"]))
        a2["resonance"] = a["resonance"]  # unchanged
        b2["resonance"] = b["resonance"]  # unchanged
        permuted.append((a2, b2))
    return permuted


def project_to_realm(a: dict, b: dict, realm: str) -> Tuple[dict, dict]:
    """
    Project the same logical pair into platformer/topdown/3d realms.
    Projection should NOT alter entanglement score for the same logical identity.
    """
    # TODO: Implement real projection rules. Here we vary rendering hints only.
    a2 = dict(a)
    b2 = dict(b)
    a2["realm"] = realm
    b2["realm"] = realm
    # Example: attach projection metadata that score_function ignores
    a2["projection"] = {"mode": realm, "lod": 1}
    b2["projection"] = {"mode": realm, "lod": 1}
    return a2, b2
```
