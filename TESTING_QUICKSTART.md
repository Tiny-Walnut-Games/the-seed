# Testing Quick Start Guide

## 🚀 Fastest Way to Get Started

### 1. Run All Tests (3 commands)
```bash
# Run unit tests only (FAST - 1 min)
pytest -m "unit" -v

# Run integration tests (MEDIUM - 5 min)
pytest -m "integration" -v

# Run E2E tests (SLOW - requires STAT7 server running)
pytest -m "e2e" -v

# Run everything
pytest -v
```

### 2. Test Admin UI (2 steps)
```bash
# Start mock API server
cd web
python server/admin_api_server.py

# Open in browser
# http://localhost:8000/admin-entity-viewer.html
```

### 3. Verify Test Quality (2 commands)
```bash
# Check test markers are applied
python assign_test_markers.py

# Verify E2E tests have no mocks
python audit_e2e_mocks.py
```

---

## 📊 Test Markers Explained

### 🔲 Unit Tests (`@pytest.mark.unit`)
- **What**: Basic functionality, mocks allowed
- **Speed**: ⚡ Very fast (1-5 seconds each)
- **Count**: 12 tests
- **Run**: `pytest -m "unit" -v`
- **Example**: Testing governance policy creation with mock objects

### 🔗 Integration Tests (`@pytest.mark.integration`)
- **What**: Cross-module tests, mixed real and mock
- **Speed**: 🐢 Medium (5-30 seconds each)
- **Count**: 402 tests
- **Run**: `pytest -m "integration" -v`
- **Example**: Event store + tick engine interaction

### 🚀 E2E Tests (`@pytest.mark.e2e`)
- **What**: Full system tests, real connections, NO MOCKS
- **Speed**: 🐌 Slow (30+ seconds each)
- **Count**: 107 tests
- **Run**: `pytest -m "e2e" -v`
- **Requirement**: STAT7 server running on localhost:8000 and WebSocket on 8765
- **Example**: Playwright browser automation testing visualization

---

## 🛠️ Utility Scripts

### Test Marker Assignment
```bash
python assign_test_markers.py
```
**What it does:**
- Scans all 561 tests
- Analyzes mock vs real connection usage
- Recommends classification (unit/integration/e2e)
- Shows summary statistics

**Output:**
```
TOTAL TESTS: 476
  Unit Tests:        11 (2%)
  Integration Tests: 339 (71%)
  E2E Tests:        126 (26%)
```

### Apply Test Markers
```bash
# Dry-run (view changes)
python apply_test_markers.py

# Apply changes
python apply_test_markers.py --apply
```
**What it does:**
- Adds @pytest.mark.{unit|integration|e2e} to all test files
- Dry-run first to verify
- Already applied (521 markers added to 47 files)

### E2E Mock Auditor
```bash
python audit_e2e_mocks.py
```
**What it does:**
- Verifies E2E tests don't use Mock objects
- Scans for mock imports and constructors
- Ensures test quality standards

**Good output:**
```
✅ NO VIOLATIONS FOUND
All @pytest.mark.e2e tests are mock-free!
```

---

## 🎮 Admin Entity Viewer

### Quick Start
```bash
# Terminal 1: Start API server
cd web
python server/admin_api_server.py

# Terminal 2: Open browser
open http://localhost:8000/admin-entity-viewer.html
```

### Features
- **Search**: Find entities by name or ID
- **Filter**: By entity type (player, npc, object, environment)
- **Realms**: Select realm (alpha, void, shadow)
- **Real-time**: Updates every 3 seconds via WebSocket
- **Details**: View entity data (position, health, actions, etc.)
- **Stats**: Entity count by type

### What You'll See
- 10-12 simulated entities
- Real-time position updates
- Health/mana changes
- Player actions (walk, cast_spell, etc.)
- System log with connection status

---

## 🧪 Running Tests Locally

### Prerequisites
```bash
# Install Pytest and dependencies
pip install pytest pytest-asyncio pytest-timeout playwright
pytest install chromium  # For E2E tests
```

### Unit Tests (Always Works)
```bash
pytest tests/ -m "unit" -v
```
✅ No infrastructure needed  
✅ Should pass instantly  
✅ Use for quick feedback  

### Integration Tests (Always Works)
```bash
pytest tests/ -m "integration" -v
```
✅ No external servers needed  
✅ Tests cross-module interactions  
✅ Most of your tests  

### E2E Tests (Requires STAT7 Server)
```bash
# Start STAT7 server first (in another terminal)
python start_stat7.py

# Then run E2E tests
pytest tests/ -m "e2e" -v
```
⚠️ Requires STAT7 running  
⚠️ Requires WebSocket on port 8765  
⚠️ Takes 20-40 minutes to run all  

---

## 🔍 Test Organization

### By Category
```bash
# All tests
pytest tests/ -v

# Only quick tests
pytest tests/ -m "unit or integration" -v  # Skip slow E2E

# Only slow tests
pytest tests/ -m "e2e" -v

# Specific file
pytest tests/test_event_store.py -v

# Specific test
pytest tests/test_event_store.py::TestEventStoreAppend::test_append_event_records_immutably -v
```

### By Performance
```bash
# Show slowest 10 tests
pytest tests/ --durations=10

# Run with timeout (5 min per test)
pytest tests/ --timeout=300
```

---

## 📈 Test Coverage Map

```
The Seed Core (tests/)
├── test_event_store.py (16 tests)
│   └── @pytest.mark.integration
│
├── test_tick_engine.py (22 tests)
│   └── @pytest.mark.integration
│
├── test_governance_integration.py (19 tests)
│   └── @pytest.mark.e2e
│
├── test_stat7_e2e.py (12 tests)
│   └── @pytest.mark.e2e
│
├── test_stat7_e2e_optimized.py (11 tests)
│   └── @pytest.mark.e2e
│
└── ... + 12 more files

WARBLER (packages/.../tests/)
├── test_recovery_gate_phase1.py (23 tests)
│   └── @pytest.mark.integration
│
├── test_wfc_firewall.py (28 tests)
│   └── @pytest.mark.integration
│
├── test_wfc_integration.py (20 tests)
│   └── @pytest.mark.integration
│
└── ... + 32 more files

TOTAL: 521 markers applied across 47 files
```

---

## 🚦 Test Status Dashboard

Check current status:

```bash
# Count tests by marker
pytest tests/ --collect-only -q | grep "mark" | sort | uniq -c

# Show all tests
pytest tests/ --collect-only

# Show test tree
pytest tests/ --collect-only -q
```

---

## 🐛 Debugging Failing Tests

### Get More Details
```bash
# Very verbose output
pytest tests/test_file.py -vv

# Show print statements
pytest tests/test_file.py -v -s

# Stop on first failure
pytest tests/test_file.py -x

# Show local variables on failure
pytest tests/test_file.py -l

# Full traceback
pytest tests/test_file.py --tb=long
```

### Common Issues

**"ImportError: cannot import name X"**
```bash
# Install missing dependencies
pip install -r requirements-gpu.txt
pip install -e .
```

**"Connection refused" on E2E tests**
```bash
# Make sure STAT7 server is running
python start_stat7.py

# Check if ports are in use
netstat -an | grep 8000  # Web server
netstat -an | grep 8765  # WebSocket
```

**"Playwright not installed"**
```bash
pip install playwright
playwright install chromium
```

---

## 📊 CI/CD Pipeline (GitHub Actions)

### View Status
1. Go to repo
2. Click "Actions" tab
3. Select "Test Suite - Release Validation"
4. View latest run

### Test Tiers (Automatic on Push)

```
On: push to main/develop

Jobs:
├── Unit Tests (5 min)
│   └── Runs: pytest -m "unit"
│   └── Fails if any test fails
│
├── Integration Tests (10 min)
│   └── Runs: pytest -m "integration"
│   └── Fails if any test fails
│
├── E2E Tests (30 min)
│   └── Starts STAT7 in Docker
│   └── Runs: pytest -m "e2e"
│   └── Fails if any test fails
│
└── Test Summary
    └── Collects all results
    └── Fails if any tier fails
```

### View Results
- Unit test results: Artifacts → unit-test-results
- Integration results: Artifacts → integration-test-results
- E2E results: Artifacts → e2e-test-results

---

## ✅ Pre-Release Checklist

Before alpha release (v0.1.0):

```
Testing Infrastructure:
  [✅] All 521 tests marked with @pytest.mark
  [✅] 0 E2E mock violations
  [✅] Unit/integration/e2e tiers separated
  [✅] Run pytest -m "unit" - passes
  [✅] Run pytest -m "integration" - passes
  [ ] Run pytest -m "e2e" - passes (requires real server)

Admin UI:
  [✅] web/admin-entity-viewer.html built
  [✅] admin_api_server.py running
  [✅] Can view simulated entities
  [✅] Real-time updates working
  [ ] Connected to real STAT7 server
  [ ] Privacy filters working
  [ ] Audit logging working

CI/CD:
  [✅] GitHub Actions workflow created
  [✅] Three test tiers defined
  [ ] Workflow passing all tests
  [ ] Docker image for STAT7 ready
  [ ] Release candidate created

Documentation:
  [✅] Testing guide written
  [✅] Admin tools documented
  [✅] Known limitations listed
  [✅] Repository config updated
```

---

## 📞 Getting Help

**Quick checks:**
```bash
# List all test markers
pytest --markers

# Show test configuration
pytest --version
pytest --co -q

# Validate pytest.ini
cat pytest.ini
```

**If tests fail:**
1. Run single test file: `pytest tests/test_event_store.py -vv`
2. Check imports: `python -c "from event_store import EventStore"`
3. Run marker assignment: `python assign_test_markers.py`
4. Check audit: `python audit_e2e_mocks.py`

---

## 🎯 Next Steps

1. **Verify locally**: Run unit + integration tests
2. **Test admin UI**: Start mock server, view entities
3. **Review quality**: Run audit scripts
4. **Check CI/CD**: Push to develop branch, watch actions
5. **Connect real**: Hook up to real STAT7 server
6. **Release**: Create alpha v0.1.0 tag

---

*Last Updated: 2025-10-30*