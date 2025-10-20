# EXP-06 Entanglement Detection: Unblocking Action Plan

**Date:** 2025-10-19  
**Status:** 🟢 READY TO PROCEED  
**Dependency Check:** ✅ Phase 1 & 2 Complete, NO BLOCKERS

---

## Executive Summary

**EXP-06 can begin immediately.** All foundational experiments (EXP-01 through EXP-05) are complete and locked. The entanglement detection algorithm is standalone (does not depend on QR-E output API or any other Phase 3 capability).

**No security blockers, no architectural gaps, no missing dependencies.**

---

## Current State Verification

| Component | Status | Evidence |
|-----------|--------|----------|
| **Phase 1 (EXP-01 to EXP-03)** | ✅ DOCTRINE LOCKED | All three experiments passing, zero collisions proven |
| **Phase 2 (EXP-04 to EXP-05)** | ✅ COMPLETE + SECURED | Fractal scaling + compression both validated; 3-Layer Firewall deployed |
| **Security Hardening (WFC + RecoveryGate + Conservator)** | ✅ PRODUCTION-READY | 27+ tests passing, audit trail immutable, rate limiting enforced |
| **Short-term integration work** | 🔄 NOT BLOCKING EXP-06 | SimpleAuthService/InMemoryAuditLedger replacements are orthogonal |
| **QR-E Output API** | ❌ NOT YET STARTED | Will be Phase 2.5/3 integration layer; **does not block EXP-06** |

---

## EXP-06 Specification

**Experiment:** Entanglement Detection (High Precision/Recall)

### Hypothesis
Bit-chains with high semantic similarity are reliably detected as entangled via resonance and polarity alignment.

### Mathematical Goals
- **Precision > 90%:** Of all pairs detected as entangled, >90% should be true entanglements
- **Recall > 85%:** Of all true entanglements in the dataset, >85% should be detected

### Test Design
```
Test Dataset: 100 bit-chains

├── 20 TRUE PAIRS (should be detected as entangled)
│   ├── High polarity alignment (Polarity distance < 0.2)
│   ├── Same Realm or adjacent Realm
│   ├── Similar Luminosity (within 1 generation)
│   └── Adjacency overlap > 40%
│
├── 20 FALSE PAIRS (should NOT be detected)
│   ├── Low polarity alignment (Polarity distance > 0.7)
│   ├── Different Realm + orthogonal Adjacency
│   ├── Luminosity distance > 3 generations
│   └── Adjacency overlap < 10%
│
└── 60 UNRELATED (baseline noise)
    └── Random STAT7 coordinates
```

### Algorithm (from 03-BIT-CHAIN-SPEC)
The entanglement score is computed as a weighted combination of:

```python
entanglement_score = (
    0.3 * polarity_resonance(bc1, bc2) +
    0.2 * realm_affinity(bc1, bc2) +
    0.25 * adjacency_overlap(bc1, bc2) +
    0.15 * luminosity_proximity(bc1, bc2) +
    0.1 * lineage_affinity(bc1, bc2)
)

# Entangled if: entanglement_score > threshold (to be calibrated)
```

### Key Algorithms to Implement

1. **polarity_resonance(bc1, bc2) → float [0.0 to 1.0]**
   - Input: Two bit-chain Polarity vectors (7-dimensional)
   - Output: Cosine similarity of polarity vectors
   - Interpretation: 1.0 = identical polarity, 0.0 = orthogonal

2. **realm_affinity(bc1, bc2) → float [0.0 to 1.0]**
   - Input: bc1.realm, bc2.realm
   - Output: 1.0 if same Realm, 0.7 if adjacent, 0.0 if orthogonal
   - Adjacency rule: Realms connected by narrative flow or structural dependency

3. **adjacency_overlap(bc1, bc2) → float [0.0 to 1.0]**
   - Input: bc1.adjacency_set, bc2.adjacency_set (sets of IDs)
   - Output: Jaccard similarity = |intersection| / |union|
   - Interpretation: 1.0 = identical neighborhood, 0.0 = no overlap

4. **luminosity_proximity(bc1, bc2) → float [0.0 to 1.0]**
   - Input: bc1.luminosity, bc2.luminosity
   - Output: 1.0 - min(|Lum1 - Lum2| / max_luminosity_distance, 1.0)
   - Interpretation: 1.0 = same luminosity tier, 0.0 = max distance

5. **lineage_affinity(bc1, bc2) → float [0.0 to 1.0]**
   - Input: bc1.lineage, bc2.lineage
   - Output: 1.0 if same parent; decay by 0.9^(generation_distance)
   - Interpretation: 1.0 = same parent, decays with distance

### Success Criteria
```
✅ PASS if:
   - Precision >= 90%
   - Recall >= 85%
   - All 20 TRUE pairs detected
   - All 20 FALSE pairs NOT detected (or ~2 false positives acceptable)
   - Runtime < 1 second for 100 bit-chains (5000x pairs to check)
```

---

## Implementation Plan

### Phase 1: Core Algorithm (1-2 hours)
**File:** `seed/engine/exp06_entanglement_detection.py`

```python
class EXP06_EntanglementDetection:
    """Standalone entanglement detection validator."""
    
    def compute_entanglement_score(
        self, 
        bitchain_1: BitChain, 
        bitchain_2: BitChain
    ) -> float:
        """Returns 0.0 to 1.0 entanglement score."""
        pass
    
    def detect_entanglements(
        self, 
        bitchains: List[BitChain],
        threshold: float = 0.65  # To be tuned
    ) -> List[Tuple[BitChain, BitChain, float]]:
        """Returns list of (bc1, bc2, score) where score >= threshold."""
        pass
    
    def run_validation(
        self,
        true_pairs: List[Tuple[BitChain, BitChain]],
        false_pairs: List[Tuple[BitChain, BitChain]],
        unrelated: List[BitChain]
    ) -> ValidationResult:
        """Computes precision/recall metrics."""
        pass
```

### Phase 2: Test Data Generation (30 minutes)
**File:** `seed/engine/exp06_test_data.py`

```python
def generate_test_dataset() -> Tuple[
    List[BitChain],           # All 100
    List[Tuple[int, int]],    # True pair indices
    List[Tuple[int, int]],    # False pair indices
]:
    """Creates 100 bit-chains with known entanglement structure."""
    pass
```

### Phase 3: Validation & Metrics (1 hour)
**File:** `seed/engine/exp06_metrics.py`

```python
@dataclass
class ValidationResult:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float  # TP / (TP + FP)
    recall: float     # TP / (TP + FN)
    runtime_seconds: float
    threshold: float
    
    @property
    def passed(self) -> bool:
        return self.precision >= 0.90 and self.recall >= 0.85
```

### Phase 4: Threshold Calibration (1-2 hours)
- Run algorithm with different thresholds (0.5, 0.55, 0.60, 0.65, 0.70, 0.75)
- Plot precision vs. recall curve
- Select threshold that maximizes F1 score while meeting minimum targets

---

## Threshold Calibration Strategy

The entanglement detection algorithm will likely need tuning. Here's the process:

```
For each threshold in [0.5, 0.55, 0.60, ..., 0.75]:
    ├── Run detection on test dataset
    ├── Compute precision, recall, F1
    ├── Log results
    └── Plot on ROC curve

Select threshold that:
    ├── Meets precision >= 90%
    ├── Meets recall >= 85%
    └── Maximizes F1 = 2 * (precision * recall) / (precision + recall)
```

Expected result: threshold likely between 0.60 and 0.70

---

## Testing Strategy

### Unit Tests (test_exp06_entanglement.py)
```python
def test_perfect_entanglement():
    """Two identical bit-chains score 1.0"""
    pass

def test_orthogonal_pairs():
    """Completely different bit-chains score < 0.3"""
    pass

def test_precision_metric():
    """Verify precision calculation"""
    pass

def test_recall_metric():
    """Verify recall calculation"""
    pass

def test_threshold_sweep():
    """Verify calibration across all thresholds"""
    pass
```

### Integration Test
```python
def test_full_validation():
    """Run full experiment on 100-element dataset"""
    pass
```

---

## Execution Checklist

- [ ] Create `seed/engine/exp06_entanglement_detection.py`
- [ ] Create `seed/engine/exp06_test_data.py`
- [ ] Create `seed/engine/exp06_metrics.py`
- [ ] Create `tests/test_exp06_entanglement.py` (unit tests)
- [ ] Generate test dataset (20 true, 20 false, 60 unrelated)
- [ ] Implement core scoring algorithm
- [ ] Run with default threshold (0.65)
- [ ] Sweep thresholds and plot ROC curve
- [ ] Document final threshold selection
- [ ] Verify precision >= 90%, recall >= 85%
- [ ] Create `seed/engine/results/exp06_entanglement_[timestamp].json`
- [ ] Update `AUDIT_VALIDATION_REPORT_2025-10-19.md` with results

---

## Files to Create/Modify

### New Files
- `seed/engine/exp06_entanglement_detection.py` (main algorithm, 300-400 lines)
- `seed/engine/exp06_test_data.py` (test dataset generator, 150-200 lines)
- `seed/engine/exp06_metrics.py` (validation metrics, 100-150 lines)
- `tests/test_exp06_entanglement.py` (unit tests, 200-300 lines)
- `seed/engine/results/exp06_entanglement_[timestamp].json` (results)

### Updated Files
- `seed/engine/stat7_experiments.py` (add EXP06 class if needed)
- `AUDIT_VALIDATION_REPORT_2025-10-19.md` (add Phase 2 closure + EXP-06 entry)

---

## QR-Entanglement (QR-E) Output API: Roadmap

**Status:** ❌ NOT STARTED (intentionally deferred)  
**Planned Phase:** 2.5 or Phase 3 integration layer  
**Priority:** Lower than EXP-06 through EXP-10 (validation math comes first)

### Why QR-E is NOT a blocker for EXP-06

1. **QR-E is a presentation layer** (how entities appear to users)
2. **EXP-06 is a detection layer** (how entities are discovered via resonance)
3. **No data flow dependency:** QR-E wraps EXP-06 results; doesn't feed into them

### When QR-E Should Be Scheduled

**Option A: After EXP-06 complete (Recommended)**
- Run all math validation experiments first (EXP-06 through EXP-10)
- Understand full system behavior under stress
- Then wrap with QR-E for onboarding/display

**Option B: Parallel to EXP-07/EXP-08**
- If you need user-facing functionality for demos
- Create stub QR-E API that accepts STAT7 coordinates and returns QR codes
- Can integrate with real fractal encoding once EXP-06 results are in

### QR-E Component Architecture (Placeholder)

```
┌─────────────────────────────────────────┐
│ QR-ENTANGLEMENT OUTPUT API (Phase 2.5)  │
├─────────────────────────────────────────┤
│                                         │
│  Input: STAT7 coordinates (bc.id)      │
│  ├─ Realm, Lineage, Adjacency, etc     │
│                                         │
│  Processing: Fractal QR Encoding       │
│  ├─ Zoom level 1 (minimal)             │
│  ├─ Zoom level 2-3 (standard)          │
│  ├─ Zoom level 4-7 (detailed)          │
│  └─ 2FA integration (progressive auth) │
│                                         │
│  Output: QR code metadata               │
│  ├─ Base64 PNG image                   │
│  ├─ Encoding format version             │
│  ├─ Scan destination URL                │
│  └─ Entanglement hints (for UI)         │
│                                         │
└─────────────────────────────────────────┘
        ↑
        │ wraps results from
        ↓
┌─────────────────────────────────────────┐
│ EXP-06 ENTANGLEMENT DETECTION           │
│ (currently being implemented)           │
└─────────────────────────────────────────┘
```

---

## No Blockers: Go Ahead

**You are unblocked. EXP-06 can proceed immediately.**

- ✅ All Phase 1 experiments passing
- ✅ All Phase 2 experiments passing + secured
- ✅ No architectural gaps in entanglement algorithm
- ✅ Test dataset design is clear
- ✅ Success criteria well-defined (Precision/Recall targets)
- ❌ QR-E is NOT required for EXP-06 validation
- ❌ No other Phase 3 capability blocks this

**Next action:** Begin `seed/engine/exp06_entanglement_detection.py` implementation.

---

## Estimated Timeline

| Task | Duration | Status |
|------|----------|--------|
| Core Algorithm | 1-2 hours | → Ready to start |
| Test Data Generation | 30 minutes | → Ready to start |
| Unit Tests | 1 hour | → Ready to start |
| Threshold Calibration | 1-2 hours | → After core is working |
| **Total Estimated** | **4-5 hours** | **→ EXP-06 COMPLETE** |

---

## Success Definition

**EXP-06 is LOCKED when:**
- [ ] Precision >= 90%
- [ ] Recall >= 85%
- [ ] All 20 true pairs detected (TP = 20 or 19 acceptable)
- [ ] < 3 false positives (FP < 3)
- [ ] Results JSON saved with timestamp
- [ ] Updated audit report shows EXP-06 = ✅ COMPLETE

**Then proceed to:**
- EXP-07: LUCA Bootstrap
- EXP-08: RAG Integration
- EXP-09: Concurrency
- EXP-10: Narrative Preservation

---

**Unblocked. Ready to go.** 🟢