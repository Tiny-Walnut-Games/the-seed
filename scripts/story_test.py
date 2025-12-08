#!/usr/bin/env python3
"""Story Test for The Seed - Mental Model Adherence Validator.

Validates that the project implementation matches its claimed mental model.
Adapted from Tiny Walnut Games story-testing philosophy.
"""

import json
import os
import sys
import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class StoryTestReport:
    """Story test results."""

    timestamp: str
    project_name: str
    status: str  # PASS, FAIL, WARNING
    claims_verified: int
    claims_total: int
    artifacts_found: int
    artifacts_missing: int
    completeness_percentage: float
    quality_gates_passed: int
    quality_gates_total: int
    feature_flags_enabled: List[str]
    gaps: List[Dict]
    violations: List[Dict]


def load_config(config_path: str = "storytest-mental-model.json") -> Optional[Dict]:
    """Load mental model configuration."""
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found", file=sys.stderr)
        return None

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return None


def load_feature_flags(flags_path: str = "flags.yaml") -> Dict[str, bool]:
    """Load feature flags configuration."""
    if not os.path.exists(flags_path):
        return {}

    try:
        import yaml

        with open(flags_path, "r") as f:
            flags_data = yaml.safe_load(f)
            return {k: v.get("enabled", False) for k, v in flags_data.items()}
    except:
        return {}


def verify_artifacts(config: Dict, feature_flags: Dict[str, bool]) -> Tuple[int, int, List[str]]:
    """Verify required artifacts exist."""
    artifacts = config.get("required_artifacts", [])
    found = 0
    missing = []

    for artifact in artifacts:
        path = artifact.get("path")
        required = artifact.get("required", True)
        feature_flag = artifact.get("feature_flag")

        # Skip if feature flag is disabled
        if feature_flag and not feature_flags.get(feature_flag, False):
            continue

        if os.path.exists(path):
            found += 1
        elif required:
            missing.append(path)

    return found, len(missing), missing


def count_classes_in_file(filepath: str) -> int:
    """Count number of classes defined in a Python file."""
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    except:
        return 0


def verify_stat7_experiments() -> Tuple[int, List[str]]:
    """Verify STAT7 experiments (EXP-01 through EXP-09) are implemented."""
    experiments = [
        ("EXP-01", "Address Uniqueness", ["stat7_experiments.py"]),
        ("EXP-02", "Retrieval Efficiency", ["stat7_experiments.py"]),
        ("EXP-03", "Dimension Necessity", ["stat7_experiments.py"]),
        ("EXP-04", "Fractal Scaling", ["exp04_fractal_scaling.py"]),
        ("EXP-05", "Compression/Expansion", ["exp05_compression_expansion.py"]),
        ("EXP-06", "Entanglement Detection", ["exp06_entanglement_detection.py"]),
        ("EXP-07", "LUCA Bootstrap", ["exp07_luca_bootstrap.py"]),
        ("EXP-08", "RAG Integration", ["exp08_rag_integration.py"]),
        ("EXP-09", "Concurrency", ["exp09_concurrency.py", "exp09_api_service.py", "exp09_cli.py"]),
    ]

    implemented = 0
    missing = []
    base_path = "packages/com.twg.the-seed/seed/engine"

    for exp_id, exp_name, files in experiments:
        exp_complete = True
        for file in files:
            filepath = os.path.join(base_path, file)
            if not os.path.exists(filepath):
                missing.append(f"{exp_id} ({exp_name}): missing {file}")
                exp_complete = False

        if exp_complete:
            implemented += 1

    return implemented, missing


def verify_stat7_core() -> Tuple[bool, List[str]]:
    """Verify STAT7 core components exist."""
    core_files = [
        "stat7_entity.py",
        "stat7_rag_bridge.py",
        "stat7_companion.py",
        "stat7_badge.py",
        "stat7_visualization.py",
        "retrieval_api.py",
    ]

    base_path = "packages/com.twg.the-seed/seed/engine"
    missing = []

    for file in core_files:
        filepath = os.path.join(base_path, file)
        if not os.path.exists(filepath):
            missing.append(file)

    return len(missing) == 0, missing


def verify_test_coverage(test_dir: str = "tests") -> Tuple[int, List[str]]:
    """Count test files and check coverage."""
    if not os.path.exists(test_dir):
        return 0, ["Tests directory not found"]

    test_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))

    return len(test_files), test_files


def verify_documentation() -> Tuple[bool, List[str]]:
    """Verify documentation completeness."""
    issues = []

    # Check for Seed README
    seed_readme = "packages/com.twg.the-seed/seed/README.md"
    if not os.path.exists(seed_readme):
        issues.append("Seed README.md not found")
    else:
        with open(seed_readme, "r") as f:
            lines = len(f.readlines())
            if lines < 100:
                issues.append(f"Seed README has only {lines} lines (expected 100+)")

    # Check for documentation directory
    docs_dir = "packages/com.twg.the-seed/seed/docs"
    if not os.path.exists(docs_dir):
        issues.append("Documentation directory not found")

    return len(issues) == 0, issues


def verify_visualization_system() -> Tuple[bool, List[str]]:
    """Verify STAT7 visualization system."""
    required_files = [
        "web/server/stat7wsserve.py",
        "web/stat7_visualization_demo.ipynb",
        "packages/com.twg.the-seed/seed/engine/stat7_visualization.py",
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    return len(missing) == 0, missing


def verify_production_components() -> Tuple[bool, List[str]]:
    """Verify production-ready components."""
    components = [
        ("FastAPI Service", "packages/com.twg.the-seed/seed/engine/exp09_api_service.py"),
        ("CLI Interface", "packages/com.twg.the-seed/seed/engine/exp09_cli.py"),
        ("GPU Support", "packages/com.twg.the-seed/seed/engine/exp09_api_service_gpu_enabled.py"),
        ("Docker Support", "Dockerfile"),
    ]

    missing = []
    for name, path in components:
        if not os.path.exists(path):
            missing.append(f"{name}: {path}")

    return len(missing) == 0, missing


def validate_quality_gates(
    config: Dict, feature_flags: Dict[str, bool]
) -> Tuple[int, int, List[str]]:
    """Validate all quality gates."""
    gates = config.get("quality_gates", [])
    passed = 0
    failures = []

    for gate in gates:
        gate_name = gate.get("gate")
        critical = gate.get("critical", False)
        feature_flag = gate.get("feature_flag")

        # Skip if feature flag is disabled
        if feature_flag and not feature_flags.get(feature_flag, False):
            continue

        if gate_name == "stat7_experiments_complete":
            required = gate.get("required_experiments", 9)
            implemented, missing = verify_stat7_experiments()
            if implemented >= required:
                passed += 1
            else:
                msg = f"STAT7 Experiments: {implemented}/{required} implemented"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)
                if missing:
                    for m in missing[:3]:  # Show first 3
                        failures.append(f"  - {m}")

        elif gate_name == "stat7_core_complete":
            success, missing = verify_stat7_core()
            if success:
                passed += 1
            else:
                msg = f"STAT7 Core: missing {', '.join(missing)}"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)

        elif gate_name == "test_coverage":
            minimum = gate.get("minimum_test_files", 5)
            test_count, _ = verify_test_coverage()
            if test_count >= minimum:
                passed += 1
            else:
                msg = f"Test coverage: {test_count}/{minimum} test files"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)

        elif gate_name == "documentation_complete":
            success, issues = verify_documentation()
            if success:
                passed += 1
            else:
                msg = f"Documentation: {', '.join(issues)}"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)

        elif gate_name == "visualization_system":
            success, missing = verify_visualization_system()
            if success:
                passed += 1
            else:
                msg = f"Visualization: missing {', '.join(missing)}"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)

        elif gate_name == "production_ready":
            success, missing = verify_production_components()
            if success:
                passed += 1
            else:
                msg = f"Production components: {', '.join(missing[:2])}"
                if critical:
                    msg += " [CRITICAL]"
                failures.append(msg)

    return passed, len(gates), failures


def verify_claims(config: Dict, feature_flags: Dict[str, bool]) -> Tuple[int, int, List[str]]:
    """Verify claimed capabilities have evidence."""
    claims = config.get("claimed_capabilities", {})
    verified = 0
    total = 0
    gaps = []

    for category, items in claims.items():
        # Check if category has feature flag
        category_flag = None
        for item in items:
            if isinstance(item, dict) and "feature_flag" in item:
                category_flag = item["feature_flag"]
                break

        # Skip if feature flag is disabled
        if category_flag and not feature_flags.get(category_flag, False):
            continue

        total += len(items)

        if category == "stat7_addressing":
            success, missing = verify_stat7_core()
            if success:
                verified += len(items)
            else:
                gaps.append(f"STAT7 Addressing: {', '.join(missing)}")

        elif category == "validation_experiments":
            implemented, missing = verify_stat7_experiments()
            if implemented == 9:
                verified += len(items)
            else:
                gaps.append(f"Validation Experiments: {9 - implemented} missing")

        elif category == "visualization_system":
            success, missing = verify_visualization_system()
            if success:
                verified += len(items)
            else:
                gaps.append(f"Visualization: {', '.join(missing)}")

        elif category == "production_components":
            success, missing = verify_production_components()
            if success:
                verified += len(items)
            else:
                gaps.append(f"Production: {', '.join(missing[:2])}")

        elif category == "documentation":
            success, issues = verify_documentation()
            if success:
                verified += len(items)
            else:
                gaps.append(f"Documentation: {', '.join(issues)}")

    return verified, total, gaps


def generate_report(config: Dict, feature_flags: Dict[str, bool]) -> StoryTestReport:
    """Generate comprehensive story test report."""
    artifacts_found, artifacts_missing, missing_list = verify_artifacts(config, feature_flags)
    claims_verified, claims_total, claim_gaps = verify_claims(config, feature_flags)
    gates_passed, gates_total, gate_failures = validate_quality_gates(config, feature_flags)

    # Calculate completeness
    total_checks = claims_total + len(config.get("required_artifacts", [])) + gates_total
    total_success = claims_verified + artifacts_found + gates_passed
    completeness = (total_success / total_checks * 100) if total_checks > 0 else 0

    # Determine status
    critical_failures = [f for f in gate_failures if "[CRITICAL]" in f]
    if len(critical_failures) > 0:
        status = "FAIL"
    elif gates_passed == gates_total and len(claim_gaps) == 0:
        status = "PASS"
    else:
        status = "WARNING"

    # Collect all gaps
    all_gaps = []
    for artifact in missing_list:
        all_gaps.append({"type": "MISSING_ARTIFACT", "message": f"Required artifact: {artifact}"})
    for gap in claim_gaps:
        all_gaps.append({"type": "UNVERIFIED_CLAIM", "message": gap})
    for failure in gate_failures:
        gap_type = "CRITICAL_GATE_FAILED" if "[CRITICAL]" in failure else "QUALITY_GATE_FAILED"
        all_gaps.append({"type": gap_type, "message": failure})

    # Get enabled feature flags
    enabled_flags = [k for k, v in feature_flags.items() if v]

    return StoryTestReport(
        timestamp=datetime.now().isoformat(),
        project_name=config.get("project", {}).get("name", "Unknown"),
        status=status,
        claims_verified=claims_verified,
        claims_total=claims_total,
        artifacts_found=artifacts_found,
        artifacts_missing=artifacts_missing,
        completeness_percentage=completeness,
        quality_gates_passed=gates_passed,
        quality_gates_total=gates_total,
        feature_flags_enabled=enabled_flags,
        gaps=all_gaps,
        violations=[],
    )


def print_report(report: StoryTestReport):
    """Print story test report to console."""
    status_emoji = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}

    print("\n" + "=" * 70)
    print(f"  🌱 The Seed - Story Test Report")
    print("=" * 70)
    print(f"\nStatus: {status_emoji.get(report.status, '?')} {report.status}")
    print(f"Completeness: {report.completeness_percentage:.1f}%")
    print(f"\nMetrics:")
    print(f"  Claims Verified:  {report.claims_verified}/{report.claims_total}")
    print(
        f"  Artifacts Found:  {report.artifacts_found}/{report.artifacts_found + report.artifacts_missing}"
    )
    print(f"  Quality Gates:    {report.quality_gates_passed}/{report.quality_gates_total}")

    if report.feature_flags_enabled:
        print(f"\nFeature Flags Enabled ({len(report.feature_flags_enabled)}):")
        for flag in report.feature_flags_enabled[:5]:  # Show first 5
            print(f"  🚩 {flag}")
        if len(report.feature_flags_enabled) > 5:
            print(f"  ... and {len(report.feature_flags_enabled) - 5} more")

    if report.gaps:
        print(f"\nGaps & Issues ({len(report.gaps)}):")
        for gap in report.gaps[:10]:  # Show first 10
            print(f"  [{gap['type']}] {gap['message']}")
        if len(report.gaps) > 10:
            print(f"  ... and {len(report.gaps) - 10} more issues")
    else:
        print("\n✅ No gaps detected - mental model is coherent!")

    print("\n" + "=" * 70)
    print(f"Report generated: {report.timestamp}")
    print("=" * 70 + "\n")


def main():
    """Run story test validation."""
    config = load_config()

    if not config:
        sys.exit(1)

    # Load feature flags
    feature_flags = load_feature_flags()

    # Generate report
    report = generate_report(config, feature_flags)

    # Print to console
    print_report(report)

    # Output JSON for CI/CD
    report_dict = {
        "timestamp": report.timestamp,
        "project": report.project_name,
        "status": report.status,
        "completeness": f"{report.completeness_percentage:.1f}%",
        "metrics": {
            "claims": f"{report.claims_verified}/{report.claims_total}",
            "artifacts": f"{report.artifacts_found}/{report.artifacts_found + report.artifacts_missing}",
            "quality_gates": f"{report.quality_gates_passed}/{report.quality_gates_total}",
        },
        "feature_flags": report.feature_flags_enabled,
        "gaps": report.gaps,
    }

    with open("story-test-report.json", "w") as f:
        json.dump(report_dict, indent=2, fp=f)

    print(f"📊 JSON report saved: story-test-report.json\n")

    # Exit with appropriate code
    sys.exit(0 if report.status == "PASS" else 1)


if __name__ == "__main__":
    main()
