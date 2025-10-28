# HOW-TO-BOB: Using Bob the Skeptic in Practice

**Quick reference for working with Bob in real scenarios**

---

## What Bob Does (In One Sentence)

Bob watches for query results that look perfect but are isolated—and he stress-tests them to catch hallucinations and dataset biases.

---

## Bob's Three Verdicts

### 🟢 PASSED
**What it means:** Normal result. No investigation needed.
- Coherence is not suspiciously high, OR
- Coherence is high but entanglement is also high (well-connected)
- Return the result immediately

**When you see this:** Trust the result. Bob didn't find anything suspicious.

### 🟡 VERIFIED
**What it means:** Result looked suspicious, but stress tests confirmed it's solid.
- High coherence (>0.85) + low entanglement (<0.30)
- BUT stress tests show consistency (≥85% of results hold up across retrieval methods)
- Bob's verdict: "Genuinely good despite isolation"

**When you see this:** Use the result with confidence. Bob checked it thoroughly.

### 🔴 QUARANTINED
**What it means:** Result looks good but falls apart under stress testing.
- High coherence (>0.85) + low entanglement (<0.30)
- Stress tests show inconsistency (<85% of results hold up)
- Possible hallucination, dataset bias, or artifact

**When you see this:** Don't use this result without human review. Escalate to Faculty.

---

## How to Trigger Bob

### Scenario 1: Normal Query (Bob Likely Won't Activate)

```powershell
python exp09_cli.py query `
  --query-id "normal_1" `
  --semantic "What is The Seed?"
```

**Result:**
```json
{
  "bob_status": "PASSED",
  "bob_verification_log": null
}
```
✅ Normal result. Bob didn't investigate.

### Scenario 2: Hybrid Query (Bob Might Investigate)

```powershell
python exp09_cli.py query `
  --query-id "hybrid_1" `
  --semantic "Tell me about consciousness" `
  --hybrid `
  --weight-semantic 0.6 `
  --weight-stat7 0.4
```

**Result if Bob activates:**
```json
{
  "bob_status": "VERIFIED",
  "bob_verification_log": {
    "stress_test_started": "2025-01-20T10:15:00",
    "original_result_ids": ["id1", "id2", "id3", "id4", "id5"],
    "tests_run": [
      {
        "test": "SEMANTIC_ONLY",
        "overlap_ratio": 0.88,
        "result_count": 5
      },
      {
        "test": "STAT7_ONLY",
        "overlap_ratio": 0.90,
        "result_count": 5
      },
      {
        "test": "HIGH_CONFIDENCE",
        "overlap_ratio": 0.92,
        "result_count": 4
      }
    ],
    "consistency_score": 0.90,
    "verdict": "CONSISTENT"
  }
}
```
✅ Bob investigated and verified the results.

### Scenario 3: Edge Case Query (Bob Quarantines)

```powershell
python exp09_cli.py query `
  --query-id "edge_1" `
  --semantic "What color is Tuesday?" `
  --hybrid `
  --weight-semantic 0.6 `
  --weight-stat7 0.4
```

**Result if Bob quarantines:**
```json
{
  "bob_status": "QUARANTINED",
  "bob_verification_log": {
    "stress_test_started": "2025-01-20T10:16:00",
    "original_result_ids": ["id_weird1", "id_weird2"],
    "tests_run": [
      {
        "test": "SEMANTIC_ONLY",
        "overlap_ratio": 0.35,
        "result_count": 2
      },
      {
        "test": "STAT7_ONLY",
        "overlap_ratio": 0.12,
        "result_count": 1
      },
      {
        "test": "HIGH_CONFIDENCE",
        "overlap_ratio": 0.21,
        "result_count": 0
      }
    ],
    "consistency_score": 0.23,
    "verdict": "DIVERGENT"
  }
}
```
🚨 Bob caught inconsistency. Don't use these results.

---

## Interpreting Bob's Stress Test Results

When Bob investigates (VERIFIED or QUARANTINED), look at these metrics:

### Overlap Ratio
**What:** % of original results found in re-test
- **0.90-1.00** → ✅ Strong consistency (same results)
- **0.75-0.90** → ⚠️ Moderate consistency (mostly same)
- **0.50-0.75** → ❌ Weak consistency (diverging)
- **< 0.50** → ❌❌ Divergent (completely different)

### Consistency Score
**What:** Average of all overlap ratios across 3 tests
- **≥ 0.85** → ✅ PASSED stress tests (Bob verifies)
- **< 0.85** → ❌ FAILED stress tests (Bob quarantines)

### Tests Breakdown

1. **SEMANTIC_ONLY** — Query without STAT7 addresses
   - Tests if high coherence comes from semantic relevance alone
   
2. **STAT7_ONLY** — Query without semantic weighting
   - Tests if high coherence comes from spatial relationships alone
   
3. **HIGH_CONFIDENCE** — Query with stricter threshold (+0.2)
   - Tests if borderline results are inflated

**If all 3 tests return similar results → genuinely good**
**If tests diverge dramatically → probably an artifact**

---

## Common Patterns

### Pattern A: "Perfect consistency across all methods"
```
Semantic:        0.92
STAT7:           0.90
High Confidence: 0.88
Consistency:     0.90 → VERIFIED ✅
```
**Interpretation:** Result is genuinely good. It holds up no matter which retrieval method you use.

### Pattern B: "High in semantic, low in STAT7"
```
Semantic:        0.88
STAT7:           0.15
High Confidence: 0.42
Consistency:     0.48 → QUARANTINED 🚨
```
**Interpretation:** Result relies entirely on semantic similarity. Probably not grounded in spatial/address relationships. May be a hallucination.

### Pattern C: "All tests fail"
```
Semantic:        0.12
STAT7:           0.08
High Confidence: 0.05
Consistency:     0.08 → QUARANTINED 🚨
```
**Interpretation:** Nothing is consistent. Definite hallucination or severe dataset bias.

### Pattern D: "Borderline but consistent"
```
Semantic:        0.68
STAT7:           0.72
High Confidence: 0.70
Consistency:     0.70 → QUARANTINED 🚨 (just barely fails)
```
**Interpretation:** Moderately consistent but below threshold. Might be worth human review, or tune Bob's threshold.

---

## What to Do When Bob Quarantines

### Option 1: Accept the Verdict
"Bob found inconsistency. I'll skip this result and query again."

```powershell
# Run a new query
python exp09_cli.py query `
  --query-id "retry_1" `
  --semantic "Different approach to same question"
```

### Option 2: Escalate to Faculty (Future)
"Bob quarantined this. Flag it for human review."

(Implementation in progress. For now, log the `bob_verification_log` and review manually.)

### Option 3: Examine What Bob Found
"I want to understand why Bob quarantined this."

```powershell
# Look at the stress test results
Get-Content "bob_stress_results.json" | ConvertFrom-Json | Where-Object { $_.bob_status -eq "QUARANTINED" } | ForEach-Object {
  Write-Host "Query: $($_.query_id)"
  Write-Host "Consistency Score: $($_.bob_verification_log.consistency_score)"
  Write-Host "Tests:"
  $_.bob_verification_log.tests_run | ForEach-Object {
    Write-Host "  $($_.test): $($_.overlap_ratio)"
  }
}
```

---

## Tuning Bob (If He's Wrong)

### Bob is TOO PARANOID (quarantining good results)

**In `exp09_api_service.py`, edit lines 71-80:**
```python
class BobSkepticConfig:
    COHERENCE_HIGH_THRESHOLD = 0.90          # Raise from 0.85
    ENTANGLEMENT_LOW_THRESHOLD = 0.30        # Keep same
    STRESS_TEST_DIVERGENCE_THRESHOLD = 0.20  # Raise from 0.15
```

**Effect:** Fewer quarantines, faster queries, fewer false positives.

### Bob is NOT PARANOID ENOUGH (missing hallucinations)

**In `exp09_api_service.py`, edit lines 71-80:**
```python
class BobSkepticConfig:
    COHERENCE_HIGH_THRESHOLD = 0.80          # Lower from 0.85
    ENTANGLEMENT_LOW_THRESHOLD = 0.25        # Lower from 0.30
    STRESS_TEST_DIVERGENCE_THRESHOLD = 0.10  # Lower from 0.15
```

**Effect:** More quarantines, slower queries, catch more hallucinations.

### Bob is TOO SLOW (stress tests taking too long)

**Reduce max_results in stress test queries:**

In `exp09_api_service.py`, find `_stress_test_result()` and change:
```python
max_results=5  # Reduce from 10
```

---

## Metrics to Monitor

After running a batch of queries:

```powershell
python exp09_cli.py metrics --json-output
```

**Key numbers:**
- **Alert Rate:** % of queries Bob flags (should be 1-5%)
- **Verification Rate:** % of alerts that pass (should be 80-95%)
- **Average latency:** Extra time from stress testing (should be <500ms)

---

## Decision Tree: Should I Use This Result?

```
Is bob_status = "PASSED"?
  ├─ YES → Use it ✅
  └─ NO

Is bob_status = "VERIFIED"?
  ├─ YES → Use it ✅ (Bob checked it)
  └─ NO

Is bob_status = "QUARANTINED"?
  ├─ YES
  │  ├─ High stakes decision? → Get human review 👤
  │  ├─ Low stakes decision? → Get different result 🔄
  │  └─ Debugging? → Examine bob_verification_log 🔍
  └─ UNKNOWN → Something went wrong 💥
```

---

## Next: Deep Dive

Want to understand Bob's internals? See `HOW-BOB-WORKS.md`

Want to run the full test suite? See `TESTING-ZERO-TO-BOB.md`