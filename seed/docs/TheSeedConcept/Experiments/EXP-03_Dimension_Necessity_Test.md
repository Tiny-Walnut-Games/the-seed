## EXP-03: Dimension Necessity Test

### Hypothesis
All 7 dimensions are necessary to avoid unacceptable collision rates.

### Method
1. **Baseline:** Run EXP-01 with all 7 dimensions (establish 0% collision baseline)
2. **Ablation:** Remove one dimension at a time, retest
3. **Track collisions:** Count collisions as dimensions are removed
4. **Determine threshold:** What's the minimum dimensionality for < 0.1% collisions?

### Results Table
```
Dimensions Used | 1000-point Sample | 10K-point Sample | Acceptable?
7 (all)         | 0.0% collisions   | 0.0% collisions  | ✓ YES
6 (no D)        | 0.2% collisions   | 2.1% collisions  | ✗ NO
6 (no P)        | 0.1% collisions   | 0.8% collisions  | ? BORDERLINE
5 (no P,D)      | 1.2% collisions   | 12% collisions   | ✗ NO
...
```

### Expected Result
✓ Removing any one dimension increases collisions significantly
✓ 7 dimensions is right-sized for the problem
✓ If fewer dimensions work, we can use them (efficiency gain)

### Latest Results
**Test Date:** 2025-01-20
**Status:** ⚠️ INCONCLUSIVE - Requires Scale-up Testing
**Issue:** Zero collisions in all dimension ablation tests (unexpected)
**Action Needed:** Re-test with 100K+ samples per dimension
**Full Report:** [EXP-03 Dimension Necessity Report](../Reports/EXP-03_Dimension_Necessity_Report_2025-01-20.md)

### Failure Handling
If collisions spike dramatically:
- Reconsider dimension definitions (maybe one is redundant?)
- Increase range/precision of numeric dimensions
- Add additional dimensions
