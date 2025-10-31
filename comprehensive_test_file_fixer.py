#!/usr/bin/env python3
"""
Comprehensive fix for test files:
1. Ensure proper UTF-8 BOM at the very start
2. Ensure proper import pytest statement
3. Fix file structure: BOM → shebang/encoding → imports → decorators → code
"""

import os
import re
from pathlib import Path

def fix_test_file(filepath):
    """Fix a test file to have proper structure."""
    try:
        # Read file as binary to preserve BOM
        with open(filepath, 'rb') as f:
            binary_content = f.read()
        
        # Remove any existing BOM
        if binary_content.startswith(b'\xef\xbb\xbf'):
            binary_content = binary_content[3:]
        
        # Decode as UTF-8
        try:
            text_content = binary_content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = binary_content.decode('utf-8', errors='replace')
        
        lines = text_content.split('\n')
        
        # Parse file structure
        shebang_idx = None
        encoding_idx = None
        docstring_end_idx = None
        import_pytest_idx = None
        first_code_idx = None
        
        in_docstring = False
        docstring_char = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Shebang (should be line 0)
            if i == 0 and stripped.startswith('#!'):
                shebang_idx = i
                continue
            
            # Encoding (should be line 0 or 1)
            if 'coding' in stripped and stripped.startswith('#'):
                encoding_idx = i
                continue
            
            # Docstring
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    docstring_char = '"""' if '"""' in stripped else "'''"
                    # Single-line docstring?
                    if stripped.count(docstring_char) >= 2:
                        in_docstring = False
                        docstring_end_idx = i
                else:
                    in_docstring = False
                    docstring_end_idx = i
                continue
            
            if in_docstring:
                continue
            
            # Import pytest
            if 'import pytest' in line:
                import_pytest_idx = i
                continue
            
            # Skip blank lines and comments before actual code
            if not stripped or stripped.startswith('#'):
                continue
            
            # First real code line
            if first_code_idx is None:
                first_code_idx = i
                break
        
        # Rebuild the file
        new_lines = []
        
        # Add shebang if exists
        if shebang_idx is not None:
            new_lines.append(lines[shebang_idx])
        
        # Add encoding if exists
        if encoding_idx is not None:
            new_lines.append(lines[encoding_idx])
        
        # Add docstring if exists
        if docstring_end_idx is not None:
            for i in range((shebang_idx if shebang_idx is not None else 0) + 
                          (1 if encoding_idx is not None else 0),
                          docstring_end_idx + 1):
                if i < len(lines) and i not in [shebang_idx, encoding_idx]:
                    new_lines.append(lines[i])
        
        # Add import pytest if not present
        if import_pytest_idx is None:
            new_lines.append('import pytest')
        
        # Add blank line if needed
        if new_lines and new_lines[-1].strip():
            new_lines.append('')
        
        # Add rest of the file (all non-header lines)
        start_idx = (docstring_end_idx if docstring_end_idx is not None 
                    else (encoding_idx if encoding_idx is not None 
                          else (shebang_idx if shebang_idx is not None else -1))) + 1
        
        for i in range(start_idx, len(lines)):
            if i not in [shebang_idx, encoding_idx, import_pytest_idx] and i <= (docstring_end_idx or -1):
                continue
            if i >= len(lines):
                break
            if lines[i].strip() or (i > start_idx):  # Keep all lines after headers
                new_lines.append(lines[i])
        
        # Remove trailing empty lines
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()
        
        # Join back
        final_content = '\n'.join(new_lines)
        if final_content and not final_content.endswith('\n'):
            final_content += '\n'
        
        # Write back with UTF-8 BOM
        with open(filepath, 'wb') as f:
            f.write(b'\xef\xbb\xbf' + final_content.encode('utf-8'))
        
        return True
    except Exception as e:
        print(f"ERROR in {filepath}: {e}")
        return False

def main():
    """Process all problematic test files."""
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
    ]
    
    fixed = 0
    for filepath in problem_files:
        if os.path.exists(filepath):
            if fix_test_file(filepath):
                print(f"✅ FIXED: {filepath}")
                fixed += 1
            else:
                print(f"❌ FAILED: {filepath}")
        else:
            print(f"⚠️  NOT FOUND: {filepath}")
    
    print(f"\n✅ Fixed {fixed} files")

if __name__ == '__main__':
    main()