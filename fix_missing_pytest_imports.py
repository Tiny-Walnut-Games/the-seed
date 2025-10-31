#!/usr/bin/env python3
"""
Fix missing 'import pytest' in test files that have @pytest.mark decorators.
This corrects a bug in apply_test_markers.py that added decorators without imports.
"""

import os
import re
from pathlib import Path

def needs_pytest_import(filepath):
    """Check if file has @pytest.mark but no 'import pytest'."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    has_mark = '@pytest.mark' in content
    has_import = 'import pytest' in content
    
    return has_mark and not has_import

def add_pytest_import(filepath):
    """Add 'import pytest' to the file if missing."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    # Find the first non-comment, non-docstring line after encoding/shebang
    insert_index = 0
    in_docstring = False
    docstring_quote = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip encoding declarations and shebangs
        if i == 0 and (stripped.startswith('#!') or 'coding' in stripped):
            insert_index = i + 1
            continue
        
        if i == 1 and 'coding' in stripped:
            insert_index = i + 1
            continue
        
        # Skip blank lines
        if not stripped:
            insert_index = i + 1
            continue
        
        # Skip comments
        if stripped.startswith('#'):
            insert_index = i + 1
            continue
        
        # Handle docstrings
        if '"""' in stripped or "'''" in stripped:
            if not in_docstring:
                in_docstring = True
                docstring_quote = '"""' if '"""' in stripped else "'''"
                # Check if it's a single-line docstring
                if stripped.count(docstring_quote) >= 2:
                    in_docstring = False
            elif in_docstring:
                in_docstring = False
            insert_index = i + 1
            continue
        
        if in_docstring:
            insert_index = i + 1
            continue
        
        # Found the first real line
        break
    
    # Check if pytest is already imported
    for line in lines[:insert_index]:
        if 'import pytest' in line:
            return False  # Already has import
    
    # Insert the import
    lines.insert(insert_index, 'import pytest\n')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def main():
    """Scan all test files and fix missing imports."""
    test_dirs = [
        'tests',
        'packages/com.twg.the-seed/The Living Dev Agent/tests'
    ]
    
    fixed_files = []
    already_had = []
    
    for test_dir in test_dirs:
        if not os.path.isdir(test_dir):
            print(f"⚠️  Directory not found: {test_dir}")
            continue
        
        for filepath in Path(test_dir).rglob('test_*.py'):
            try:
                if needs_pytest_import(str(filepath)):
                    if add_pytest_import(str(filepath)):
                        fixed_files.append(str(filepath))
                        print(f"✅ FIXED: {filepath}")
                    else:
                        already_had.append(str(filepath))
            except Exception as e:
                print(f"❌ ERROR processing {filepath}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print(f"✅ Fixed {len(fixed_files)} files")
    print(f"⚠️  Already had import: {len(already_had)} files")
    print("="*80)
    
    if fixed_files:
        print("\nFixed files:")
        for f in sorted(fixed_files):
            print(f"  • {f}")

if __name__ == '__main__':
    main()