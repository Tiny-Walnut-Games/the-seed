#!/usr/bin/env python3
"""
Fix UTF-8 BOM encoding for all Python test files.
This ensures Windows systems can properly decode files with emojis and special characters.
"""

import sys
from pathlib import Path

def add_utf8_bom_to_file(file_path):
    """Add UTF-8 BOM to file if not already present."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check if BOM already exists
        if content.startswith(b'\xef\xbb\xbf'):
            return False  # Already has BOM
        
        # Add BOM and write back
        with open(file_path, 'wb') as f:
            f.write(b'\xef\xbb\xbf' + content)
        return True
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False

def main():
    """Scan all Python files and add BOM where needed."""
    root = Path(__file__).parent
    
    # Scan both test directories
    test_dirs = [
        root / "tests",
        root / "packages/com.twg.the-seed/The Living Dev Agent/tests"
    ]
    
    fixed_count = 0
    skipped_count = 0
    
    for test_dir in test_dirs:
        if not test_dir.exists():
            print(f"[SKIP] Directory not found: {test_dir}")
            continue
        
        print(f"\n[SCAN] Processing {test_dir}...")
        py_files = list(test_dir.rglob("*.py"))
        
        for py_file in py_files:
            if add_utf8_bom_to_file(py_file):
                print(f"  [FIXED] {py_file.relative_to(root)}")
                fixed_count += 1
            else:
                skipped_count += 1
    
    print(f"\n[SUMMARY]")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Skipped (already had BOM): {skipped_count} files")
    print(f"  All Python test files now have UTF-8 BOM encoding")

if __name__ == "__main__":
    main()