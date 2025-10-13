# 🔄 Migration Guide: Baseline Set Schema Implementation

## Overview

This guide provides step-by-step instructions for migrating existing Alchemist experiments to use the new `baseline_set.json` schema. The migration ensures consistency, improves validation, and enhances integration with the experiment pipeline.

## Pre-Migration Assessment

### 1. Inventory Current Baselines

First, identify all existing baseline configurations in your experimental setup:

```bash
# Find existing baseline files
find . -name "*baseline*" -type f \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" \)

# Check current baseline references in experiments
grep -r "baseline" assets/experiments/ --include="*.json" --include="*.yaml"

# Review Stage 4 validation configurations
find assets/experiments/ -name "*validation*" -o -name "*stage*4*"
```

### 2. Analyze Current Structure

Document your existing baseline format:

```bash
# Extract sample baseline structure
python3 -c "
import json
import sys
from pathlib import Path

# Find and analyze existing baseline files
baseline_files = list(Path('.').glob('**/baseline*.json'))
for file in baseline_files[:3]:  # Sample first 3 files
    print(f'File: {file}')
    try:
        with open(file) as f:
            data = json.load(f)
        print(f'Keys: {list(data.keys())}')
        if 'metrics' in data:
            print(f'Metrics: {list(data[\"metrics\"].keys())}')
    except Exception as e:
        print(f'Error: {e}')
    print('---')
"
```

### 3. Backup Current Configuration

```bash
# Create migration backup
mkdir -p migration_backup/$(date +%Y%m%d_%H%M%S)
cp -r data/ migration_backup/$(date +%Y%m%d_%H%M%S)/data/ 2>/dev/null || true
cp -r assets/experiments/ migration_backup/$(date +%Y%m%d_%H%M%S)/experiments/ 2>/dev/null || true
cp -r scripts/capture_baseline_metrics.py migration_backup/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

echo "✅ Backup created in migration_backup/"
```

## Migration Steps

### Step 1: Convert Existing data/baseline_metrics.json

The current `data/baseline_metrics.json` file can be converted to the new schema:

```python
#!/usr/bin/env python3
"""Convert existing baseline_metrics.json to baseline_set.json format"""

import json
import sys
from datetime import datetime
from pathlib import Path

def migrate_baseline_metrics():
    """Convert data/baseline_metrics.json to new baseline_set format"""
    
    baseline_path = Path("data/baseline_metrics.json")
    if not baseline_path.exists():
        print("❌ data/baseline_metrics.json not found")
        return False
    
    # Load existing baseline
    with open(baseline_path) as f:
        legacy_data = json.load(f)
    
    # Extract metadata from legacy format
    metadata = legacy_data.get("metadata", {})
    metrics = legacy_data.get("metrics", {})
    
    # Create new baseline_set structure
    baseline_set = {
        "metadata": {
            "version": "1.0.0",
            "created_at": metadata.get("captured_at", datetime.now().isoformat() + "Z"),
            "baseline_id": "migrated_self_care_baseline",
            "description": f"Migrated from self-care baseline: {metadata.get('purpose', 'Self-care system baseline')}",
            "author": "Migration Script",
            "tags": ["self-care", "migrated"],
            "alchemist_version": "0.1.0"
        },
        "baseline_metrics": {
            "primary_metrics": {},
            "secondary_metrics": {}
        },
        "experiment_context": {
            "experiment_type": "system_performance",
            "applicable_conditions": [
                {
                    "condition_name": "self_care_mode",
                    "condition_values": ["enabled", "disabled"],
                    "default_value": "enabled"
                }
            ],
            "environment_requirements": {
                "min_corpus_size": 50,
                "required_features": ["self_care_tracking"],
                "incompatible_features": []
            }
        },
        "provenance": {
            "establishment_method": "historical_analysis",
            "source_experiments": [
                {
                    "experiment_id": "self_care_baseline_capture",
                    "weight": 1.0
                }
            ]
        },
        "usage_notes": {
            "description": "Baseline established from self-care system metrics including idea catalog, cognitive state, melt budget, and development telemetry.",
            "migration_notes": "Migrated from legacy data/baseline_metrics.json format. Original structure preserved in secondary metrics.",
            "known_limitations": [
                "Historical data may not reflect current system behavior",
                "Sample sizes may be limited for some metrics"
            ]
        }
    }
    
    # Process idea catalog metrics
    idea_catalog = metrics.get("idea_catalog", {})
    if idea_catalog:
        if "total_ideas" in idea_catalog:
            baseline_set["baseline_metrics"]["primary_metrics"]["total_ideas_count"] = {
                "value": idea_catalog["total_ideas"],
                "unit": "count",
                "threshold_lower": 10,
                "threshold_upper": 200
            }
        
        if "promoted_ideas" in idea_catalog:
            baseline_set["baseline_metrics"]["secondary_metrics"]["promoted_ideas_count"] = {
                "value": idea_catalog["promoted_ideas"],
                "unit": "count"
            }
    
    # Process cognitive state metrics
    cognitive_state = metrics.get("cognitive_state", {})
    if cognitive_state:
        if "violations" in cognitive_state:
            baseline_set["baseline_metrics"]["primary_metrics"]["cognitive_violations"] = {
                "value": cognitive_state["violations"],
                "unit": "count",
                "threshold_upper": 5
            }
    
    # Process melt budget metrics
    melt_budget = metrics.get("melt_budget", {})
    if melt_budget:
        if "budget_utilization_percent" in melt_budget:
            baseline_set["baseline_metrics"]["primary_metrics"]["melt_budget_utilization"] = {
                "value": melt_budget["budget_utilization_percent"],
                "unit": "percent",
                "threshold_upper": 80.0
            }
    
    # Process development telemetry
    dev_telemetry = metrics.get("development_telemetry", {})
    if dev_telemetry:
        if "hours_slept_last_night" in dev_telemetry:
            baseline_set["baseline_metrics"]["primary_metrics"]["sleep_hours"] = {
                "value": dev_telemetry["hours_slept_last_night"],
                "unit": "hours",
                "threshold_lower": 6.0,
                "threshold_upper": 10.0
            }
    
    # Process system health
    system_health = metrics.get("system_health", {})
    if system_health and "test_suite_passes" in system_health:
        baseline_set["baseline_metrics"]["primary_metrics"]["test_suite_pass_rate"] = {
            "value": 1.0 if system_health["test_suite_passes"] else 0.0,
            "unit": "ratio",
            "threshold_lower": 0.95
        }
    
    # Add derived metrics
    baseline_set["baseline_metrics"]["derived_metrics"] = {
        "self_care_health_score": {
            "formula": "(1 - cognitive_violations/10) * (sleep_hours/8) * test_suite_pass_rate",
            "unit": "composite_score",
            "description": "Overall self-care system health combining cognitive state, sleep, and test status"
        }
    }
    
    # Save migrated baseline
    output_path = Path("data/baseline_set.json")
    with open(output_path, 'w') as f:
        json.dump(baseline_set, f, indent=2)
    
    print(f"✅ Migrated baseline saved to: {output_path}")
    print(f"   Primary metrics: {len(baseline_set['baseline_metrics']['primary_metrics'])}")
    print(f"   Secondary metrics: {len(baseline_set['baseline_metrics']['secondary_metrics'])}")
    print(f"   Derived metrics: {len(baseline_set['baseline_metrics']['derived_metrics'])}")
    
    return True

if __name__ == "__main__":
    migrate_baseline_metrics()
```

Save this as `scripts/migrate_baseline_metrics.py` and run:

```bash
chmod +x scripts/migrate_baseline_metrics.py
python3 scripts/migrate_baseline_metrics.py
```

### Step 2: Validate Migrated Baseline

```bash
# Validate the migrated baseline
python3 scripts/validate_baseline_set.py data/baseline_set.json

# If validation fails, review and fix issues
# Common fixes needed:
# - Adjust metric names to follow naming conventions
# - Set appropriate thresholds based on historical data
# - Add missing required fields
```

### Step 3: Update Experiment Configurations

Update experiment manifests to reference the new baseline format:

```python
#!/usr/bin/env python3
"""Update experiment manifests to use new baseline_set format"""

import json
import yaml
from pathlib import Path

def update_experiment_manifests():
    """Update experiment manifests to reference baseline_set.json"""
    
    manifest_files = list(Path("assets/experiments").glob("**/*.yaml"))
    manifest_files.extend(list(Path("assets/experiments").glob("**/*.json")))
    
    for manifest_path in manifest_files:
        try:
            # Load manifest
            with open(manifest_path) as f:
                if manifest_path.suffix in ['.yaml', '.yml']:
                    manifest = yaml.safe_load(f)
                else:
                    manifest = json.load(f)
            
            # Check if this manifest has baseline references
            updated = False
            
            # Update baseline references in metrics section
            if "metrics" in manifest and "baselines" in manifest["metrics"]:
                for baseline in manifest["metrics"]["baselines"]:
                    if baseline.get("name") == "baseline_metrics":
                        baseline["name"] = "baseline_set"
                        baseline["source"] = "data/baseline_set.json"
                        updated = True
            
            # Update processing configuration
            if "processing" in manifest:
                if "baseline_file" in manifest["processing"]:
                    manifest["processing"]["baseline_file"] = "data/baseline_set.json"
                    updated = True
            
            # Update validation configuration
            if "validation" in manifest and "baseline_comparison" in manifest["validation"]:
                manifest["validation"]["baseline_comparison"]["source"] = "data/baseline_set.json"
                updated = True
            
            # Save updated manifest
            if updated:
                with open(manifest_path, 'w') as f:
                    if manifest_path.suffix in ['.yaml', '.yml']:
                        yaml.dump(manifest, f, default_flow_style=False, indent=2)
                    else:
                        json.dump(manifest, f, indent=2)
                
                print(f"✅ Updated: {manifest_path}")
            
        except Exception as e:
            print(f"⚠️ Error processing {manifest_path}: {e}")

if __name__ == "__main__":
    update_experiment_manifests()
```

### Step 4: Update Stage 4 Validation Integration

Update the Stage 4 validation to use the new baseline format:

```python
# In your Stage 4 validation code, update baseline loading:

def load_baseline_set(baseline_path="data/baseline_set.json"):
    """Load baseline_set.json with validation"""
    from scripts.validate_baseline_set import BaselineSetValidator
    
    # Validate baseline first
    validator = BaselineSetValidator()
    is_valid, errors, warnings = validator.validate_file(baseline_path)
    
    if not is_valid:
        print(f"❌ Invalid baseline set: {baseline_path}")
        for error in errors:
            print(f"  - {error}")
        return None
    
    # Load validated baseline
    with open(baseline_path) as f:
        baseline_set = json.load(f)
    
    # Extract metrics for comparison
    baseline_metrics = {}
    
    # Process primary metrics
    for metric_name, metric_data in baseline_set["baseline_metrics"]["primary_metrics"].items():
        baseline_metrics[metric_name] = {
            "value": metric_data["value"],
            "unit": metric_data["unit"],
            "threshold_upper": metric_data.get("threshold_upper"),
            "threshold_lower": metric_data.get("threshold_lower"),
            "tolerance": metric_data.get("tolerance", 0.1)
        }
    
    return baseline_metrics

# Use in your validation pipeline:
baseline_metrics = load_baseline_set()
if baseline_metrics:
    # Perform baseline comparison
    deltas = calculate_baseline_deltas(experiment_results, baseline_metrics)
```

### Step 5: Update Capture Script Integration

Modify the baseline capture script to generate baseline_set format:

```python
# Add to scripts/capture_baseline_metrics.py

def generate_baseline_set(baseline_data, output_path="data/baseline_set.json"):
    """Generate baseline_set.json from captured metrics"""
    
    baseline_set = {
        "metadata": {
            "version": "1.0.0",
            "created_at": datetime.datetime.now().isoformat() + "Z",
            "baseline_id": f"captured_baseline_{datetime.datetime.now().strftime('%Y%m%d')}",
            "description": "Automatically captured baseline metrics from current system state",
            "author": "Baseline Capture Script",
            "tags": ["captured", "self-care", "automated"],
            "alchemist_version": "0.1.0"
        },
        "baseline_metrics": {
            "primary_metrics": convert_metrics_to_baseline_format(baseline_data["metrics"]),
            "derived_metrics": {
                "system_health_composite": {
                    "formula": "test_suite_pass_rate * (1 - cognitive_violations/10) * (sleep_hours/8)",
                    "unit": "composite_score",
                    "description": "Overall system health composite metric"
                }
            }
        },
        "experiment_context": {
            "experiment_type": "system_performance",
            "applicable_conditions": [
                {
                    "condition_name": "capture_mode",
                    "condition_values": ["manual", "automated"],
                    "default_value": "automated"
                }
            ]
        },
        "provenance": {
            "establishment_method": "single_experiment",
            "source_experiments": [
                {
                    "experiment_id": f"baseline_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "weight": 1.0
                }
            ]
        }
    }
    
    # Save baseline set
    with open(output_path, 'w') as f:
        json.dump(baseline_set, f, indent=2)
    
    return baseline_set
```

## Validation and Testing

### Step 6: Comprehensive Validation

```bash
# Validate all baseline files
python3 scripts/validate_baseline_set.py --directory data/ --pattern "*baseline*.json"

# Run baseline set validation tests
python3 tests/test_baseline_set_validation.py

# Test experiment integration
cd assets/experiments/school/
# Run a test experiment to verify baseline integration works
```

### Step 7: Integration Testing

Create a test experiment to verify the migration:

```yaml
# test_migration_experiment.yaml
metadata:
  name: "Migration Validation Test"
  description: "Test experiment to validate baseline migration"
  version: "1.0.0"

model:
  type: "simple"
  performance_profile: "dev"

conditions:
  test_condition: [1, 2]

corpus:
  type: "synthetic"
  size: 20

processing:
  batch_size: 5
  baseline_file: "data/baseline_set.json"  # New baseline reference

metrics:
  baselines:
    - name: "migrated_baseline"
      source: "data/baseline_set.json"

validation:
  baseline_comparison:
    source: "data/baseline_set.json"
    required_metrics: ["total_ideas_count", "sleep_hours"]

output:
  base_path: "migration_test_results"

execution:
  random_seeds:
    global_seed: 42

integration:
  chronicle_integration:
    enabled: false
```

## Rollback Procedures

### If Migration Issues Occur

```bash
# Restore from backup
BACKUP_DIR=$(ls -t migration_backup/ | head -1)
echo "Restoring from: migration_backup/$BACKUP_DIR"

# Restore data directory
cp -r migration_backup/$BACKUP_DIR/data/* data/ 2>/dev/null || true

# Restore experiments
cp -r migration_backup/$BACKUP_DIR/experiments/* assets/experiments/ 2>/dev/null || true

# Restore scripts
cp migration_backup/$BACKUP_DIR/capture_baseline_metrics.py scripts/ 2>/dev/null || true

echo "✅ Rollback completed"
```

### Selective Rollback

```bash
# Rollback specific components only
git checkout HEAD~1 -- data/baseline_set.json  # Remove new baseline
git checkout HEAD~1 -- data/baseline_metrics.json  # Restore old baseline

# Rollback experiment manifests
git checkout HEAD~1 -- assets/experiments/
```

## Post-Migration Verification

### Step 8: Final Verification

```bash
# 1. Verify all baselines are valid
echo "🔍 Validating all baseline files..."
python3 scripts/validate_baseline_set.py --directory . --pattern "*baseline_set*.json"

# 2. Run experiment harness tests
echo "🧪 Testing experiment harness integration..."
python3 tests/test_experiment_harness.py

# 3. Verify Stage 4 validation works
echo "🎯 Testing Stage 4 validation..."
# Run a sample experiment through the pipeline

# 4. Check CI integration
echo "⚙️ Validating CI integration..."
.github/workflows/ci.yml  # Review the updated workflow
```

### Step 9: Documentation Updates

Update relevant documentation:

```bash
# Update experiment documentation
# Update README files that reference baseline configurations
# Update any custom scripts that use baseline data
# Update team documentation about baseline procedures
```

## Common Migration Issues and Solutions

### Issue 1: Metric Name Conflicts

**Problem**: Existing metric names don't follow new naming conventions

**Solution**:
```python
# Rename metrics to follow conventions
METRIC_NAME_MAPPING = {
    "total_ideas": "total_ideas_count",
    "promoted_ideas": "promoted_ideas_count",
    "violations": "cognitive_violations",
    "budget_utilization_percent": "melt_budget_utilization_pct"
}

def normalize_metric_names(baseline_set):
    for old_name, new_name in METRIC_NAME_MAPPING.items():
        for section in ["primary_metrics", "secondary_metrics"]:
            if old_name in baseline_set["baseline_metrics"][section]:
                baseline_set["baseline_metrics"][section][new_name] = \
                    baseline_set["baseline_metrics"][section].pop(old_name)
```

### Issue 2: Missing Threshold Values

**Problem**: Legacy baselines don't have threshold definitions

**Solution**:
```python
# Add default thresholds based on metric analysis
DEFAULT_THRESHOLDS = {
    "total_ideas_count": {"lower": 10, "upper": 200},
    "cognitive_violations": {"upper": 5},
    "sleep_hours": {"lower": 6.0, "upper": 10.0},
    "test_suite_pass_rate": {"lower": 0.95}
}

def add_default_thresholds(baseline_set):
    for metric_name, metric_data in baseline_set["baseline_metrics"]["primary_metrics"].items():
        if metric_name in DEFAULT_THRESHOLDS:
            thresholds = DEFAULT_THRESHOLDS[metric_name]
            metric_data.update(thresholds)
```

### Issue 3: Experiment Integration Failures

**Problem**: Experiments can't load new baseline format

**Solution**:
```python
# Add backward compatibility layer
def load_baseline_with_fallback(baseline_path):
    """Load baseline with fallback to legacy format"""
    try:
        # Try new format first
        return load_baseline_set(baseline_path)
    except Exception:
        # Fall back to legacy format
        return load_legacy_baseline(baseline_path.replace("baseline_set.json", "baseline_metrics.json"))
```

## Migration Checklist

- [ ] **Pre-Migration**
  - [ ] Inventory existing baseline files
  - [ ] Analyze current baseline structure
  - [ ] Create comprehensive backup
  - [ ] Review experiment dependencies

- [ ] **Migration Execution**
  - [ ] Convert data/baseline_metrics.json
  - [ ] Validate migrated baseline
  - [ ] Update experiment manifests
  - [ ] Update Stage 4 validation
  - [ ] Update capture script integration

- [ ] **Testing and Validation**
  - [ ] Run baseline validation
  - [ ] Execute integration tests
  - [ ] Verify CI pipeline
  - [ ] Test rollback procedures

- [ ] **Post-Migration**
  - [ ] Update documentation
  - [ ] Train team on new format
  - [ ] Monitor for issues
  - [ ] Clean up legacy files

## Support and Troubleshooting

### Getting Help

If you encounter issues during migration:

1. **Check validation output**: Run `python3 scripts/validate_baseline_set.py` with verbose flag
2. **Review logs**: Check experiment execution logs for baseline-related errors  
3. **Test components**: Use the test suite to isolate issues
4. **Rollback if needed**: Use backup procedures to restore previous state

### Debug Commands

```bash
# Debug baseline loading
python3 -c "
from scripts.validate_baseline_set import BaselineSetValidator
validator = BaselineSetValidator()
result = validator.validate_file('data/baseline_set.json')
print('Valid:', result[0])
print('Errors:', result[1])
print('Warnings:', result[2])
"

# Test experiment integration
python3 -c "
import json
with open('data/baseline_set.json') as f:
    baseline = json.load(f)
print('Baseline ID:', baseline['metadata']['baseline_id'])
print('Primary metrics:', list(baseline['baseline_metrics']['primary_metrics'].keys()))
"
```

---

*This migration guide ensures a smooth transition from legacy baseline formats to the new baseline_set.json schema, maintaining experimental continuity while gaining enhanced validation and integration capabilities.*