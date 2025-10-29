# Testing The Seed System

This folder contains all documentation for testing and validating The Seed's STAT7 addressing system and the Bob the Skeptic anti-cheat filter.

## Documents

### [TESTING-ZERO-TO-BOB.md](./TESTING-ZERO-TO-BOB.md)
**The complete linear test suite for AuDHD users**

Start here if you want to run all validation experiments (EXP-01 through EXP-10) from beginning to end. This is a single, self-contained PowerShell guide with:
- Step-by-step instructions (no context switching)
- Expected outputs at each step
- Troubleshooting section
- Sequential flow from address uniqueness through Bob's skeptic validation

**Read this if:** You need to run the full test suite or understand what each experiment does.

### [HOW-TO-BOB.md](./HOW-TO-BOB.md)
**Practical guide: Running Bob in your queries**

How to use Bob in real scenarios. Covers:
- Running queries that trigger Bob
- Interpreting Bob's verdicts
- Examples: PASSED vs VERIFIED vs QUARANTINED
- Common patterns and what they mean
- When to trust Bob's decisions

**Read this if:** You want to use Bob in production or understand what to do when Bob quarantines a result.

### [HOW-BOB-WORKS.md](./HOW-BOB-WORKS.md)
**Technical deep-dive: Bob's architecture and design**

Internal design of Bob the Skeptic:
- Detection layer (thresholds)
- Stress testing (orthogonal retrieval methods)
- Resolution logic (PASSED/VERIFIED/QUARANTINED)
- How to tune Bob's sensitivity
- Configuration parameters and what they do
- Debugging and monitoring

**Read this if:** You need to tune Bob, debug why he's misbehaving, or understand the math behind his decisions.

---

## Quick Start

**Just want to test?** → Go to `TESTING-ZERO-TO-BOB.md` and start from PART 0.

**Just want to use Bob?** → Go to `HOW-TO-BOB.md` for examples.

**Need to fix Bob?** → Go to `HOW-BOB-WORKS.md` and look for "Tuning Bob" section.

---

## Related Documentation

- **Experiment Details:** See `../TheSeedConcept/Experiments/EXPERIMENTS-REFERENCE.md`
- **STAT7 Concept:** See `../TheSeedConcept/START_HERE.md`
- **Architecture:** See `../TheSeedConcept/README.md`