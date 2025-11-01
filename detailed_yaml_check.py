#!/usr/bin/env python3
"""Get detailed YAML error information."""

import yaml

files_to_check = [
    '.github/workflows/overlord-sentinel-security.yml',
    '.github/workflows/cid-schoolhouse.yml'
]

print("=" * 80)
print("📍 DETAILED YAML ERROR ANALYSIS")
print("=" * 80)

for filepath in files_to_check:
    print(f"\n\n📄 {filepath}")
    print("-" * 80)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print("✅ Valid")
    except yaml.YAMLError as e:
        print(f"❌ ERROR:")
        print(f"   Line: {e.problem_mark.line + 1}")
        print(f"   Column: {e.problem_mark.column + 1}")
        print(f"   Problem: {e.problem}")
        print(f"   Context: {e.problem_mark.get_snippet()}")
        
        # Show context lines
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            error_line = e.problem_mark.line + 1
            start = max(0, error_line - 3)
            end = min(len(lines), error_line + 2)
            
            print(f"\n   Context (lines {start+1}-{end}):")
            for i in range(start, end):
                marker = ">>>" if i == error_line - 1 else "   "
                print(f"   {marker} {i+1}: {lines[i].rstrip()}")