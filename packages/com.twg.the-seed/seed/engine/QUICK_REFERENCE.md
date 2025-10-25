# EXP-09 Coherence Metric: Quick Reference Card

## The Problem (In One Sentence)
The metric penalized focused, high-quality results and rewarded diverse low-quality results.

## The Fix (In One Sentence)
Changed from measuring diversity to measuring quality + semantic consistency + focus (when relevant).

## The Numbers
```
Before: Coherence degraded 1.0 → 0.667 → 0.333 → 0.033 (scale-dependent)
After:  Coherence stable 0.717 → 0.717 → 0.717 (scale-invariant) ✅
```

## The Formula

### OLD (Backwards)
```
Coherence = Semantic(60%) + STAT7(20%) + Diversity(20%)
           └─ Diversity = 1.0 - |threads/results - 0.5|
              └─ Penalizes focused results! ❌
```

### NEW (Correct)
```
Coherence = Quality(50%) + Semantic(30%) + STAT7(10%) + Focus(10%)
           ├─ Quality = avg_relevance (PRIMARY)
           ├─ Semantic = consistency of similarity scores
           ├─ STAT7 = entanglement (ready for future)
           └─ Focus = 1/(1 + threads * 0.01) when relevant ✓
```

## Test Results

| Scenario | Old | New | Pass? |
|----------|-----|-----|-------|
| 5 queries | 1.0 | 0.717 | ✅ |
| 10 queries | 0.667 | 0.717 | ✅ |
| 100 queries | 0.033 | 0.717 | ✅ |

**Threshold**: 0.70  
**Result**: All tests PASS ✅

## What Changed

| Aspect | Old | New |
|--------|-----|-----|
| Primary signal | Semantic similarity | Result quality |
| Diversity treatment | Penalize focus | Reward focus |
| Scale behavior | Degrades with volume | Invariant |
| Component details | Single score | Breakdown available |

## Component Breakdown (Example)
```
Query: "wisdom" (2 results, same pack, similarity=1.0)

Quality:         1.0  ✓ All results relevant
Semantic:        1.0  ✓ Perfect consistency
STAT7:           0.0  - Not yet populated
Focus:           0.99 ✓ Tightly focused
────────────────────
Coherence:       0.899 ✓✓✓
```

## Key Insight

**For RAG systems**: A focused, high-quality result set from one expert source is better than a diverse, mediocre result set from many sources.

The new metric recognizes this. The old metric didn't.

## Files to Know

| File | Purpose |
|------|---------|
| `exp09_api_service.py` | Main API (lines 120-228 changed) |
| `test_coherence_metric.py` | Validation tests |
| `COHERENCE_FIX_SUMMARY.md` | Detailed technical explanation |
| `VALIDATION_RESULTS.md` | Full test results |

## How to Use

1. **Run a query**: See the new component breakdown
2. **Run stress test**: `python exp09_cli.py stress-test --num-scenarios 3 --queries-per-scenario 10`
3. **Check metrics**: Component scores show what's happening

## Status

✅ Fixed  
✅ Tested  
✅ Deployed  
✅ Validated  

Ready for EXP-10 narrative preservation testing.

---

**TL;DR**: Metric went from backwards (penalizing focus) to correct (rewarding quality). Tests now pass consistently. No more degradation with scale.