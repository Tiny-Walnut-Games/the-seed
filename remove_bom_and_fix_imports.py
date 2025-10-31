#!/usr/bin/env python3
"""
Remove BOM and ensure pytest import is present.
BOM doesn't work well with shebangs in Python, so we'll remove it entirely.
"""

import os
from pathlib import Path

def fix_file(filepath):
    """Remove BOM and ensure import pytest."""
    try:
        # Read as binary
        with open(filepath, 'rb') as f:
            binary = f.read()
        
        # Remove BOM if present
        if binary.startswith(b'\xef\xbb\xbf'):
            binary = binary[3:]
        
        # Decode
        text = binary.decode('utf-8', errors='replace')
        
        # Ensure import pytest
        lines = text.split('\n')
        has_pytest = any('import pytest' in line for line in lines)
        
        if not has_pytest:
            # Find where to insert it
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Skip shebang and encoding
                if stripped.startswith('#!') or 'coding' in stripped:
                    insert_idx = i + 1
                    continue
                # Skip blank lines at start
                if not stripped:
                    insert_idx = i + 1
                    continue
                # Found first real content
                break
            
            lines.insert(insert_idx, 'import pytest')
        
        # Rejoin
        text = '\n'.join(lines)
        
        # Write back WITHOUT BOM
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return True
    except Exception as e:
        print(f"ERROR {filepath}: {e}")
        return False

def main():
    """Fix all problematic files."""
    problem_files = [
        'packages/com.twg.the-seed/The Living Dev Agent/tests/agent-profiles/test_agent_profile_validation.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/agent-profiles/test_runner.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_alchemist_report_synthesizer.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_badge_pet_system.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_baseline_set_validation.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_claims_classification.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_companion_battle_system.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_conservator.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_dtt_vault.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_experiment_harness.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_geo_thermal_scaffold.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_privacy_hooks.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_safety_policy_transparency.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_selfcare_system.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_semantic_anchors.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_template_system.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_v06_performance_optimization.py',
        'packages/com.twg.the-seed/The Living Dev Agent/tests/test_warbler_quote_integration.py',
    ]
    
    fixed = 0
    for filepath in problem_files:
        if os.path.exists(filepath):
            if fix_file(filepath):
                print(f"✅ {filepath}")
                fixed += 1
    
    print(f"\n✅ Fixed {fixed} files (removed BOM, ensured import pytest)")

if __name__ == '__main__':
    main()