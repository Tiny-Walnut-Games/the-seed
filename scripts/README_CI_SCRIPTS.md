# 🔧 CI/CD Pipeline Scripts

Quick reference for test discovery and pipeline verification scripts.

---

## 📋 Available Scripts

### 1. `inventory_all_tests.py` - Test Discovery

**Purpose**: Discover and categorize all tests in the codebase

**Usage**:
```bash
# Show summary
python scripts/inventory_all_tests.py

# Show detailed list
python scripts/inventory_all_tests.py --full

# Generate JSON manifest
python scripts/inventory_all_tests.py --json

# Validate test imports
python scripts/inventory_all_tests.py --validate

# Fix pytest configuration
python scripts/inventory_all_tests.py --fix
```

**Output**:
```
✅ Discovered 46+ total tests

📁 Unit Tests
   Count: 20
   📄 test_simple.py: 3 tests
   📄 test_api_contract.py: 5 tests
   ...

📁 Integration Tests
   Count: 15
   📄 test_stat7_e2e.py: 4 tests
   ...

📁 Experiment Tests
   Count: Multiple per category
   ...

📁 Load Tests
   Count: 10 configurations
   ...
```

**Features**:
- ✓ Automatic test discovery via pytest
- ✓ Intelligent categorization
- ✓ Import validation
- ✓ JSON export
- ✓ pytest configuration repair

**When to use**:
- Daily: Check test count (should stay 46+)
- Weekly: Review detailed list for new tests
- On error: Run `--validate` or `--fix`

---

### 2. `verify_ci_pipeline.py` - Pipeline Verification

**Purpose**: Validate that your CI/CD pipeline is properly configured

**Usage**:
```bash
# Full verification
python scripts/verify_ci_pipeline.py

# Quick check
python scripts/verify_ci_pipeline.py --quick

# Generate JSON report
python scripts/verify_ci_pipeline.py --json

# Auto-fix issues
python scripts/verify_ci_pipeline.py --fix
```

**Output**:
```
🔍 CI PIPELINE VERIFICATION

✅ Python Version... ✅ Python 3.11
✅ pytest Installation... ✅ pytest 7.4.0
✅ pytest Configuration... ✅ OK
✅ Test Paths Accessible... ✅ OK
✅ Test Discovery... ✅ 46 tests discovered
✅ GitHub Actions Workflows... ✅ OK
✅ Dependencies... ✅ All installed
✅ Test Markers... ✅ OK

✅ PIPELINE VERIFICATION PASSED
```

**Checks**:
- ✓ Python version (3.9+)
- ✓ pytest installation
- ✓ pytest.ini configuration
- ✓ Test path accessibility
- ✓ Test discovery working
- ✓ GitHub Actions workflows
- ✓ Required dependencies
- ✓ Test markers

**When to use**:
- **Before first push**: Verify setup is correct
- **After configuration changes**: Ensure nothing broke
- **Troubleshooting**: Identify what's misconfigured
- **CI/CD setup**: Run on new machines

---

## 🚀 Quick Start Workflow

### For First-Time Setup

```bash
# 1. Verify pipeline (should pass)
python scripts/verify_ci_pipeline.py

# 2. View all tests
python scripts/inventory_all_tests.py

# 3. Run tests locally (unit only)
pytest tests/ -k "not slow" -n auto

# 4. Push and watch workflow
git push origin feature-branch
```

### For Daily Development

```bash
# Check that your new test is discovered
python scripts/inventory_all_tests.py --json | grep your_test_name

# Run tests locally before pushing
pytest tests/ -k "not slow" -n auto

# Push
git push
```

### For Troubleshooting

```bash
# 1. Verify pipeline is working
python scripts/verify_ci_pipeline.py

# 2. Check all tests are discoverable
python scripts/inventory_all_tests.py --validate

# 3. If issues, try auto-fix
python scripts/verify_ci_pipeline.py --fix
python scripts/inventory_all_tests.py --fix

# 4. Try running tests locally
pytest tests/ -v --tb=short
```

---

## 📊 Script Comparison

| Feature | inventory_all_tests | verify_ci_pipeline |
|---------|--------------------|--------------------|
| **Purpose** | Discover tests | Verify setup |
| **Speed** | ~10 seconds | ~30 seconds |
| **Output** | Test listing | Configuration report |
| **Auto-fix** | Yes (`--fix`) | Yes (`--fix`) |
| **JSON output** | Yes (`--json`) | Yes (`--json`) |
| **Use frequency** | Weekly | After changes |

---

## 🔍 Common Use Cases

### Use Case 1: Add New Test
```bash
# Write your test
echo '@pytest.mark.unit
def test_my_feature():
    assert True' > tests/test_my_feature.py

# Verify it's discovered
python scripts/inventory_all_tests.py --full | grep test_my_feature

# Run locally
pytest tests/test_my_feature.py -v

# Push
git add tests/test_my_feature.py
git commit -m "Add test for my feature"
git push
```

### Use Case 2: Debug Failing Test
```bash
# Run test locally first
pytest tests/test_failing.py -v

# Check if it uses mocks (bad)
grep -n "Mock\|@patch" tests/test_failing.py

# If it uses mocks, refactor to use real objects
# Then re-run

# If still failing, check dependencies
python scripts/verify_ci_pipeline.py

# Then push for full CI validation
git push
```

### Use Case 3: Find Slow Tests
```bash
# Run all tests with durations
pytest tests/ --durations=20

# Output shows 20 slowest tests
# Add @pytest.mark.slow to tests >1 second
# Then they're excluded from quick runs

python scripts/inventory_all_tests.py --full
```

### Use Case 4: Check Coverage
```bash
# Run with coverage
pytest tests/ --cov=seed --cov=web/server --cov-report=html

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

---

## ⚙️ Configuration Files

### `pytest.ini`
Main pytest configuration. Modified to include:
- Both test directories
- All markers (exp01-exp10, unit, integration, load, slow)
- Timeout settings

**Don't edit directly unless you know what you're doing.**

### `.github/workflows/comprehensive-test-suite.yml`
Main CI/CD workflow. Automatically triggered on:
- Push to main/develop
- Pull requests
- Schedule (daily)
- Manual trigger (workflow_dispatch)

**Modify if you need different test configuration.**

---

## 🆘 Troubleshooting

### Problem: "No tests found"

```bash
# Check pytest configuration
python scripts/inventory_all_tests.py --validate

# Fix configuration
python scripts/inventory_all_tests.py --fix

# Verify
python scripts/inventory_all_tests.py
```

### Problem: "Tests can't import modules"

```bash
# Check if pytest discovery works
pytest --collect-only -q

# If errors, check Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Try again
pytest --collect-only -q
```

### Problem: "Dependencies missing"

```bash
# Check what's missing
python scripts/verify_ci_pipeline.py

# Install missing packages
pip install pytest pytest-cov pytest-xdist pytest-asyncio

# Verify
python scripts/verify_ci_pipeline.py
```

### Problem: "Workflow not triggering"

```bash
# Verify workflow file exists
ls -la .github/workflows/comprehensive-test-suite.yml

# Check workflow syntax (if you edited it)
cat .github/workflows/comprehensive-test-suite.yml | python -m yaml

# Otherwise, manually trigger:
# GitHub → Actions → Comprehensive Test Suite → Run workflow
```

---

## 📈 Monitoring

### Daily
```bash
# Check that tests are still being discovered
python scripts/inventory_all_tests.py
# Should show: Discovered 46+ total tests
```

### Weekly
```bash
# Detailed review
python scripts/inventory_all_tests.py --full

# Export for analysis
python scripts/inventory_all_tests.py --json > /tmp/tests.json
```

### After Configuration Changes
```bash
# Full verification
python scripts/verify_ci_pipeline.py

# Should pass all checks
```

---

## 🔧 Advanced Usage

### Export Test Manifest
```bash
# Get JSON with all tests
python scripts/inventory_all_tests.py --json > test-manifest.json

# Use in other tools/scripts
cat test-manifest.json | jq '.test_details.experiment_tests | length'
# Shows: Number of experiment tests
```

### Validate Before Commit
```bash
# Add to pre-commit hook
#!/bin/bash
python scripts/verify_ci_pipeline.py || exit 1
python scripts/inventory_all_tests.py --validate || exit 1
```

### Generate Report
```bash
# Create comprehensive report
python scripts/verify_ci_pipeline.py --json > /tmp/pipeline-check.json
python scripts/inventory_all_tests.py --json > /tmp/test-inventory.json

# Combine
jq -s 'add' /tmp/pipeline-check.json /tmp/test-inventory.json > report.json
```

---

## 📚 Related Documentation

- **[PIPELINE_STRATEGY.md](../.github/PIPELINE_STRATEGY.md)** - Complete architecture guide
- **[PIPELINE_QUICK_START.md](../.github/PIPELINE_QUICK_START.md)** - Quick reference
- **[BEFORE_AND_AFTER.md](../.github/BEFORE_AND_AFTER.md)** - Visual comparison
- **[pytest.ini](../pytest.ini)** - Test configuration

---

## ✅ Quick Checklist

- [ ] Both scripts are in `scripts/` directory
- [ ] Both scripts are executable: `chmod +x scripts/*.py`
- [ ] Can run both locally: `python scripts/verify_ci_pipeline.py`
- [ ] Test discovery finds 46+ tests
- [ ] pytest.ini exists and looks correct
- [ ] GitHub workflows exist in `.github/workflows/`

---

## 🎯 Key Takeaways

1. **Use `inventory_all_tests.py`** to discover and manage all tests
2. **Use `verify_ci_pipeline.py`** to ensure everything is configured correctly
3. **Run `--fix` options** if things break
4. **Run locally first** before pushing to GitHub
5. **Check outputs regularly** to catch issues early

---

**Status**: ✅ All scripts ready for use

For issues or questions, check the troubleshooting section above or refer to the comprehensive documentation in `.github/` directory.