# Alchemist Quickstart (v0.1.0)

1. Choose a Gu Pot issue at distilled stage.
2. Scaffold manifest:
   alchemist scaffold --issue 123 --logline "..." --tension "..." --metric avg_frame_time_ms:reduce
3. Execute deterministic runs:
   alchemist run --manifest experiments/gu_pot/issue-123/manifest_v1.json --repeat 3
4. Validate claims:
   alchemist validate --issue 123
5. Review generated claims (hypotheses vs validated vs regressions).
6. Generate report:
   alchemist report --issue 123
7. Update Gu Pot issue Evidence Links section.
8. Promote stage (serum / antitoxin / compost / remain distilled).

CLI Command Concepts (future stubs)
- scaffold: Produce manifest from narrative fields
- run: Execute deterministic experiment(s)
- validate: Produce claims from run outputs
- report: Compile validated claims into report.md
- linkback: Update issue body + post comment

Manifest Essentials
{
  "schema_version": "0.1.0",
  "origin": {"type": "gu_pot", "issue_number": 123},
  "hypothesis": "...",
  "metrics": [
    {"name": "avg_frame_time_ms", "unit": "ms", "direction": "reduce", "precision": 2}
  ],
  "determinism": {"seed": 1337, "platform": "win64", "engine_version": "2025.1.0f1"}
}

Determinism Tips
- Pin engine version
- Explicit seed in both runtime and manifest
- Normalize logs (strip timestamps or isolate deterministic subset)
- Round metric values before hashing (define precision)

Confidence (placeholder)
confidence = w1*data_quality + w2*effect_strength - w3*variance_penalty
(Weights documented later; keep reproducible)

Provenance Block (report excerpt)
```
{
  "alchemist_version": "0.1.0",
  "claims": [...],
  "runs": [...],
  "hashes": [...]
}
```