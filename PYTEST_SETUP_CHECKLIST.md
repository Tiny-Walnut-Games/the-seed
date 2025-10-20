# Pytest IDE Integration - Setup Verification Checklist

**Date:** 2025-01-23  
**Status:** ✅ Complete - All files created

---

## Files Created

- [x] `pytest.ini` - Pytest configuration at project root
- [x] `pyproject.toml` - Python project metadata and tool config
- [x] `tests/conftest.py` - Pytest fixtures and sys.path setup
- [x] `PYTEST_SETUP_GUIDE.md` - Complete usage guide

---

## Why This Fixes the Problem

### Before
- ❌ No IDE test discovery
- ❌ Had to manually run `pytest` from terminal
- ❌ Tests scattered across multiple directories
- ❌ No way to click "Run Tests" in IDE menu
- ❌ Every conversation had to re-establish test context

### After
- ✅ Full IDE test discovery in JetBrains Rider
- ✅ Click Run → Run All Tests (or green play button)
- ✅ Tests organized by experiment in test panel
- ✅ Single source of truth for test configuration
- ✅ One-time setup, permanent integration

---

## Verification Steps

### Step 1: Verify Files Exist
```bash
# Check from project root
ls pytest.ini
ls pyproject.toml
ls tests/conftest.py
```

Expected: All three files exist ✅

### Step 2: Restart JetBrains Rider
- Close Rider completely
- Reopen the project
- This triggers IDE test discovery

### Step 3: Open Test Panel
- Go to **View** → **Tool Windows** → **Unit Tests**
- Wait a few seconds for discovery to complete

Expected: You should see:
```
tests/
├── test_exp06_entanglement_math
├── test_exp06_simple_validation
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

### Step 4: Run a Single Test
1. Right-click on `test_exp06_entanglement_math` in test panel
2. Select **Run**
3. Watch test execute in bottom panel

Expected: Test runs and shows results ✅

### Step 5: Run All STAT7 Tests
1. Right-click on `test_exp06_*` group
2. Select **Run**
3. Wait for all EXP-06 tests to complete

Expected: 25+ tests pass in ~5-30 seconds ✅

### Step 6: Use Command Palette (Optional)
- Press `Ctrl+Shift+A` (Windows)
- Type "Run All Tests"
- Press Enter

Expected: All tests in `tests/` directory run ✅

---

## Understanding pytest.ini

```ini
[pytest]
testpaths = tests              # Look ONLY in tests/ directory
python_files = test_*.py       # Find files named test_*.py
python_classes = Test*         # Find classes named Test*
python_functions = test_*      # Find functions named test_*
```

This tells pytest exactly where and what to look for. Our existing test files already follow these conventions, so discovery should be automatic.

---

## Understanding conftest.py

Key things it does:

```python
# 1. Add seed/engine to sys.path
sys.path.insert(0, str(SEED_ENGINE))

# 2. Provides fixtures that tests can use
@pytest.fixture
def test_data_dir(tmp_path):
    return tmp_path

# 3. Auto-marks tests based on filename
if "exp06" in item.nodeid:
    item.add_marker(pytest.mark.exp06)
```

This means:
- Tests can import from `seed/engine` without manual path manipulation
- Tests have access to temporary directories for test data
- Tests are automatically tagged by experiment type

---

## Understanding pyproject.toml

Provides:
- Project metadata (name, version, description)
- Python version requirement (3.9+)
- Dependencies (pytest, pydantic, numpy, pyyaml)
- Tool configuration (pytest markers, coverage, black, mypy)
- Optional dev dependencies for linting/formatting

---

## Now You Can

### From IDE:
1. **Run all tests** - Click Run menu → Run All Tests
2. **Run experiment tests** - Right-click on test_exp06_* → Run
3. **Debug test** - Click green arrow next to test name
4. **View results** - Results appear in test panel automatically
5. **Filter tests** - Use IDE search to find tests by name

### From Command Line (Still Works):
```bash
pytest                              # Run all
pytest tests/test_exp06_*.py        # Run EXP-06 only
pytest -v                           # Verbose
pytest -m exp06                     # By marker
pytest --cov=seed                   # With coverage
```

---

## Troubleshooting

### Tests Still Not Appearing
1. Make sure you restarted Rider AFTER creating these files
2. File → Invalidate Caches / Restart → Invalidate and Restart
3. Check pytest.ini is at: E:/Tiny_Walnut_Games/the-seed/pytest.ini

### Import Errors When Running Tests
- conftest.py handles sys.path setup, but if you see import errors:
  - Check that seed/engine files exist: `ls seed/engine/stat7_entity.py`
  - Run: `pip install pytest numpy pydantic pyyaml`

### Tests Fail With "ModuleNotFoundError"
- The conftest.py should handle this automatically
- If not: Check that you're running from IDE (not terminal in different directory)

---

## What's Next

The infrastructure is now complete. You can now:

1. **Continue development** - Add new tests, they'll be discovered automatically
2. **Run before commits** - Use "Run All Tests" in IDE before committing
3. **Debug failing tests** - Click on test → Debug with green arrow
4. **Track test results** - Test panel shows pass/fail visually

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Test Discovery | Manual pytest | Automatic in IDE |
| Running Tests | Terminal commands | Click Run menu |
| Debugging Tests | Manual pytest -vv | IDE debugger with breakpoints |
| Test Organization | Scattered across dirs | Visible in IDE test tree |
| Configuration | No central config | pytest.ini + pyproject.toml |
| sys.path Setup | Scattered per-file | Centralized in conftest.py |

**Result:** Professional, IDE-integrated testing that works out of the box. No more "I have to re-explain testing every conversation."
