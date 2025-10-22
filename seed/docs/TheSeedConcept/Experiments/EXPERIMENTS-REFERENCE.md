# Experiments Reference: EXP-01 through EXP-10

**Quick reference for all 10 validation experiments. For detailed testing instructions, see `../../testing/TESTING-ZERO-TO-BOB.md`**

---

## PHASE 1: Foundational Tests

### EXP-01: Address Uniqueness
**Goal:** Prove STAT7 addresses have zero collisions

**What it tests:**
- Generate 1000+ random bit-chains with random STAT7 coordinates
- Compute address hash for each (SHA256)
- Count collisions

**Expected Result:**
- 0 collisions across 10 iterations
- 100% unique addresses

**Latest Status:** ✅ **PASSED**
- Date: 2025-01-20
- Collisions: 0/10,000 (0.000%)

**Failure Means:**
- STAT7 dimensions aren't sufficiently distinct
- Hash function has collisions (unlikely)
- Need to add 8th dimension or increase hash space

---

### EXP-02: Retrieval Efficiency
**Goal:** Prove STAT7 retrieval is sub-millisecond

**What it tests:**
- Generate 10,000 bit-chains
- Measure retrieval latency for random lookups
- Check p95/p99 percentiles

**Expected Result:**
- Mean latency: <1ms
- p95 latency: <5ms
- Throughput: >10,000 addresses/second

**Latest Status:** ✅ **PASSED**
- Mean latency: 0.000211ms
- Throughput: 13,000 addresses/sec

**Failure Means:**
- Index structure is inefficient (need B-tree or hash table optimization)
- Hardware bottleneck
- Network latency if distributed

---

### EXP-03: Dimension Necessity
**Goal:** Prove all 7 STAT7 dimensions are needed

**What it tests:**
- Generate bit-chains with all 7 dimensions
- Generate bit-chains with only 6 dimensions (drop one at a time)
- Compare collision rates

**Expected Result:**
- 7D: 0 collisions
- 6D (any): Significantly more collisions
- Conclusion: All 7 dimensions are necessary

**Latest Status:** ✅ **PASSED**
- 7D collision rate: 0%
- 6D collision rates: 2-8% (dimension-dependent)

**Failure Means:**
- Some dimensions are redundant
- STAT7 model needs redesign
- Some dimensions don't contribute uniqueness

---

## PHASE 2: Scaling & Architecture Tests

### EXP-04: Fractal Scaling
**Goal:** Prove STAT7 scales logarithmically

**What it tests:**
- Generate 1K → 10K → 100K → 1M bit-chains
- Measure collisions and latency at each scale
- Verify latency grows logarithmically

**Expected Result:**
- 0 collisions at all scales
- Latency increases ~4x for 1000x data
- Logarithmic scaling confirmed

**Latest Status:** ✅ **PASSED**
- Date: 2025-10-18
- Scales tested: 1K, 10K, 100K, 1M
- Max latency: 0.000665ms at 100K
- Scaling ratio: 4.21x (for 1000x increase) ✓

**Failure Means:**
- Linear or exponential degradation (system doesn't scale)
- Collision rate increases (addressing breaks at scale)
- Need distributed addressing scheme

---

### EXP-05: Compression/Expansion
**Goal:** Prove lossless encoding to LUCA

**What it tests:**
- Create 1000 bit-chains with full context
- Compress each to minimal LUCA form
- Expand back to original
- Compare: original == expanded?

**Expected Result:**
- 100% lossless (no data loss)
- Compression ratio: >50% smaller
- Expansion recreates original exactly

**Latest Status:** ✅ **PASSED**
- Losslessness: 100% match
- Compression cycles: 5 iterations successful
- No degradation on recompression

**Failure Means:**
- Information loss during compression
- LUCA bootstrap incomplete
- Expansion algorithm is incorrect

---

### EXP-06: Entanglement Detection
**Goal:** Prove we can find relationships between bit-chains

**What it tests:**
- Generate 500 bit-chains with known relationships
- Compute entanglement matrix (polarity + resonance)
- Detect high-resonance pairs
- Verify against ground truth

**Expected Result:**
- High precision (>85% of detected pairs are real)
- High recall (>80% of real pairs are detected)
- Math validated (polarity calculations correct)

**Latest Status:** ✅ **PASSED**
- High-resonance pairs detected: 157/500
- Math validation: Verified
- Precision: >85%

**Failure Means:**
- Polarity/resonance calculation is wrong
- Entanglement algorithm misses relationships
- Need different relationship model

---

## PHASE 3: Integration & Validation Tests

### EXP-07: LUCA Bootstrap
**Goal:** Prove we can reconstruct entire system from LUCA

**What it tests:**
- Compress full system to LUCA (irreducible minimum)
- Bootstrap: Can we unfold LUCA back to full system?
- Compare: bootstrapped system == original?

**Expected Result:**
- Full reconstruction possible
- No information loss
- System is self-contained and fractal

**Latest Status:** ⏳ **PENDING**
- Implementation: In progress
- Expected: Next milestone

**Success Means:**
- LUCA is true ground state
- System is fractal (self-similar at all scales)
- Can recover from LUCA alone

---

### EXP-08: RAG Integration
**Goal:** Prove The Seed connects to your storage system

**What it tests:**
- Take real documents from your RAG
- Generate STAT7 addresses for each
- Retrieve via STAT7 addresses + semantic queries
- Verify both methods find correct documents

**Expected Result:**
- All documents addressable
- Hybrid retrieval works (STAT7 + semantic)
- No conflicts with existing RAG

**Latest Status:** ⏳ **PENDING**
- Implementation: Awaiting RAG integration
- Expected: Phase 3 completion

**Failure Means:**
- STAT7 doesn't map to your document model
- Hybrid retrieval causes conflicts
- Need design adjustment

---

### EXP-09: Concurrency & Thread Safety
**Goal:** Prove system handles concurrent queries

**What it tests:**
- Launch 20 parallel queries
- Verify no race conditions
- Check result consistency under load
- Measure throughput

**Expected Result:**
- 20/20 queries succeed
- No data corruption
- Throughput: >100 queries/second
- Narrative coherence preserved

**Latest Status:** ✅ **PASSED**
- Concurrent queries: 20/20 successful
- No race conditions detected
- Throughput: 150+ queries/sec

**Failure Means:**
- Index is not thread-safe (needs locking)
- Hash collisions under concurrent access
- Need distributed locking mechanism

---

### EXP-10: Bob the Skeptic
**Goal:** Prove anti-cheat filter catches hallucinations

**What it tests:**
- Query system with intentional hallucinations + good results
- Bob detects suspicious patterns (high coherence + low entanglement)
- Bob stress-tests suspicious results
- Compare: Bob's quarantines match Faculty decisions

**Expected Result:**
- Bob detects 90%+ of hallucinations
- False positive rate <5%
- Stress tests are reliable indicator

**Latest Status:** ✅ **PASSED**
- Hallucination detection: >90%
- False positive rate: <3%
- Stress test consistency: >85%

**Failure Means:**
- Thresholds are wrong (too loose or strict)
- Stress test methodology isn't catching artifacts
- Need different detection approach

---

## Success Checklist

If all tests pass:

- ✅ **Phase 1 (EXP-01, 02, 03):** Addressing system is sound
- ✅ **Phase 2 (EXP-04, 05, 06):** System scales and handles complexity
- ✅ **Phase 3 (EXP-07, 08, 09, 10):** Production-ready

**Recommendation:** Proceed to implementation and real-world testing.

---

## Running Tests

### Linear Test Suite (Recommended)
```powershell
# See: ../../testing/TESTING-ZERO-TO-BOB.md
```

### Individual Test
```powershell
cd E:\Tiny_Walnut_Games\the-seed\seed\engine
python exp06_entanglement_detection.py
```

### Phase Batch
```powershell
python stat7_experiments.py --run-all  # EXP-01, 02, 03
python run_exp_phase2.py               # EXP-04, 05, 06
```

---

## Interpreting Results

### Phase 1 Results

**All Pass → Address system is solid. Proceed to Phase 2.**

**EXP-01 Fails → Collisions detected. 7 dimensions insufficient.**
- Add 8th dimension (orthogonal to others)
- Or switch to larger hash (SHA-512)

**EXP-02 Fails → Retrieval is slow.**
- Profile to find bottleneck (hash computation? index lookup?)
- Optimize index structure (B-tree? distributed?)

**EXP-03 Fails → Dimension(s) are redundant.**
- Analyze which dimensions don't contribute
- Redesign STAT7 (remove or replace that dimension)

---

### Phase 2 Results

**All Pass → Architecture is proven. Proceed to Phase 3.**

**EXP-04 Fails → Doesn't scale.**
- Check collision rate increase at each scale
- If logarithmic, acceptable
- If exponential, redesign addressing

**EXP-05 Fails → Compression is lossy.**
- Debug LUCA bootstrap algorithm
- Check encoding/decoding symmetry
- Verify all fields are preserved

**EXP-06 Fails → Entanglement detection broken.**
- Review polarity calculation
- Check resonance formula
- Compare against manual ground truth

---

### Phase 3 Results

**All Pass → System is production-ready.**

**EXP-07 Fails → LUCA bootstrap incomplete.**
- Verify LUCA definition (irreducible minimum)
- Check unfolding algorithm (fractal expansion)

**EXP-08 Fails → RAG integration broken.**
- Check document-to-bit-chain mapping
- Verify hybrid retrieval combines scores correctly

**EXP-09 Fails → Thread safety issue.**
- Add locking to index modifications
- Review concurrent access patterns
- Use thread-safe data structures

**EXP-10 Fails → Bob is miscalibrated.**
- See: `../../testing/HOW-BOB-WORKS.md` → Tuning section
- Adjust COHERENCE_HIGH_THRESHOLD or STRESS_TEST_DIVERGENCE_THRESHOLD

---

## Results Files

After each test run, results are saved:

| Experiment | Output Location |
|------------|-----------------|
| EXP-01, 02, 03 | Console + `Reports/EXP-01_*.md` |
| EXP-04 | `results/exp04_*.json` |
| EXP-05 | `results/exp05_*.json` |
| EXP-06 | Console + entanglement matrix |
| EXP-09 | HTTP responses (if running API) |
| EXP-10 | Metrics from Bob logs |

---

## Next Steps

1. **First time?** → Run `../../testing/TESTING-ZERO-TO-BOB.md` for guided walkthrough
2. **Rerunning tests?** → Use individual `python exp0X_*.py` commands
3. **Need to debug?** → Check latest results files + check `HOW-BOB-WORKS.md` for tuning
4. **Ready for production?** → Start Phase 3 tests (EXP-07, 08, 09, 10)

---

**Last Updated:** 2025  
**Status:** Phase 1 & 2 Complete, Phase 3 In Progress  
**Ownership:** The Seed Project