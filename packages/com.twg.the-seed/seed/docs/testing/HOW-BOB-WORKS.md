# HOW-BOB-WORKS: Bob's Architecture and Design

**For developers who need to understand, tune, or debug Bob**

---

## Overview

Bob is a **pre-return filter** in the EXP-09 API service that detects suspiciously perfect query results and verifies them using stress testing.

**His hypothesis:**
- **High Coherence + High Entanglement** = Trustworthy (good results + well-connected)
- **High Coherence + Low Entanglement** = Suspicious (isolated high scores = possible hallucination)

---

## Architecture Layers

### Layer 1: Detection
**When does Bob activate?**

```python
if coherence > 0.85 AND entanglement < 0.30:
    # Initiate investigation
```

Configuration in `exp09_api_service.py` (lines 71-80):
```python
class BobSkepticConfig:
    COHERENCE_HIGH_THRESHOLD = 0.85
    ENTANGLEMENT_LOW_THRESHOLD = 0.30
    STRESS_TEST_DIVERGENCE_THRESHOLD = 0.15
```

**In plain English:**
- Results with coherence ≤ 0.85 → Always PASSED (not suspicious)
- Results with coherence > 0.85 AND entanglement ≥ 0.30 → PASSED (good + connected)
- Results with coherence > 0.85 AND entanglement < 0.30 → INVESTIGATE (suspicious)

---

### Layer 2: Stress Testing
**How does Bob investigate?**

When triggered, Bob re-queries using **three orthogonal retrieval methods** and compares:

#### Test 1: Pure Semantic Retrieval
- If original query was hybrid, run **semantic-only** (no STAT7)
- Compare: Do the same documents rank high?
- **Why:** Tests if coherence comes from semantic relevance alone

#### Test 2: Pure STAT7 Retrieval
- If original query was hybrid, run **STAT7-only** (no semantic)
- Compare: Do the same documents rank high in address space?
- **Why:** Tests if coherence comes from spatial relationships alone

#### Test 3: Higher Confidence Threshold
- Re-run with stricter quality threshold (+0.2)
- Example: if original threshold was 0.6, test at 0.8
- Compare: Do strict results match original results?
- **Why:** Tests if borderline results are inflated in the original query

**Scoring:**
```
overlap_ratio = (documents found in re-test) / (documents in original)
consistency_score = average(overlap_ratios across all tests)
```

**Decision:**
- `consistency_score ≥ 0.85` → PASSED stress tests
- `consistency_score < 0.85` → FAILED stress tests

---

### Layer 3: Resolution
**What does Bob return?**

| Status | Condition | Action |
|--------|-----------|--------|
| `PASSED` | Never triggered investigation | Return immediately; no log |
| `VERIFIED` | High coherence + low entanglement, BUT consistent in stress tests | Return results + confidence boost; include verification log |
| `QUARANTINED` | High coherence + low entanglement, AND inconsistent in stress tests | Return with PENDING flag; include full audit trail; escalate to Faculty |

---

## Configuration Parameters

### COHERENCE_HIGH_THRESHOLD
**Default:** 0.85  
**Range:** 0.75–0.95  
**Meaning:** What counts as "suspiciously high" coherence?

**If too high (e.g., 0.95):**
- Bob rarely activates
- Hallucinations slip through (low False Negatives, high False Positives)
- Faster queries (no stress testing)

**If too low (e.g., 0.75):**
- Bob investigates more results
- Catches hallucinations better (high False Negatives, low False Positives)
- Slower queries (more stress testing)

---

### ENTANGLEMENT_LOW_THRESHOLD
**Default:** 0.30  
**Range:** 0.15–0.50  
**Meaning:** What counts as "suspiciously low" entanglement?

**If too high (e.g., 0.50):**
- Bob investigates more aggressively
- Catches isolated results earlier
- More stress testing overhead

**If too low (e.g., 0.15):**
- Bob only investigates truly isolated results
- Fewer stress tests
- Faster but misses some artifacts

---

### STRESS_TEST_DIVERGENCE_THRESHOLD
**Default:** 0.15  
**Range:** 0.10–0.25  
**Meaning:** How much divergence between tests = failure?

**If too high (e.g., 0.25):**
- Bob is more lenient
- Consistency scores can reach 0.75+ and still pass
- Fewer quarantines, more false negatives

**If too low (e.g., 0.10):**
- Bob is stricter
- Consistency must reach 0.90+ to pass
- More quarantines, fewer false negatives

**Relationship:**
```
Consistency Needed to Pass = 1.0 - STRESS_TEST_DIVERGENCE_THRESHOLD
Example: If threshold = 0.15, then consistency ≥ 0.85 passes
```

---

## Decision Logic (Code Flow)

```
┌─────────────────────────────────────────┐
│ Query Result Received                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Extract: coherence_score & entanglement │
└────────────┬────────────────────────────┘
             │
             ▼
         Is coherence > THRESHOLD?
         /                      \
       NO                        YES
       │                          │
       ▼                          ▼
    PASSED                   Is entanglement > THRESHOLD?
   (exit)                    /                         \
                           YES                         NO
                           │                            │
                           ▼                            ▼
                        PASSED                    Run Stress Tests
                       (exit)                          │
                                                       ▼
                                        Is consistency > (1.0 - DIVERGENCE_THRESHOLD)?
                                        /                                          \
                                      YES                                          NO
                                      │                                            │
                                      ▼                                            ▼
                                   VERIFIED                                  QUARANTINED
                            (return + log)                            (return + full log)
```

---

## Response Format

### When Bob Doesn't Investigate (PASSED)

```json
{
  "query_id": "q1",
  "result_count": 5,
  "results": [...],
  "narrative_analysis": {
    "coherence_score": 0.75,
    "stat7_coherence": 0.40
  },
  "bob_status": "PASSED",
  "bob_verification_log": null
}
```

### When Bob Investigates (VERIFIED or QUARANTINED)

```json
{
  "query_id": "q1",
  "result_count": 5,
  "results": [...],
  "narrative_analysis": {
    "coherence_score": 0.87,
    "stat7_coherence": 0.25
  },
  "bob_status": "VERIFIED",
  "bob_verification_log": {
    "stress_test_started": "2025-01-20T10:15:00Z",
    "original_result_ids": ["id1", "id2", "id3", "id4", "id5"],
    "tests_run": [
      {
        "test": "SEMANTIC_ONLY",
        "overlap_ratio": 0.90,
        "result_count": 5
      },
      {
        "test": "STAT7_ONLY",
        "overlap_ratio": 0.88,
        "result_count": 4
      },
      {
        "test": "HIGH_CONFIDENCE",
        "overlap_ratio": 0.92,
        "result_count": 5
      }
    ],
    "consistency_score": 0.90,
    "verdict": "CONSISTENT"
  }
}
```

---

## Tuning Bob

### Scenario 1: Too Many False Positives (Bob quarantines good results)

**Symptom:** Faculty reviews 20 quarantined results, 18 are actually good.

**Fix:**
```python
# In exp09_api_service.py, BobSkepticConfig:
COHERENCE_HIGH_THRESHOLD = 0.90          # from 0.85
STRESS_TEST_DIVERGENCE_THRESHOLD = 0.20  # from 0.15
```

**Why:**
- Raise coherence threshold → Only investigate VERY high scores
- Raise divergence threshold → Allow 20% divergence instead of 15%

**Trade-off:** Fewer quarantines, but might miss some hallucinations.

### Scenario 2: Too Many False Negatives (Bob misses hallucinations)

**Symptom:** Faculty finds bad results that Bob marked VERIFIED or PASSED.

**Fix:**
```python
# In exp09_api_service.py, BobSkepticConfig:
COHERENCE_HIGH_THRESHOLD = 0.80          # from 0.85
ENTANGLEMENT_LOW_THRESHOLD = 0.25        # from 0.30
STRESS_TEST_DIVERGENCE_THRESHOLD = 0.10  # from 0.15
```

**Why:**
- Lower coherence threshold → Investigate more aggressively
- Lower entanglement threshold → Flag more isolated results
- Lower divergence threshold → Stricter consistency requirement

**Trade-off:** More quarantines (slower queries), but catch more hallucinations.

### Scenario 3: Stress Tests Are Too Slow

**Symptom:** Queries with Bob's stress testing take >2 seconds.

**Fix (Option A):** Reduce max_results in stress test queries
```python
# In exp09_api_service.py, _stress_test_result() function:
max_results=5  # from 10
```

**Why:** Fewer results to compare = faster queries. Still representative.

**Fix (Option B):** Disable certain stress tests conditionally
```python
# Check if STAT7 is even in the original query
if not original_query.hybrid:
    skip_stat7_only_test = True
```

**Why:** Don't test methods that weren't used originally.

---

## Debugging Bob

### Bob Never Triggers (Always PASSED)

**Cause 1:** Your queries don't produce high coherence + low entanglement.

**Diagnosis:**
```powershell
# Check actual values
python exp09_cli.py query --query-id "test_1" --semantic "query" --json-output | ConvertFrom-Json | Select-Object -ExpandProperty "narrative_analysis"
```

Look for: `coherence_score` and `stat7_coherence` values

**Fix:** Either:
- Artificially craft a query that triggers Bob, OR
- Verify Bob's thresholds (maybe they're set too high)

**Cause 2:** Thresholds are configured too high.

**Diagnosis:**
```python
# In exp09_api_service.py, check:
print(BobSkepticConfig.COHERENCE_HIGH_THRESHOLD)  # Should be ~0.85
print(BobSkepticConfig.ENTANGLEMENT_LOW_THRESHOLD)  # Should be ~0.30
```

**Fix:** Adjust thresholds per "Tuning Bob" section above.

---

### Stress Tests Are Timing Out

**Cause:** RetrievalAPI is slow; stress tests running many queries in parallel.

**Diagnosis:**
```python
# Profile individual stress test queries
# Add timing logs to _stress_test_result()
```

**Fix:**
1. Reduce max_results (see "Scenario 3" above)
2. Disable individual stress tests if rarely triggered
3. Profile RetrievalAPI separately to find bottleneck

---

### Bob Quarantines Everything

**Cause:** Thresholds are too strict.

**Diagnosis:**
```powershell
# Run a batch and inspect results
python exp09_cli.py stress-test --num-scenarios 1 --queries-per-scenario 5 | ConvertFrom-Json | Where-Object { $_.bob_status -eq "QUARANTINED" } | Measure-Object

# If > 50% quarantined, Bob is too paranoid
```

**Fix:** Raise thresholds per "Scenario 1" above.

---

## Monitoring Bob

### Key Metrics to Track

**Alert Rate** = (queries triggering investigation) / (total queries)
- Target: 1-5%
- >10%: Too paranoid
- <0.5%: Might be missing issues

**Verification Rate** = (VERIFIED results) / (results investigated)
- Target: 80-95%
- >98%: Thresholds might be too loose
- <70%: Thresholds might be too strict

**Quarantine Rate** = (QUARANTINED results) / (results investigated)
- Target: 5-20%
- >50%: Bob is too paranoid
- <2%: Bob might be missing hallucinations

**Average Stress Test Latency** = Total time for stress tests
- Target: <500ms
- >1000ms: Optimize query efficiency

### Dashboard Query

```python
# After running a batch, calculate metrics:
metrics = {
    "total_queries": 100,
    "alerts_triggered": 6,        # 6% alert rate ✓
    "verified": 5,                # 83% verification rate ✓
    "quarantined": 1,             # 17% quarantine rate ✓
    "avg_stress_test_time": 250,  # 250ms latency ✓
}
```

---

## Design Rationale

### Why Orthogonal Tests?

If a result is genuinely good, it should hold up under different retrieval approaches:
- Semantic-only should still find the same docs
- STAT7-only should still find the same docs
- Stricter threshold should still find most of them

**If only one method works → isolated high score → likely artifact**

### Why Three Tests (Not More)?

Three tests cover:
1. Semantic relevance (Test 1)
2. Spatial relationships (Test 2)
3. Confidence robustness (Test 3)

Adding more tests would increase latency without much benefit. Three is optimal.

### Why Not Just Use Faculty Review?

Faculty review is expensive. Bob acts as a **high-precision first filter**:
- Most queries (95%) pass immediately (no overhead)
- Only suspicious queries (5%) get stress-tested
- Faculty only reviews the quarantined edge cases (1%)

This scales better than reviewing every result manually.

---

## Integration Points

### Logging
Bob logs to console and (optionally) Chronicle:
```
WARNING: 🔍 BOB ALERT: Suspicious result for query q1 (coherence=0.87, entanglement=0.25). Initiating stress test...
INFO: Bob Test 1: Pure semantic retrieval for query q1
INFO: Bob Test 2: Pure STAT7 retrieval for query q1
INFO: Bob Test 3: Higher confidence threshold for query q1
WARNING: ✅ BOB VERIFIED: Query q1 PASSED stress tests (consistency=0.90)
```

### Faculty Integration (Future)
```
Chronicle Entry:
- Event: BOB_VERIFIED or BOB_QUARANTINE
- Query ID: q1
- Coherence: 0.87
- Entanglement: 0.25
- Consistency: 0.90 or 0.42
- Action: APPROVED or PENDING_REVIEW
```

---

## Next Steps

1. **Run the full test suite:** See `TESTING-ZERO-TO-BOB.md`
2. **Use Bob in practice:** See `HOW-TO-BOB.md`
3. **Integrate with Faculty:** Build dashboard for quarantine review
4. **Measure accuracy:** Compare Bob's decisions with Faculty feedback
5. **Fine-tune thresholds:** Optimize for your specific use case