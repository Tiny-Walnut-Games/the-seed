# 🧪 Alchemist Determinism Smoke Test Pipeline

This document describes the CI pipeline for testing determinism of Alchemist experiment runs, ensuring reproducibility in the narrative → evidence distillation process.

## Overview

The Alchemist Determinism Smoke Test pipeline automatically validates that experiments produce consistent, reproducible results when run with the same seeds and environment configuration. This is critical for the integrity of the Alchemist Faculty's distillation → serum promotion pipeline.

## Features

### 🎯 Core Capabilities
- **Automated determinism validation** for experiment manifests
- **Multiple run comparison** with fixed seeds and environment
- **Metrics hash comparison** for exact reproducibility verification
- **Statistical variance analysis** for result stability
- **PR status checks** with clear pass/fail indicators
- **Detailed reporting** with troubleshooting guidance

### 🔬 Testing Methodology
- Runs scaffolded experiments multiple times (default: 3 runs)
- Uses fixed seeds for deterministic execution
- Compares metrics.json hash values across runs
- Analyzes variance in numerical results
- Provides clear success/failure status

### 🚨 Alerting & Reporting
- PR comments with detailed determinism results
- Commit status checks for integration gates
- Workflow artifacts with full test reports
- Badge generation for repository status
- Automated troubleshooting tips

## Pipeline Triggers

The determinism pipeline runs on:

### Automatic Triggers
- **Push to main/develop**: When experiment-related files change
- **Pull Requests**: For all PRs touching experiment code
- **File Changes**: Specifically monitors:
  - `assets/experiments/**/*.yaml` - Experiment manifests
  - `scripts/alchemist-faculty/**` - Alchemist tooling
  - `engine/experiment_harness.py` - Core experiment framework

### Manual Triggers
- **Workflow Dispatch**: Manual execution with custom parameters
  - `run_count`: Number of runs per experiment (default: 3)
  - `variance_threshold`: Acceptable variance level (default: 0.01)

## Usage

### Running Determinism Tests Locally

```bash
# Test a single experiment manifest
python3 scripts/alchemist-faculty/determinism_smoke_test.py test \
  --manifest assets/experiments/school/manifests/experiment_example.yaml \
  --run-count 3

# Test all experiments in a directory
python3 scripts/alchemist-faculty/determinism_smoke_test.py suite \
  --search-path assets/experiments \
  --pattern "*.yaml" \
  --run-count 3 \
  --variance-threshold 0.01

# Create a test manifest for validation
python3 scripts/alchemist-faculty/determinism_smoke_test.py create-test-manifest \
  --output test_manifest.yaml

# Find available experiment manifests
python3 scripts/alchemist-faculty/determinism_smoke_test.py find-manifests \
  --search-path assets/experiments
```

### CI Integration

The pipeline automatically:

1. **Discovers** experiment manifests in the repository
2. **Executes** each experiment multiple times with fixed seeds
3. **Compares** results for consistency
4. **Reports** determinism status on PRs
5. **Sets** commit status checks for branch protection

## Expected Results & Interpretation

### ✅ Success Criteria
- **Hash Match**: All runs produce identical metrics.json hashes
- **Low Variance**: Numerical metrics within acceptable variance threshold
- **No Errors**: All experiment runs complete successfully

### ❌ Failure Conditions
- **Hash Mismatch**: Different metrics across runs with same configuration
- **High Variance**: Numerical results vary beyond threshold
- **Execution Errors**: Experiments fail to complete

### 📊 Status Reporting

| Success Rate | Badge Color | Interpretation |
|-------------|-------------|----------------|
| 100% | 🟢 Green | All experiments deterministic |
| 80-99% | 🟡 Yellow | Mostly deterministic, review needed |
| 50-79% | 🟠 Orange | Some determinism issues |
| <50% | 🔴 Red | Poor determinism, immediate attention required |

## Troubleshooting Guide

### Common Determinism Issues

#### 1. **Hash Mismatch Across Runs**
- **Cause**: Non-deterministic elements in experiment execution
- **Solutions**:
  - Ensure fixed seed configuration in manifests (`processing.seed`)
  - Disable parallel execution (`processing.parallel_execution: false`)
  - Check for time-dependent operations in experiment code
  - Verify deterministic mode is enabled (`processing.deterministic_mode: true`)

#### 2. **High Variance in Timing Metrics**
- **Cause**: Expected system performance variations
- **Solutions**:
  - Timing metrics are automatically excluded from hash comparison
  - Adjust variance threshold for performance experiments
  - Use `--variance-threshold 0.1` for more tolerance
  - Focus on functional metrics rather than performance metrics

#### 3. **Manifest Loading Errors**
- **Cause**: Invalid YAML format or missing required fields
- **Solutions**:
  - Validate YAML syntax using online validators
  - Ensure required fields are present: `metadata`, `processing`
  - Check for multiple document separators (`---`) in YAML files
  - Review manifest against schema documentation

#### 4. **BehavioralGovernance Parameter Errors**
- **Cause**: Compatibility issues with experiment harness
- **Solutions**:
  - Script automatically falls back to synthetic execution
  - Review `intervention_threshold` configuration format
  - Update experiment manifests to current format
  - Check logs for specific parameter issues

#### 1. **Seed Configuration Problems**
**Symptoms**: Different results across runs
**Solutions**:
- Verify `processing.seed` is set in experiment manifest
- Ensure `corpus.seed` matches processing seed
- Check that `deterministic_mode: true` is enabled

```yaml
processing:
  seed: 42
  deterministic_mode: true
  parallel_execution: false

corpus:
  seed: 42
  type: synthetic
```

#### 2. **Parallel Execution Issues**
**Symptoms**: Inconsistent results, timing variations
**Solutions**:
- Disable parallel processing: `parallel_execution: false`
- Use single-threaded execution for determinism tests
- Review any multithreaded operations in experiment code

#### 3. **Floating Point Precision**
**Symptoms**: Tiny variations in numerical metrics
**Solutions**:
- Adjust variance threshold if variations are acceptable
- Review metric calculation precision
- Consider rounding in metric computation

#### 4. **Time-Dependent Operations**
**Symptoms**: Different timestamps, execution times
**Solutions**:
- Use fixed timestamps for testing
- Exclude time-based metrics from determinism validation
- Review any operations that depend on system time

#### 5. **External Dependencies**
**Symptoms**: Network-dependent variations, file system differences
**Solutions**:
- Mock external dependencies for determinism tests
- Use synthetic data instead of external sources
- Ensure consistent environment configuration

### Advanced Troubleshooting

#### Understanding Determinism Test Results

**Hash Comparison**:
- Excludes timing-related metrics (time, throughput, duration) to focus on functional determinism
- Rounds floating-point values to 6 decimal places to handle precision variations
- Compares core experiment metrics like success rates, item counts, and processing outcomes

**Variance Analysis**:
- Uses coefficient of variation (CV) to measure relative variability
- Timing metrics get 10x more permissive thresholds (default: 0.1 vs 0.01)
- Reports specific metrics that exceed variance thresholds
- Helps identify which parts of experiments are non-deterministic

**Test Suite Reporting**:
- Provides individual experiment results and overall statistics
- Generates both JSON data files and human-readable reports
- Archives results for historical trend analysis
- Includes troubleshooting recommendations

#### Analyzing Variance Reports
```bash
# Review detailed variance analysis
cat experiments/determinism_tests/determinism_report_*.txt

# Check individual run results
ls experiments/determinism_tests/harness_results/

# Examine JSON data for programmatic analysis
jq '.test_results[] | select(.success == false)' experiments/determinism_tests/determinism_suite_*.json
```

#### Custom Variance Thresholds
```bash
# Adjust threshold for specific experiment types
python3 scripts/alchemist-faculty/determinism_smoke_test.py test \
  --manifest experiment.yaml \
  --variance-threshold 0.05  # More permissive for timing-sensitive tests

# Use tighter thresholds for critical experiments
python3 scripts/alchemist-faculty/determinism_smoke_test.py test \
  --manifest critical_experiment.yaml \
  --variance-threshold 0.001  # Very strict for functional determinism
```

#### Debugging Individual Experiments
```bash
# Run with more iterations for statistical confidence
python3 scripts/alchemist-faculty/determinism_smoke_test.py test \
  --manifest experiment.yaml \
  --run-count 5  # More runs for better variance analysis

# Test specific manifest patterns
python3 scripts/alchemist-faculty/determinism_smoke_test.py suite \
  --search-path gu_pot \
  --pattern "*issue-100*" \
  --run-count 3
```

#### CI Integration Tips
```bash
# Manual workflow trigger with custom parameters
gh workflow run "Alchemist Determinism Smoke Test" \
  -f run_count=5 \
  -f variance_threshold=0.02

# Check determinism for specific experiments
gh workflow run "Alchemist Faculty - Determinism Smoke Test Pipeline" \
  -f experiment_pattern="issue-123" \
  -f test_iterations=3
```

## Configuration

### Pipeline Configuration

The determinism pipeline can be customized through:

1. **Workflow inputs** (for manual runs)
2. **Environment variables** in the workflow
3. **Script parameters** in the determinism test tool

### Default Settings

```yaml
# Default pipeline configuration
run_count: 3                    # Number of determinism test runs
variance_threshold: 0.01        # Acceptable coefficient of variation
timeout_minutes: 20             # Maximum pipeline execution time
results_retention_days: 30      # Artifact retention period
```

### Experiment Manifest Requirements

For determinism testing, experiment manifests should include:

```yaml
metadata:
  name: "Experiment Name"
  description: "Description"

processing:
  seed: 42                      # Required: Fixed seed
  deterministic_mode: true      # Required: Determinism flag
  parallel_execution: false     # Recommended: Disable parallelism

corpus:
  seed: 42                      # Should match processing seed
  type: synthetic               # Recommended for testing

validation:
  success_criteria:
    min_processed_items: 1
    max_error_rate: 0.1
```

## Integration with Alchemist Faculty

### Promotion Gate Integration
The determinism pipeline integrates with the Alchemist Faculty promotion gates:

1. **Pre-Distillation**: Validates determinism before claim generation
2. **Distilled → Serum Gate**: Ensures reproducible evidence
3. **Quality Assurance**: Part of the promotion gating checklist

### Baseline Set Validation
Works with existing baseline set validation:
- Leverages existing validation infrastructure
- Follows established schema patterns
- Integrates with CI/CD validation workflow

### Experiment Harness Integration
- Uses the existing `ExperimentHarness` when available
- Falls back to synthetic execution for testing
- Maintains compatibility with experiment framework

## Best Practices

### For Experiment Authors
1. **Always set deterministic seeds** in manifests
2. **Disable parallel execution** for critical experiments
3. **Test locally** before submitting PRs
4. **Review determinism reports** when tests fail

### For Repository Maintainers
1. **Monitor determinism success rates** over time
2. **Investigate variance trends** in experiment results
3. **Update variance thresholds** as needed for different experiment types
4. **Review failed experiments** promptly

### For CI/CD Integration
1. **Use determinism status** in branch protection rules
2. **Monitor pipeline performance** and timeout settings
3. **Archive test results** for historical analysis
4. **Update documentation** when adding new experiment types

## Examples

### Successful Determinism Test
```
🧪 Determinism Test Result:
  Experiment: Performance Optimization Test
  Status: ✅ PASS
  Hash Match: ✅
  Variance: ✅ Acceptable
```

### Failed Determinism Test
```
🧪 Determinism Test Result:
  Experiment: Non-Deterministic Example
  Status: ❌ FAIL
  Hash Match: ❌
  Variance: ❌ High
  Error: Hash mismatch detected across runs
```

### Suite Results
```
🧙‍♂️ Alchemist Determinism Test Suite Report
============================================================
Suite ID: det_suite_1757175404
Timestamp: 2025-09-06T16:16:44.971504

📊 Summary:
  Total Experiments: 5
  ✅ Deterministic: 4
  ❌ Non-deterministic: 1
  Success Rate: 80.0%
```

## Support

### Getting Help
- **GitHub Issues**: Report determinism pipeline problems
- **Workflow Artifacts**: Download detailed test results
- **Documentation**: Review troubleshooting guide above

### Contributing
- **Submit PRs** for pipeline improvements
- **Report bugs** in determinism detection
- **Suggest features** for better reporting

---

🧙‍♂️ *"A potion that changes each time you brew it is not alchemy, it's chaos."*  
*- Bootstrap Sentinel's Alchemist Wisdom*