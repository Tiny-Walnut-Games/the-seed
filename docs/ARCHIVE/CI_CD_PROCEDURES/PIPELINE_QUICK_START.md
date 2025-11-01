# ⚡ Pipeline Quick Start Guide

## TL;DR - Your New Testing Reality

You now have **comprehensive test discovery** running automatically. No more mocks hiding problems.

```bash
# Before: Only 1 test file running (with mocks) ❌
# After:  46+ tests across ALL modules ✅
```

---

## 🚀 30-Second Setup

### 1. Verify Everything Works (Local)

```bash
# Run verification
python scripts/verify_ci_pipeline.py

# Should say: ✅ PIPELINE VERIFICATION PASSED
```

### 2. View All Tests (Local)

```bash
# Show summary
python scripts/inventory_all_tests.py

# Should show: ✅ Discovered 46+ total tests
```

### 3. Run All Tests Locally

```bash
# Quick unit tests (5 min)
pytest tests/ -k "not slow" -n auto

# All tests including integration (20 min)
pytest tests/ packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/ -v

# Specific experiment
pytest -m exp06 packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/
```

---

## 🔄 What Happens Automatically

### On Every Push to main/develop

```
┌─ Test Discovery (1 min)
│  └─ Finds ALL 46+ tests
│
├─ Unit Tests (5 min, parallel)
├─ Integration Tests (10 min)
├─ Experiments EXP-01-10 (15 min, parallel)
├─ Load Tests (30 min)
│
└─ Aggregation (2 min)
   └─ Comments on PR with results
   └─ Creates summary report
```

**Total time**: ~30 minutes (running in parallel, not sequentially)

### On Pull Requests

You'll get a PR comment like:

```
## 📊 Test Results Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 46 |
| **✅ Passed** | 46 |
| **❌ Failed** | 0 |
| **Success Rate** | 100% |

### 🔍 Suite Breakdown
- **Unit Tests**: 20/20 passed
- **Integration Tests**: 15/15 passed
- **Experiment Tests**: 9/10 passed
- **Load Tests**: 1/1 passed
```

---

## 🎯 Triggering Workflows Manually

### Full Comprehensive Suite
1. Go to **GitHub → Actions → Comprehensive Test Suite**
2. Click **Run workflow**
3. Select option:
   - `all` - Everything (~30 min)
   - `unit` - Fast tests only (~5 min)
   - `quick` - Smoke tests (~5 min)

### MMO Load Testing (Existing)
1. Go to **GitHub → Actions → MMO Load Test**
2. Click **Run workflow**
3. Select:
   - `player_count`: 100, 250, 500, 1000, 2500, 5000
   - `stress_patterns`: standard, message-flood, connection-spikes

---

## 🔍 Understanding Test Categories

### Unit Tests (5 min)
- Fast, isolated tests
- Run in parallel
- Examples: `test_simple.py`, `test_api_contract.py`

```bash
pytest tests/ -k "not slow" -n auto
```

### Integration Tests (10 min)
- Cross-module tests
- Examples: `test_stat7_e2e.py`, `test_complete_system.py`

```bash
pytest tests/ -k "e2e or integration or server"
```

### Experiment Tests (15 min per experiment)
- EXP-01: Address Uniqueness
- EXP-02: Retrieval Efficiency
- ... through EXP-10
- Location: `packages/com.twg.the-seed/The Living Dev Agent/tests/`

```bash
pytest -m exp06  # Run specific experiment
```

### Load Tests (30 min)
- WebSocket stress testing
- Multiple player counts and patterns
- Example: `test_websocket_load_stress.py`

```bash
pytest tests/test_websocket_load_stress.py --capture=no -v
```

---

## 🐛 Quick Troubleshooting

### Q: Tests not found locally?

```bash
python scripts/inventory_all_tests.py --validate
```

### Q: Missing dependencies?

```bash
pip install pytest pytest-cov pytest-xdist pytest-asyncio
```

### Q: Need to fix pytest config?

```bash
python scripts/inventory_all_tests.py --fix
```

### Q: Want detailed test list?

```bash
python scripts/inventory_all_tests.py --full
```

### Q: Export as JSON?

```bash
python scripts/inventory_all_tests.py --json > tests.json
```

---

## 📊 Accessing Results

### After Workflow Completes

1. **GitHub → Actions → [Workflow Name]**
2. **Click latest run**
3. **Download artifacts**:
   - `unit-test-results/` - Unit test JUnit + coverage
   - `integration-test-results/` - Integration test results
   - `experiment-test-results-exp01/` through `/exp10/` - Each experiment
   - `load-test-results/` - Load test results
   - `test-aggregation-report/` - Final summary (JSON)

### Coverage Reports

After download, open:
```
unit-test-results/coverage-unit-html/index.html
```

### Test Results (JUnit XML)

Open in your IDE:
```
unit-test-results/unit-tests.xml
integration-test-results/integration-tests.xml
```

---

## 📈 Key Metrics to Watch

| Metric | Target | Status |
|--------|--------|--------|
| **Test Coverage** | >80% | Check HTML reports |
| **Pass Rate** | 100% | PR comments |
| **Pipeline Duration** | <30 min | GitHub Actions |
| **Mock Detection** | 0 | Review test code |

---

## 🔒 Security Notes

✅ All tests run on **GitHub's infrastructure** (not your machine)
✅ **No credentials exposed** (use secrets properly)
✅ **Results are public** (build-time metrics only)
✅ **Reproducible** (anyone can run the same tests)

---

## 🚨 Common Issues & Fixes

### Issue: "Test discovery finds 0 tests"

```bash
# Check pytest paths
cat pytest.ini | grep testpaths

# Should show:
# testpaths = 
#     tests
#     packages/com.twg.the-seed/The Living Dev Agent/tests
```

**Fix:**
```bash
python scripts/inventory_all_tests.py --fix
```

---

### Issue: "Tests work locally but fail in CI"

Check environment:
```bash
# Version mismatch?
python --version  # Should be 3.11+

# Missing deps?
pip install pytest pytest-asyncio websockets

# Run with CI flags
pytest tests/ --junitxml=results.xml --cov=seed
```

---

### Issue: "Mocks are still running"

Search for mock patterns:
```bash
grep -r "@patch\|@mock\|Mock()" tests/
grep -r "return Mock" tests/
```

**Fix**: Replace with real implementations:
```python
# ❌ Before
def test_something(self):
    mock_stat7 = Mock()
    assert mock_stat7.connected

# ✅ After
def test_something(self):
    real_stat7 = STAT7EventStreamer()
    assert real_stat7.connected
```

---

### Issue: "CI pipeline timeout"

Pipeline should complete in ~30 minutes. If timing out:

1. **Reduce scope in workflow dispatch**
   - Run `unit` tests only (~5 min)
   - Or `quick` (~5 min)

2. **Check for slow tests**
   ```bash
   pytest --durations=10  # Show 10 slowest
   ```

3. **Use larger runner** (if available)
   ```yaml
   runs-on: ubuntu-latest-x64
   ```

---

## ✅ Verification Checklist

- [ ] Run `python scripts/verify_ci_pipeline.py` locally
- [ ] See "✅ PIPELINE VERIFICATION PASSED"
- [ ] Run `python scripts/inventory_all_tests.py` and confirm 46+ tests
- [ ] Make a test PR and see workflow run
- [ ] Check PR comment has test results
- [ ] Download artifacts and verify coverage HTML
- [ ] All checks passing? You're ready! 🎉

---

## 📚 Additional Resources

- [PIPELINE_STRATEGY.md](.github/PIPELINE_STRATEGY.md) - Comprehensive architecture guide
- [DELIVERY_CHECKLIST.md](.github/DELIVERY_CHECKLIST.md) - Soft-cap testing details
- [pytest.ini](../pytest.ini) - Test configuration

---

## 🎯 Next Steps

1. **Local verification**:
   ```bash
   python scripts/verify_ci_pipeline.py
   ```

2. **View all tests**:
   ```bash
   python scripts/inventory_all_tests.py
   ```

3. **Run tests locally** (pick one):
   ```bash
   pytest tests/ -k "not slow" -n auto        # Unit tests
   pytest tests/ -k "e2e or integration"      # Integration tests
   pytest -m exp06                             # Experiment
   pytest tests/test_websocket_load_stress.py # Load tests
   ```

4. **Push to GitHub** and watch the workflow!

---

**Status**: ✅ **Your pipeline is now comprehensive and mock-free!**

46+ real tests validating your entire system on every push.