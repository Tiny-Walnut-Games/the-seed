# The Seed Validation Experiments

This folder contains reference documentation for all 10 validation experiments (EXP-01 through EXP-10) that prove The Seed's STAT7 addressing system works.

## Quick Links

For detailed walkthrough with PowerShell commands, see: `../../testing/TESTING-ZERO-TO-BOB.md`

For quick reference of what each experiment tests, see: `./EXPERIMENTS-REFERENCE.md`

---

## The 10 Experiments at a Glance

| Exp | Name | Tests | Status |
|-----|------|-------|--------|
| **EXP-01** | Address Uniqueness | Do STAT7 addresses have zero collisions? | ✅ PASS |
| **EXP-02** | Retrieval Efficiency | Can we retrieve data sub-millisecond? | ✅ PASS |
| **EXP-03** | Dimension Necessity | Are all 7 STAT7 dimensions needed? | ✅ PASS |
| **EXP-04** | Fractal Scaling | Does STAT7 work at 1M+ scale? | ✅ PASS |
| **EXP-05** | Compression/Expansion | Lossless encoding to LUCA? | ✅ PASS |
| **EXP-06** | Entanglement Detection | Can we find relationships between bit-chains? | ✅ PASS |
| **EXP-07** | LUCA Bootstrap | Can we reconstruct the entire system? | ⏳ Pending |
| **EXP-08** | RAG Integration | Does it connect to your storage? | ⏳ Pending |
| **EXP-09** | Concurrency | Thread-safe under parallel queries? | ✅ PASS |
| **EXP-10** | Bob the Skeptic | Anti-cheat validation filter | ✅ PASS |

---

## Phase Structure

### Phase 1: Foundational (EXP-01, EXP-02, EXP-03)
Proves the core addressing mechanism works:
- Addresses are unique
- Retrieval is fast
- All 7 dimensions are necessary

**When to run:** First. These are prerequisites.

### Phase 2: Scaling & Architecture (EXP-04, EXP-05, EXP-06)
Proves the system scales and handles complexity:
- Works at massive scale (1M items)
- Can compress and expand without data loss
- Can detect meaningful relationships

**When to run:** After Phase 1 passes.

### Phase 3: Integration & Validation (EXP-07, EXP-08, EXP-09, EXP-10)
Proves real-world readiness:
- Can bootstrap from LUCA
- Integrates with your RAG system
- Handles concurrent queries
- Catches hallucinations

**When to run:** After Phase 2 passes.

---

## Running Tests

### Option 1: Linear Test Suite (Recommended)
```powershell
# See: ../../testing/TESTING-ZERO-TO-BOB.md
# This walks you through all tests step-by-step
```

**Best for:** First time, AuDHD compatibility, learning what each test does.

### Option 2: Individual Experiments
```powershell
# In: E:\Tiny_Walnut_Games\the-seed\seed\engine

# Run specific experiment
python exp04_fractal_scaling.py
python exp06_entanglement_detection.py
# etc.
```

**Best for:** Debugging a specific test, rerunning after changes.

### Option 3: Batch Testing
```powershell
# Run all Phase 1 tests
python stat7_experiments.py --run-all

# Run all Phase 2 tests
python run_exp_phase2.py
```

**Best for:** CI/CD, automated validation.

---

## Understanding Results

### Success Criteria by Phase

**Phase 1 (EXP-01, 02, 03):**
- Zero collisions across all iterations
- Sub-millisecond retrieval (< 1ms average)
- All 7 dimensions contribute to uniqueness

**Phase 2 (EXP-04, 05, 06):**
- Logarithmic scaling (1000x data = ~4x latency increase)
- 100% lossless compression/expansion
- High-precision entanglement detection (>80% accuracy)

**Phase 3 (EXP-07, 08, 09, 10):**
- Full system reconstruction from LUCA
- Seamless RAG integration
- Concurrent queries with 0 race conditions
- Hallucination detection >90% precision

### Interpreting Failure

If an experiment fails:

1. **Check the error message** — Is it a code bug, configuration issue, or fundamental problem?
2. **Review prerequisites** — Did you run Phase 1 first?
3. **Inspect test data** — Are you using the right bit-chains and parameters?
4. **Consult documentation** — Each experiment has a detailed explanation
5. **Enable debug logging** — Add `--verbose` to see what's happening

---

## Documentation

Each experiment has:
- **Hypothesis** — What we're trying to prove
- **Method** — How we test it
- **Expected Results** — What success looks like
- **Implications** — What it means for The Seed

See `EXPERIMENTS-REFERENCE.md` for quick details on each.

---

## Related Documentation

- **Architecture:** `../START_HERE.md`
- **STAT7 Specification:** `../Roadmaps/03-BIT-CHAIN-SPEC.md`
- **Validation Guide:** `../Roadmaps/04-VALIDATION-EXPERIMENTS.md`
- **Testing Guide:** `../../testing/TESTING-ZERO-TO-BOB.md`
- **Bob the Skeptic:** `../../testing/HOW-BOB-WORKS.md`