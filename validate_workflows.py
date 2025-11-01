#!/usr/bin/env python3
"""Comprehensive YAML validation for all workflow files."""

import yaml
import glob
import sys
from pathlib import Path

def validate_workflows():
    """Validate all workflow files and report errors."""
    errors = []
    warnings = []
    valid_count = 0
    
    workflows = sorted(glob.glob('.github/workflows/*.yml'))
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE WORKFLOW YAML VALIDATION")
    print("=" * 80)
    print(f"\n📁 Scanning {len(workflows)} workflow files...\n")
    
    for wf_path in workflows:
        wf_name = Path(wf_path).name
        try:
            with open(wf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                yaml.safe_load(content)
            print(f"✅ {wf_name}")
            valid_count += 1
        except yaml.YAMLError as e:
            error_msg = str(e).split('\n')[0]
            errors.append({'file': wf_name, 'error': error_msg})
            print(f"❌ {wf_name}: {error_msg}")
        except Exception as e:
            errors.append({'file': wf_name, 'error': str(e)})
            print(f"❌ {wf_name}: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"📊 RESULTS: {valid_count}/{len(workflows)} valid")
    print("=" * 80)
    
    if errors:
        print(f"\n❌ FOUND {len(errors)} ERRORS:\n")
        for i, err in enumerate(errors, 1):
            print(f"{i}. {err['file']}")
            print(f"   Error: {err['error'][:150]}")
            if len(err['error']) > 150:
                print(f"   {err['error'][150:]}")
        return False
    else:
        print("\n✅ ALL WORKFLOW FILES ARE VALID!")
        return True

if __name__ == "__main__":
    success = validate_workflows()
    sys.exit(0 if success else 1)