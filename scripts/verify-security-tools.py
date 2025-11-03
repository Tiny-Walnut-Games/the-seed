#!/usr/bin/env python3
"""
Verify that all security tools are installed and working correctly.
Run before committing security workflow changes.

Usage: python scripts/verify-security-tools.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n✅ Checking {description}...")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            shell=isinstance(cmd, str)
        )
        if result.returncode == 0:
            output = result.stdout.strip().split('\n')[0]
            print(f"   ✓ {output}")
            return True
        else:
            print(f"   ✗ Failed: {result.stderr}")
            return False
    except FileNotFoundError as e:
        print(f"   ✗ Not found: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Main verification routine."""
    print("🔍 Security Tools Verification")
    print("=" * 60)
    
    checks = [
        (["bandit", "--version"], "Bandit"),
        (["pip-audit", "--version"], "pip-audit"),
        (["safety", "--version"], "Safety"),
        (["trufflehog", "--version"], "TruffleHog"),
        (["semgrep", "--version"], "Semgrep"),
        (["cyclonedx-bom", "--help"], "CycloneDX BOM"),
    ]
    
    results = []
    for cmd, description in checks:
        results.append(run_command(cmd, description))
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} security tools verified successfully!")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tools verified. {total - passed} have issues.")
        print("\nTo install missing tools:")
        print("  pip install -r scripts/security-requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())