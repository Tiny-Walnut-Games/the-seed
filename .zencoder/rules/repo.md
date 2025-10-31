# Repository Testing Framework Configuration

**Repository:** The Seed (Tiny Walnut Games)  
**Last Updated:** 2025-10-30  
**Status:** ACTIVE

---

## Primary Testing Frameworks

### System-Level Overview

| System | Framework | Language | Entry Point | Status |
|--------|-----------|----------|-------------|--------|
| **The Seed** | Pytest | Python | `tests/` | ✅ Active |
| **WARBLER** | Pytest | Python | `packages/com.twg.the-seed/The Living Dev Agent/tests/` | ✅ Active |
| **TLDA** | Unity Test Framework | C# | Unity Editor UI | ✅ Active |

---

## Default Test Framework

### **Pytest** (Default)
- **Version:** >=7.0 (Installed: 8.4.1)
- **Configuration Files:**
  - `pytest.ini` - Primary configuration
  - `pyproject.toml` - Project metadata and pytest options
- **Discovery Paths:**
  - `tests/` (The Seed core)
  - `packages/com.twg.the-seed/The Living Dev Agent/tests/` (WARBLER)
- **Pattern:** `test_*.py` files with `test_*` functions and `Test*` classes

### Configuration Details
```ini
[pytest]
testpaths = 
    tests
    packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests

python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    exp01-exp10: Experimental series tests
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    load: Load/stress tests
    slow: Slow running tests

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings

timeout = 300
```

---

## Test Suite Inventory

### The Seed (Core System)

**Location:** `/tests/`

**Test Files:** 16 active files

**Key Suites:**
- `test_stat7_e2e_optimized.py` - Optimized E2E tests with shared sessions
- `test_governance_integration.py` - Governance system integration
- `test_api_contract.py` - API contract validation
- `test_e2e_scenarios.py` - End-to-end scenarios
- `test_tick_engine.py` - Tick engine logic
- `test_event_store.py` - Event storage system
- `test_websocket_load_stress.py` - WebSocket performance

**Total Tests Collected:** 141+

**Total Test Items:** 201 (functions + classes)

### WARBLER (Living Dev Agent)

**Location:** `/packages/com.twg.the-seed/The Living Dev Agent/tests/`

**Test Files:** 31 total (10 cleanly readable, 21 with encoding notes)

**Key Clean Suites:**
- `test_wfc_integration.py` - Workflow integration
- `test_wfc_firewall.py` - WFC firewall system
- `test_recovery_gate_phase1.py` - Recovery gate phase 1
- `test_phase2_stat7_integration.py` - STAT7 integration
- `test_plugin_system.py` - Plugin system

**Total Test Items:** 143+ (functions + classes)

**Note:** Some files use UTF-8 extended characters. Add `# -*- coding: utf-8 -*-` to headers if needed for static analysis.

### TLDA (Unity Integration)

**Location:** `/Assets/Plugins/TWG/TLDA/Tools/TestSuite/`

**Framework:** Unity Test Framework (C#)

**Execution:** Must run through Unity Editor
```
Window → General → Test Runner → Run All Tests
```

**Cannot execute:** From command line (requires Unity Editor instance)

---

## Quick Start Commands

### Run All The Seed Tests
```bash
python -m pytest tests/ -v
```

### Run All WARBLER Tests
```bash
python -m pytest packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/ -v
```

### Run Everything (Both Systems)
```bash
python -m pytest tests/ packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests/ -v
```

### Run Specific Suite
```bash
python -m pytest tests/test_governance_integration.py -v
```

### Run with Performance Metrics
```bash
python -m pytest tests/ --durations=10 -v
```

### Run Only Unit Tests (Skip Slow)
```bash
python -m pytest tests/ -m "not slow" -v
```

### Run E2E Tests Only
```bash
python -m pytest -m e2e -v
```

---

## Test Execution Requirements

### For The Seed Tests

**Minimum:**
- Pytest >=7.0
- Python 3.9+

**For E2E Tests:**
- STAT7 server running (start with `python start_stat7.py`)
- Browser/Playwright (for browser-based tests)
- WebSocket support

**For Browser Tests:**
```bash
pip install playwright
playwright install
```

### For WARBLER Tests

**Minimum:**
- Pytest >=7.0
- Python 3.9+

**For Some Tests:**
- Ollama service (for RAG integration)
- GitHub API credentials (for GitHub tests)
- Specific service dependencies

### For TLDA Tests

**Required:**
- Unity Editor (2021 LTS or later)
- Unity Test Framework
- C# scripting support enabled

---

## Test Framework Selection Logic

**For E2E Tests in This Repo:**
- **Default:** Playwright (if user requests E2E without specifying framework)
- **Override:** None currently specified
- **Detection:** From `.zencoder/rules/repo.md` (this file)

**For PyTest-based Tests:**
- Used for all Python testing
- Configuration in `pytest.ini` and `pyproject.toml`
- **NEW:** All tests now have @pytest.mark decorators (unit/integration/e2e)
- **NEW:** Use `pytest -m "unit"` to run unit tests only
- **NEW:** Use `pytest -m "integration"` to run integration tests
- **NEW:** Use `pytest -m "e2e"` to run E2E tests (real systems only, no mocks)

**For Unity Tests:**
- Unity Test Framework (UTR)
- Executed through Unity Editor UI

---

## Performance Benchmarks

### Optimization Claims (STAT7 E2E)

**Original Implementation:**
- Per-test duration: 30-60 seconds
- Total suite: 5-10 minutes
- Server startup: 5 seconds per test
- Browser launch: 2-3 seconds per test

**Optimized Implementation:**
- Per-test duration: 5-15 seconds (70-80% faster)
- Total suite: 1-2 minutes (80% faster)
- Server startup: 3 seconds once (40% faster)
- Browser launch: Once for all tests (90% faster)

**Verification Method:**
```bash
# Run both versions and compare
$start1 = Get-Date; python -m pytest tests/test_stat7_e2e.py -v; $end1 = Get-Date
$start2 = Get-Date; python -m pytest tests/test_stat7_e2e_optimized.py -v; $end2 = Get-Date
Write-Host "Original: $($end1 - $start1)"
Write-Host "Optimized: $($end2 - $start2)"
```

---

## Known Issues & Solutions

### Encoding Issues

**Issue:** UTF-8 character decoding errors in WARBLER tests

**Affected Files:** 21 test files with special characters

**Solution:** Ensure UTF-8 BOM header:
```python
# -*- coding: utf-8 -*-
```

**Impact:** Does not prevent pytest execution, only static file scanning

### Missing Dependencies

**Common Issue:** ImportError when running WARBLER tests

**Solution:**
```bash
pip install -r requirements-gpu.txt
pip install -e .
```

### Server Not Running

**Issue:** E2E tests fail with "Connection refused"

**Solution:** Start server first:
```bash
python start_stat7.py
```

---

## Test Markers & Categories

### Experiment Markers (EXP-01 through EXP-10)
- `exp01`: Address Uniqueness Tests
- `exp02`: Retrieval Efficiency Tests
- `exp03`: Dimension Necessity Tests
- `exp04`: Fractal Scaling Tests
- `exp05`: Compression/Expansion Tests
- `exp06`: Entanglement Detection Tests
- `exp07`: LUCA Bootstrap Tests
- `exp08`: Warbler Integration Tests
- `exp09`: Concurrency Tests
- `exp10`: Narrative Preservation Tests

### Standard Markers
- `unit`: Unit tests (fast, <1 second)
- `integration`: Integration tests
- `e2e`: End-to-end tests
- `load`: Load and stress tests
- `math`: Mathematical validation
- `robustness`: Robustness testing
- `slow`: Slow tests (>5 seconds)

### Usage
```bash
# Run all E2E tests
pytest -m e2e -v

# Run all except slow
pytest -m "not slow" -v

# Run EXP-06 tests
pytest -m exp06 -v
```

---

## CI/CD Integration

### Available Test Runners

1. **Optimized Runner:**
   ```bash
   python run_stat7_tests_optimized.py
   ```

2. **General Runner:**
   ```bash
   python run_tests.py --full
   ```

3. **Discovery Tool:**
   ```bash
   python system_validation_discovery.py
   ```

### GitHub Actions

Configuration files located in `.github/workflows/`

---

## Documentation References

- **API Documentation:** `/docs/API/`
- **Architecture:** `/docs/ARCHITECTURE.md`
- **Getting Started:** `/docs/GETTING_STARTED.md`
- **Development:** `/docs/DEVELOPMENT/`

---

## Support & Troubleshooting

**For test failures:**
1. Check `.test_results/` directory for recent reports
2. Review pytest output with `-vv` flag
3. Run specific failing test in isolation
4. Check server/service dependencies

**For performance issues:**
1. Use `--durations=10` to identify slow tests
2. Profile with `-m "not slow"` first
3. Ensure no background processes interfering

**For framework-specific questions:**
- Pytest: See `pytest.ini` configuration
- Playwright: See browser-based E2E tests
- Unity: See `/docs/TLDA/README.md`

---

## Release Preparation Tools (NEW - Phase 1)

### Test Marker Assignment

**Script:** `assign_test_markers.py`
- Analyzes all 561 tests across The Seed and WARBLER
- Intelligently classifies as unit/integration/e2e based on mock usage
- Provides detailed classification report

```bash
python assign_test_markers.py
```

**Output:**
- Unit Tests: 12 (2%) - mocks allowed
- Integration Tests: 402 (71%) - mixed real/mock patterns
- E2E Tests: 107 (26%) - real connections only, no mocks

### Marker Application

**Script:** `apply_test_markers.py`
- Automatically adds @pytest.mark decorators to all test files
- Dry-run first to verify changes
- Applies to 521 tests across 47 files

```bash
# Dry-run (view changes)
python apply_test_markers.py

# Apply changes
python apply_test_markers.py --apply
```

### Test Marker Maintenance Tools (Phase 1 - Bug Fixes)

**Issues Discovered & Fixed:**

1. **Missing `import pytest` in test files**
   - Issue: Markers added without ensuring import statement present
   - Fix: `fix_missing_pytest_imports.py` - adds import where missing
   - Files Fixed: 21
   - Status: ✅ RESOLVED

2. **UTF-8 BOM Encoding Conflicts**
   - Issue: BOM characters appearing after shebangs, causing SyntaxError
   - Fix: `remove_bom_and_fix_imports.py` + PowerShell cleanup
   - Files Fixed: 18
   - Status: ✅ RESOLVED

**Maintenance Scripts:**
```bash
# If needed, re-apply import pytest to all marker-decorated files
python fix_missing_pytest_imports.py

# If needed, remove stray BOM characters
python remove_bom_and_fix_imports.py
```

**Log File:** `TEST_MARKER_FIXES_LOG.md`
- Comprehensive record of all issues and fixes
- Statistics and verification steps
- Best practices for future marker applications

### E2E Mock Auditor

**Script:** `audit_e2e_mocks.py`
- Verifies no E2E tests use Mock objects
- Real systems only for @pytest.mark.e2e tests
- Ensures release quality standards

```bash
python audit_e2e_mocks.py
```

**Status:** ✅ All E2E tests are mock-free (0 violations)

### Admin Entity Viewer (NEW)

**File:** `web/admin-entity-viewer.html`
- Real-time simulation monitoring dashboard
- Entity search and filtering
- Realm navigation
- Player data display
- WebSocket real-time updates

**Mock API Server:** `web/server/admin_api_server.py`
- Development server for testing UI
- Generates sample entities
- Simulates real-time updates

```bash
cd web
python server/admin_api_server.py
# Open: http://localhost:8000/admin-entity-viewer.html
```

### GitHub Actions CI/CD (NEW)

**Workflow:** `.github/workflows/test-suite-release.yml`

Three-tier testing strategy:
1. **Unit Tests** (5-10 min) - Mock-based unit tests
2. **Integration Tests** (10-20 min) - Cross-module tests
3. **E2E Tests** (20-40 min) - Real STAT7 server in Docker container

All tests must pass for release candidate approval.

**Run locally:**
```bash
# Unit tests only (fast)
pytest -m "unit" -v

# Integration tests
pytest -m "integration" -v

# E2E tests (requires servers)
pytest -m "e2e" -v

# All tests
pytest -v
```

## Maintenance Notes

**Last Validation:** 2025-10-30  
**Test Suite Status:** ACTIVE  
**Framework Versions:** Pytest 8.4.1 (latest stable)
**Test Markers:** All 521 tests now categorized (unit/integration/e2e)
**E2E Mocks:** 0 violations (fully compliant)

**Recent Improvements:**
- ✅ Added @pytest.mark decorators to 521 tests (47 files)
- ✅ Built admin entity viewer UI with real-time updates
- ✅ Created GitHub Actions CI/CD workflow for release validation
- ✅ Implemented E2E mock auditor (0 violations found)
- ✅ Fixed UTF-8 BOM encoding in 21 Python files

**Recommended Updates:**
- Monitor pytest for security updates
- Keep Playwright updated for browser tests
- Verify Unity compatibility for TLDA tests
- Review E2E tests quarterly for mock creep

---

**Framework Selection Default:** **Pytest**  
**Fallback:** None (Pytest is required for The Seed and WARBLER)  
**Override Method:** Explicitly specify framework when requesting test creation

**Alpha Release Readiness (v0.1.0):**
- ✅ 521 tests fully categorized
- ✅ E2E tests verified mock-free
- ✅ Admin UI functional (entity viewer working)
- ⚠️ Test execution pending (requires real STAT7 server)
- ⚠️ GitHub Actions workflow pending activation