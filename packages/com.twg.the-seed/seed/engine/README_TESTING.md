# 🧪 Unified Seed Testing Framework

**Single Command Testing for EXP-01 → EXP-10 with Detailed Mathematical Reporting**

## 🚀 Quick Start

### Option 1: Simple Test Runner (from project root)
```bash
# Quick validation (EXP-01 through EXP-08)
python run_tests.py --quick

# Complete test suite (including API tests EXP-09, EXP-10)
python run_tests.py --full

# Generate HTML report for peer review
python run_tests.py --quick --report html
```

### Option 2: Direct Unified Suite (from engine directory)
```bash
# Run all tests with JSON report
python seed_test_suite.py

# Quick mode (core experiments only)
python seed_test_suite.py --quick

# Generate HTML report
python seed_test_suite.py --report html

# List available tests
python seed_test_suite.py --list
```

### Option 3: PyTest GUI Mode
```bash
# Run in Rider/PyCrunch test interface
pytest test_seed_pytest.py -v

# Run only core tests (skip slow API tests)
pytest test_seed_pytest.py -m "core"

# Generate HTML report
pytest test_seed_pytest.py --html=report.html --self-contained-html

# Skip slow tests
pytest test_seed_pytest.py -m "not slow"
```

## 📊 Test Coverage

### Core Experiments (Always Run)
- **EXP-01**: Address Uniqueness - Collision rate testing
- **EXP-02**: Retrieval Efficiency - Performance benchmarking
- **EXP-03**: Dimension Necessity - Ablation studies
- **EXP-04**: Fractal Scaling - Scale testing
- **EXP-05**: Compression/Expansion - Lossless validation
- **EXP-06**: Entanglement Detection - Relationship analysis
- **EXP-07**: LUCA Bootstrap - System reconstruction testing
- **EXP-08**: RAG Integration - Semantic retrieval validation

### API Integration (Full Suite Only)
- **EXP-09**: API Service - Concurrent query testing
- **EXP-10**: Bob the Skeptic - Anti-cheat validation

## 🧮 Mathematical Formulas

Each test includes detailed mathematical reporting:

### EXP-01: Address Uniqueness
```
Collision_Rate = Collisions / Total_Addresses
Target: < 0.001 (0.1%)
```

### EXP-02: Retrieval Efficiency
```
Retrieval_Time = O(log n) for STAT7 addressing
Target: < 2ms for 100K addresses
```

### EXP-03: Dimension Necessity
```
Dimension_Importance = Collision_Rate_With_Dimension_Removed
Target: All 7 dimensions show > 0.1% collisions when removed
```

### EXP-04: Fractal Scaling
```
Scaling_Factor = Latency_100K / Latency_1K
Target: < 5x degradation for 100x scale increase
```

### EXP-05: Compression/Expansion
```
Compression_Ratio = Compressed_Size / Original_Size
Target: Lossless compression with > 0.5x ratio
```

### EXP-06: Entanglement Detection
```
F1_Score = 2 * (Precision * Recall) / (Precision + Recall)
Target: > 0.8 F1 score
```

### EXP-07: LUCA Bootstrap
```
Recovery_Rate = Bootstrapped_Entities / Original_Entities
Target: > 95% recovery rate
```

### EXP-08: RAG Integration
```
RAG_Success_Rate = Successful_Queries / Total_Queries
Target: > 50% success rate (API service dependent)
```

### EXP-09: API Performance
```
API_Performance = Queries_Second / Response_Time_ms
Target: < 10ms average response time
```

### EXP-10: Bob's Anti-Cheat
```
Bob_Coherence_Threshold = 0.85 (anti-cheat trigger)
Target: System detects suspicious patterns
```

## 📈 Report Formats

### JSON Report
```json
{
  "total_tests": 8,
  "passed": 8,
  "failed": 0,
  "total_duration": 45.2,
  "results": [
    {
      "name": "EXP-01 Address Uniqueness",
      "status": "PASS",
      "duration": 2.1,
      "formula": "Collision_Rate = Collisions / Total_Addresses",
      "result_value": 0.0,
      "details": {"collision_rate": 0.0, "total_addresses": 10000}
    }
  ]
}
```

### HTML Report
- Interactive dashboard with charts
- Mathematical formula display
- Performance metrics visualization
- Error details and stack traces

### Markdown Report
- GitHub-compatible format
- Formula code blocks
- Summary tables
- Detailed test results

## 🎯 GUI Integration (Rider/PyCrunch)

### Test Categories
- `@pytest.mark.core`: Core experiments (fast)
- `@pytest.mark.slow`: API tests (requires service)
- `@pytest.mark.integration`: Full suite validation

### Test Structure
```python
class TestSeedCore:
    def test_exp01_address_uniqueness(self):
        # Individual test with assertions

class TestSeedAPI:
    @pytest.mark.slow
    def test_exp09_api_service(self):
        # API integration test
```

## 🔧 Features

### Auto-Dependency Management
- Installs required packages automatically
- Handles HuggingFace dataset downloads
- Manages API service startup/shutdown

### Real-Time Progress
- Live test execution status
- Performance warnings for slow tests
- Detailed error reporting

### Comprehensive Reporting
- Mathematical formulas with results
- Performance metrics and benchmarks
- Historical comparison capabilities

### Flexible Execution
- Quick mode for CI/CD pipelines
- Full mode for comprehensive validation
- GUI mode for interactive development

## 📁 File Structure

```
seed/engine/
├── seed_test_suite.py      # Unified test runner
├── test_seed_pytest.py     # PyTest integration
├── run_tests.py            # Quick start script
├── pytest.ini             # PyTest configuration
├── README_TESTING.md       # This file
└── results/                # Test reports
    ├── seed_test_report_*.json
    ├── seed_test_report_*.html
    └── seed_test_report_*.md
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the `seed/engine` directory
2. **API Service Fails**: Check port 8000 isn't in use
3. **HuggingFace Downloads**: May require internet connection
4. **Memory Issues**: Use `--quick` mode for limited resources

### Debug Mode
```bash
# Verbose output
python seed_test_suite.py --quick 2>&1 | tee debug.log

# PyTest debug mode
pytest test_seed_pytest.py -v -s --tb=long
```

## 🎯 Best Practices

### For Development
1. Use `--quick` mode during active development
2. Run full suite before committing changes
3. Check HTML reports for detailed analysis

### For CI/CD
1. Use `python run_tests.py --quick` for fast validation
2. Archive JSON reports for build history
3. Set failure thresholds for performance metrics

### For Research
1. Use `--full` mode for comprehensive validation
2. Generate HTML reports for detailed analysis
3. Compare mathematical formulas across runs

---

**Created**: 2025-10-22
**Purpose**: Unified testing framework for Seed experiments
**Compatibility**: Rider, PyCrunch, CLI, CI/CD
