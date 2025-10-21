# Pytest IDE Integration Guide

**Status:** ✅ Complete - Tests now discoverable in JetBrains Rider

---

## What Just Changed

You now have **IDE-integrated test discovery**. This means:
- ✅ JetBrains Rider automatically discovers all `test_*.py` files
- ✅ You can run tests from the IDE menu (no manual pytest commands)
- ✅ Tests are organized by experiment in the test panel
- ✅ You can filter and run specific test groups
- ✅ Full IDE debugging support

---

## How to Run Tests in JetBrains Rider

### Method 1: Run All Tests
1. Go to **Run** menu → **Run All Tests** (or press `Ctrl+Shift+F10` on Windows)
2. Rider discovers and runs all tests in the `tests/` directory
3. Results show in the test panel

### Method 2: Run Tests by Experiment
1. Open the **Test** panel (View → Tool Windows → Unit Tests)
2. Expand the tree to see tests organized by:
   - `test_exp06_*` - EXP-06 Entanglement Detection tests (25+ tests)
   - `test_experiment_harness.py` - Experiment framework tests
   - `test_semantic_anchors.py` - Semantic navigation tests
   - etc.
3. Right-click on any test or group → **Run**

### Method 3: Run Single Test File
1. Open any `test_*.py` file
2. Click the green play icon next to the class or function name
3. Or use `Ctrl+Shift+F10` (Windows) with cursor in test function

### Method 4: Run Tests by Marker (Experiment Type)
```bash
# Run only EXP-06 tests
pytest -m exp06

# Run only robustness tests
pytest -m robustness

# Run only math validation tests
pytest -m math
```

---

## File Structure (Now Organized)

```
the-seed/
├── pytest.ini                          # ✅ NEW: Pytest configuration
├── pyproject.toml                      # ✅ NEW: Python project metadata
├── tests/
│   ├── conftest.py                     # ✅ NEW: Pytest fixtures & setup
│   ├── test_exp06_entanglement_math.py          # 5 math tests
│   ├── test_exp06_simple_validation.py          # 4 validation tests
│   ├── test_exp06_robustness.py                 # 13 robustness tests
│   ├── test_exp06_score_histogram.py
│   ├── test_exp06_debug_scores.py
│   ├── test_exp06_final_validation.py
│   ├── test_experiment_harness.py     # 7 harness tests
│   ├── test_semantic_anchors.py
│   ├── stress/
│   │   └── test_stat7_reproducibility.py
│   └── agent-profiles/
│       └── test_agent_profile_validation.py
└── seed/
    └── engine/
        ├── stat7_entity.py
        ├── stat7_experiments.py
        ├── exp04_fractal_scaling.py
        ├── exp05_compression_expansion.py
        ├── exp06_entanglement_detection.py
        └── results/
            ├── exp04_*.json
            ├── exp05_*.json
            └── exp06_*.json
```

---

## What Tests Are Available

### EXP-06: Entanglement Detection (25+ Tests) ✅
- **Math Validation** (5 tests)
  - Determinism test
  - Symmetry test (A→B = B→A)
  - Boundedness test (scores in [0,1])
  - Component bounds test
  - Separation proof

- **Validation** (4 tests)
  - Threshold sweep
  - Confusion matrix
  - Score distribution
  - Artifact handling

- **Robustness** (13 tests)
  - Cross-validation
  - Threshold plateau detection
  - Adversarial perturbations
  - Stress cases (high dimensionality, sparse data)
  - Label leakage audit

- **Distribution & Debug** (3+ tests)
  - Score histogram visualization
  - Debug score breakdowns
  - Final validation (100% precision/recall)

### Experiment Harness (7 Tests) ✅
- Manifest loading
- Execution pipeline
- Benchmarking
- A/B evaluation
- Persistence

### Other Test Suites
- Semantic anchors
- STAT7 reproducibility
- Agent profile validation
- +30 other system tests

---

## Pytest Configuration Details

### `pytest.ini`
- Configures test discovery (looks in `tests/` directory)
- Defines markers for organizing experiments
- Sets output verbosity

### `pyproject.toml`
- Python 3.9+ compatibility
- Project metadata
- Tool configuration (black, mypy, coverage)
- Optional dependencies for development

### `tests/conftest.py`
- Sets up sys.path so imports work (adds `seed/engine` to path)
- Provides fixtures for shared test data
- Auto-marks tests based on filenames
- Configures logging

---

## Troubleshooting

### Tests Not Appearing in IDE
1. **Refresh test discovery**: Go to **Run** → **Edit Configurations** → Click refresh icon
2. **Check pytest.ini**: Should be at project root (E:/Tiny_Walnut_Games/the-seed/pytest.ini)
3. **Verify conftest.py**: Should be in tests/ directory
4. **Reload project**: File → Reload All from Disk

### Import Errors When Running Tests
- The `conftest.py` file automatically adds `seed/engine` to sys.path
- If still broken: Check that you're running from IDE, not terminal

### Tests Running but All Failing
- Could be missing dependencies (numpy, pydantic, pyyaml)
- Run: `pip install pytest pytest-cov numpy pydantic pyyaml`

---

## Command Line (When You Need It)

```bash
# Run all tests with verbose output
pytest -v

# Run only EXP-06 tests
pytest tests/test_exp06_*.py -v

# Run with coverage report
pytest --cov=seed --cov-report=html

# Run specific test file
pytest tests/test_exp06_entanglement_math.py -v

# Run test and show print statements
pytest -v -s tests/test_exp06_entanglement_math.py

# Run tests in parallel (if xdist installed)
pytest -n auto
```

---

## Next Steps

1. **Restart Rider** (or reload project)
2. Open **View → Tool Windows → Unit Tests**
3. Watch tests appear in the tree
4. Click green play button next to any test → **Run**
5. See results in the test panel

That's it. No more manual pytest commands needed for basic test running.

---

## Architecture Decision

This setup follows pytest best practices:
- **Centralized configuration** (pytest.ini + pyproject.toml)
- **Shared fixtures** (conftest.py in tests/)
- **Auto-discovery** (test_*.py naming convention)
- **IDE-native workflow** (no custom runners needed for basic use)
- **Backward compatible** (old manual pytest commands still work)

The trade-off: You need pytest, but that's a one-time `pip install pytest` and then everything works.
