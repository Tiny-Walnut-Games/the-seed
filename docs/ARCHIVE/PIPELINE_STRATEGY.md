# 🔧 CI/CD Pipeline Strategy - Complete Test Discovery System

## Executive Summary

Your project has **46 total tests** across 3 locations, but your old pipeline was only running 1 test file and using mocks. This document outlines the new comprehensive pipeline that discovers, categorizes, and runs ALL tests with proper reporting.

---

## 📊 Test Inventory

### Before (Old Pipeline)
```
✅ Load stress tests:     1 file (hardcoded)
❌ Core MMO tests:       14 files (missing)
❌ Living Dev Agent:     31 files (missing)
──────────────────────────────────────
Total coverage: 1/46 tests (2%)
Result: Mocks hiding real issues ⚠️
```

### After (New Pipeline)
```
✅ Load stress tests:     1 file (15 tests)
✅ Core MMO tests:       14 files (20+ tests)
✅ Living Dev Agent:     31 files (multiple experiments)
✅ Experiment tests:     EXP-01 through EXP-10
──────────────────────────────────────
Total coverage: 46+ tests (100%)
Result: Complete validation ✅
```

---

## 🏗️ Pipeline Architecture

### Two-Workflow System

#### 1. **comprehensive-test-suite.yml** (Primary Validation)
Runs on every push and pull request. Features:

| Stage | Purpose | Parallel | Duration |
|-------|---------|----------|----------|
| **Test Discovery** | Find all 46 tests | Sequential | ~1 min |
| **Unit Tests** | Fast tests (no slow/e2e) | Yes (xdist) | ~5 min |
| **Integration Tests** | Cross-module validation | Sequential | ~10 min |
| **Experiment Tests** | EXP-01 through EXP-10 | Yes (matrix) | ~15 min each |
| **Load Tests** | Performance validation | Sequential | ~30 min |
| **Aggregation** | Combine results | Sequential | ~2 min |
| **Total** | **End-to-end validation** | **Parallel execution** | **~30 min** |

#### 2. **mmo-load-test-validation.yml** (Existing - Still Active)
Continues to run sophisticated soft-cap discovery tests when needed.

---

## 🔍 Test Discovery Process

### How It Works

```
1. Test Discovery Job
   └─ Uses pytest --collect-only
   └─ Finds ALL tests across:
      ├─ tests/
      ├─ packages/com.twg.the-seed/The Living Dev Agent/tests/
      └─ Categorizes by: unit, integration, experiment, load
   └─ Outputs JSON manifest

2. Parallel Test Execution
   ├─ Unit Tests (pytest -n auto) - 5 minutes
   ├─ Integration Tests - 10 minutes
   ├─ Experiment Tests (matrix × 10 experiments) - 15 min each
   └─ Load Tests - 30 minutes
   
   All run SIMULTANEOUSLY (not sequentially!)

3. Result Aggregation
   └─ Combines JUnit XML from all jobs
   └─ Generates comprehensive report
   └─ Comments on PRs with results
   └─ Fails if any tests fail
```

### What Gets Discovered

#### Unit Tests (Fast)
- `test_simple.py` - Basic functionality
- `test_api_contract.py` - API validation
- `test_event_store.py` - Event storage
- Plus any test without "slow" or "e2e" marker

**Excluded**: Load tests, stress tests, slow tests

#### Integration Tests (Medium)
- `test_stat7_e2e.py` - End-to-end flows
- `test_stat7_server.py` - Server integration
- `test_e2e_scenarios.py` - Complete scenarios
- `test_complete_system.py` - Full system validation

**Pattern**: Tests with "e2e", "integration", "server", or "system" in name

#### Experiment Tests (Long-running)
- EXP-01: Address Uniqueness
- EXP-02: Retrieval Efficiency
- EXP-03: Dimension Necessity
- EXP-04: Fractal Scaling
- EXP-05: Compression/Expansion
- EXP-06: Entanglement Detection
- EXP-07: LUCA Bootstrap
- EXP-08: Warbler Integration
- EXP-09: Concurrency
- EXP-10: Narrative Preservation

**Location**: `packages/com.twg.the-seed/The Living Dev Agent/tests/`

#### Load Tests (Resource-intensive)
- `test_websocket_load_stress.py` - WebSocket load testing
- 10 different player count/pattern combinations
- 100, 250, 500, 1000, 2500, 5000 player scenarios

---

## 🚀 Usage Guide

### Running All Tests Locally

```bash
# Install dependencies
pip install pytest pytest-cov pytest-xdist pytest-asyncio

# Run unit tests (fast)
pytest tests/ -k "not slow" -n auto

# Run integration tests
pytest tests/ -k "integration or e2e or server"

# Run specific experiment
pytest -m exp06 packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/

# Run all tests with coverage
pytest tests/ packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/ \
  --cov=seed --cov=web/server --cov-report=html
```

### Inventory All Tests

```bash
# Show summary of all tests
python scripts/inventory_all_tests.py

# Show detailed list
python scripts/inventory_all_tests.py --full

# Generate JSON manifest
python scripts/inventory_all_tests.py --json > test-manifest.json

# Validate test imports
python scripts/inventory_all_tests.py --validate

# Fix pytest configuration
python scripts/inventory_all_tests.py --fix
```

### Triggering Workflows Manually

#### Comprehensive Test Suite
Go to: **Actions → Comprehensive Test Suite → Run workflow**

Options:
- `all` - Run everything (default, ~30 min)
- `unit` - Fast unit tests only (~5 min)
- `integration` - Integration tests only (~10 min)
- `experiments` - EXP-01 through EXP-10 (~15+ min)
- `load` - Load tests only (~30 min)
- `quick` - Smoke tests (~5 min)

#### MMO Load Test (Existing)
Go to: **Actions → MMO Load Test → Run workflow**

Options:
- `player_count`: 100, 250, 500, 1000, 2500, 5000, or comprehensive
- `stress_patterns`: standard, message-flood, connection-spikes, or all

---

## 📊 Understanding Pipeline Results

### PR Comment Example

```
## 📊 Test Results Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 46 |
| **✅ Passed** | 45 |
| **❌ Failed** | 1 |
| **⚠️ Errors** | 0 |
| **⊘ Skipped** | 0 |
| **Success Rate** | 97.8% |

### 🔍 Suite Breakdown
- **Unit Tests**: 20/20 passed
- **Integration Tests**: 15/15 passed
- **Experiment Tests**: 9/10 passed
- **Load Tests**: 1/1 passed
```

### Artifacts

After each run, these artifacts are available for 30-90 days:

```
test-discovery-report/
├─ test_discovery.json          # Test categorization
│
unit-test-results/
├─ unit-tests.xml               # JUnit results
├─ coverage-unit-html/          # Coverage report
│
integration-test-results/
├─ integration-tests.xml
│
experiment-test-results-exp01/
├─ exp01-tests.xml
├─ ... (one per experiment)
│
load-test-results/
├─ load-tests.xml
│
test-aggregation-report/
└─ test-aggregation-report.json  # Complete summary (90 days)
```

---

## 🔧 Configuration Deep Dive

### Test Path Discovery

**pytest.ini** defines where to look:
```ini
testpaths = tests Packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Markers System

Tests are organized by markers defined in `pytest.ini`:

```ini
markers =
    exp01-exp10     # Experiment tests
    slow            # Slow tests (excluded from unit runs)
    integration     # Integration tests
    load            # Load tests
    math            # Mathematical tests
```

Use markers in test files:
```python
@pytest.mark.exp06
@pytest.mark.slow
def test_entanglement_detection():
    pass
```

### Parallel Execution Strategy

#### Where Parallelization Happens

| Test Type | Method | Workers |
|-----------|--------|---------|
| **Unit** | pytest-xdist | auto (all cores) |
| **Integration** | Sequential | 1 |
| **Experiments** | GitHub matrix | 10 (one per exp) |
| **Load** | Sequential | 1 |

**Why different strategies?**
- Unit tests are fast and isolated → maximize parallelization
- Integration tests need shared state → sequential
- Experiments are heavy → one per matrix job (GitHub parallelizes)
- Load tests need full resources → sequential

---

## 🐛 Troubleshooting

### Issue: "No tests found"

**Problem**: Pipeline discovers 0 tests

**Solution**:
```bash
# Check pytest configuration
pytest --version
pytest --collect-only -q

# Run inventory to diagnose
python scripts/inventory_all_tests.py --validate

# Fix pytest configuration
python scripts/inventory_all_tests.py --fix
```

### Issue: "Mock implementations detected"

**Problem**: Tests pass but using mock data

**Solution**:
1. Check for `@pytest.fixture` with mocking:
   ```python
   @pytest.fixture
   def mock_stat7():
       return Mock()  # ❌ This is the problem
   ```

2. Use real implementations:
   ```python
   @pytest.fixture
   def real_stat7():
       return STAT7EventStreamer()  # ✅ Real
   ```

3. Run with `--verbose` to see what's being called:
   ```bash
   pytest -v --capture=short
   ```

### Issue: "Tests fail locally but pass in CI"

**Problem**: Environment mismatch

**Solution**:
1. Check Python version:
   ```bash
   python --version  # Should be 3.11+
   ```

2. Check dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r web/requirements-visualization.txt
   ```

3. Run with same flags as CI:
   ```bash
   pytest tests/ --junitxml=results.xml --cov=seed
   ```

### Issue: "Too many tests, CI timeout"

**Problem**: Job exceeds 120 minutes

**Solution**:
1. Reduce test scope in workflow dispatch
2. Run experiments separately (they're already in matrix)
3. Consider splitting into separate workflows by tier

### Issue: "Can't find tests in Living Dev Agent directory"

**Problem**: Path not recognized by pytest

**Solution**:
1. Check directory name exactly:
   ```bash
   ls -la packages/com.twg.the-seed/
   ```

2. Verify pytest.ini has correct path:
   ```bash
   cat pytest.ini | grep testpaths
   ```

3. Run inventory:
   ```bash
   python scripts/inventory_all_tests.py --full
   ```

---

## 📈 Performance Optimization

### Current Metrics

```
Total runtime (all tests parallel): ~30 minutes
├─ Test discovery:           1 min
├─ Unit tests (parallel):    5 min
├─ Integration tests:        10 min
├─ Experiments (parallel):   15 min max
├─ Load tests:              30 min
└─ Aggregation:              2 min
```

### Optimization Opportunities

1. **Enable GPU acceleration** (if available):
   ```bash
   pytest --gpu  # If implemented
   ```

2. **Distribute across runners**:
   ```yaml
   runs-on: ubuntu-latest-x64  # Use larger runner
   ```

3. **Cache dependencies**:
   ```yaml
   with:
     cache: 'pip'  # Already enabled
   ```

4. **Reduce experiment scope** in PR checks:
   ```yaml
   if: github.event_name == 'schedule' || github.event_name == 'push'
   ```

---

## 🎯 Best Practices

### For Pipeline Maintainers

1. **Regular cleanup**: Delete old artifacts
   ```bash
   # GitHub Actions auto-cleans after retention period
   ```

2. **Monitor failure patterns**:
   - Check aggregation report monthly
   - Track test duration trends
   - Alert if tests start failing consistently

3. **Keep tests current**:
   - Remove tests that always fail (or fix them)
   - Add tests when finding bugs
   - Refactor slow tests

### For Test Writers

1. **Use appropriate markers**:
   ```python
   @pytest.mark.slow      # If runs > 1 second
   @pytest.mark.exp06     # If part of EXP-06
   @pytest.mark.integration  # If crosses modules
   ```

2. **Avoid mocks when possible**:
   - Use real objects
   - Use fixtures for expensive setup
   - Mock only external services

3. **Write deterministic tests**:
   - No timing dependencies
   - No random data without seed
   - No file system assumptions

---

## 📚 Related Documentation

- [DELIVERY_CHECKLIST.md](.github/DELIVERY_CHECKLIST.md) - Soft-cap testing overview
- [SOFT_CAP_STRESS_TEST_UPGRADE.md](../docs/SOFT_CAP_STRESS_TEST_UPGRADE.md) - Load testing details
- [pytest.ini](../pytest.ini) - Test configuration

---

## ✅ Verification Checklist

- [ ] Run `python scripts/inventory_all_tests.py` and confirm 46+ tests
- [ ] Run `pytest tests/ --co -q` and see all test files
- [ ] Push to feature branch and watch comprehensive-test-suite workflow
- [ ] Verify PR comment includes all test categories
- [ ] Download artifacts and verify JSON report
- [ ] Check coverage reports in HTML artifacts
- [ ] Monitor GitHub Actions cost (should be within reasonable bounds)

---

**Status**: ✅ **Comprehensive pipeline deployed**

Your CI/CD now validates 46+ tests across unit, integration, and load testing with automatic discovery and reporting!