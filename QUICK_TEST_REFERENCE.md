# Quick Test Reference Card

**Ctrl+C friendly version - Bookmark this**

---

## 3-Step Setup

```
1. Restart JetBrains Rider
2. View → Tool Windows → Unit Tests
3. Wait 10 seconds for discovery
```

**Done.** Tests now appear in IDE.

---

## 5 Ways to Run Tests

### Way 1: Run ALL Tests (Simplest)
```
Run → Run All Tests
```
Or: `Ctrl+Shift+F10` (Windows)

### Way 2: Run ONE Test (Click Arrow)
1. Open any `test_*.py` file
2. Click green ▶ next to function name
3. Results show at bottom

### Way 3: Run Experiment Group
1. View → Tool Windows → Unit Tests
2. Expand `test_exp06_*`
3. Right-click → Run

### Way 4: Debug Test (Add Breakpoints)
1. Click on a line in test
2. Press `Ctrl+F8` to set breakpoint
3. Click green ▶ next to function → Debug
4. Use normal IDE debugger

### Way 5: Terminal (Still Works)
```bash
pytest                      # All tests
pytest -m exp06             # EXP-06 only
pytest tests/test_exp06_*.py -v  # Specific file
```

---

## Test Organization in IDE

```
Unit Tests Panel:
├── test_exp06_entanglement_math (5 tests)
│   ├── test_determinism
│   ├── test_symmetry
│   ├── test_boundedness
│   ├── test_component_bounds
│   └── test_separation_proof
├── test_exp06_simple_validation (4 tests)
├── test_exp06_robustness (13 tests)
├── test_exp06_score_histogram
├── test_exp06_debug_scores
├── test_exp06_final_validation
├── test_experiment_harness (7 tests)
├── test_semantic_anchors
├── stress/
│   └── test_stat7_reproducibility
└── [30+ other system tests]
```

Click any test or group → Green play button appears → Click to run

---

## What Tests Exist

| Test File | Tests | What It Tests |
|-----------|-------|---------------|
| test_exp06_entanglement_math.py | 5 | Mathematical proof (determinism, symmetry, bounds) |
| test_exp06_simple_validation.py | 4 | Score validation and thresholds |
| test_exp06_robustness.py | 13 | Edge cases, adversarial attacks, stress |
| test_experiment_harness.py | 7 | Experiment framework |
| test_semantic_anchors.py | Multiple | Semantic navigation |
| test_exp06_score_histogram.py | 1 | Score distribution |
| test_exp06_debug_scores.py | 1 | Score breakdown |
| test_exp06_final_validation.py | 1 | End-to-end validation |
| test_stat7_reproducibility.py | Multiple | STAT7 consistency |
| [System tests] | 30+ | Self-care, plugins, DTT vault, etc. |

**Total: 70+ tests, all discoverable**

---

## Common Tasks

### Task: Run all EXP-06 tests
```
View → Unit Tests → Expand test_exp06_entanglement_math
                 → Expand test_exp06_simple_validation
                 → Expand test_exp06_robustness
Right-click on group → Run
```

Or terminal:
```bash
pytest -m exp06
```

### Task: Debug a specific test
```
1. Open test_exp06_entanglement_math.py
2. Click on a line inside test_determinism()
3. Press Ctrl+F8 to set breakpoint (red dot appears)
4. Click green play arrow next to test_determinism()
5. Click green arrow next to function → "Debug"
6. Debugger stops at breakpoint - step through code
```

### Task: See test results with details
```
Run → Run All Tests
Results panel shows:
  ✓ test_determinism ... 0.5s
  ✓ test_symmetry ... 0.3s
  ✓ test_boundedness ... 0.4s
  ... etc
```

Click on any test name → See console output

### Task: Run tests from terminal (quick)
```bash
# All tests
pytest

# Only EXP-06
pytest -m exp06

# Only robustness tests
pytest -m robustness

# Specific file with verbose output
pytest tests/test_exp06_entanglement_math.py -v

# Show print statements while running
pytest -v -s

# With coverage report
pytest --cov=seed --cov-report=html
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests not appearing in IDE | Restart Rider, then View → Tool Windows → Unit Tests |
| "ModuleNotFoundError" when running test | conftest.py handles sys.path - make sure it's in tests/ directory |
| Test file marked as non-test file | Check filename starts with `test_` and functions start with `test_` |
| Tests fail with import errors | Verify seed/engine files exist: `ls seed/engine/stat7_entity.py` |
| IDE shows "pytest not installed" | Run: `pip install pytest` |

---

## Files That Make This Work

```
pytest.ini          ← Tells IDE where tests are
pyproject.toml      ← Python project config
tests/conftest.py   ← Test setup (imports, fixtures)
```

You don't need to edit these. They just work.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F10` | Run All Tests |
| `Ctrl+F8` | Set/remove breakpoint |
| Green play ▶ | Run test (or press Ctrl+Shift+F10 in file) |
| `F9` | Step over (when debugging) |
| `F7` | Step into function |
| `Shift+F8` | Step out of function |

---

## One-Liners

```
# Run all tests
pytest

# Run and stop on first failure
pytest -x

# Run EXP-06 tests only
pytest -m exp06

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_exp06_entanglement_math.py::test_determinism -v

# Run tests in parallel (faster)
pytest -n auto
```

---

## Remember

- ✅ Tests auto-discover in IDE (nothing to configure)
- ✅ Click green play button to run
- ✅ Results show immediately
- ✅ No terminal needed for basic testing
- ✅ Full IDE debugger available

**That's it.** It just works.
