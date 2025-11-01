#!/usr/bin/env python3
"""Find the exact line with YAML error."""

import yaml

filepath = '.github/workflows/overlord-sentinel-security.yml'

with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
    
try:
    yaml.safe_load(''.join(lines))
except yaml.YAMLError as e:
    error_line = e.problem_mark.line + 1
    error_col = e.problem_mark.column + 1
    
    print(f"Error on line {error_line}, column {error_col}")
    print(f"Problem: {e.problem}")
    
    # Show context with line numbers
    start = max(0, error_line - 5)
    end = min(len(lines), error_line + 5)
    
    print("\nContext:")
    for i in range(start, end):
        marker = ">>>" if i == error_line - 1 else "   "
        print(f"{marker} {i+1:4}: {lines[i]}", end='')
    
    # Show the specific line in detail
    print(f"\n\nProblematic line (raw bytes):")
    problem_line = lines[error_line - 1]
    print(f"Line {error_line}: {repr(problem_line)}")
    print(f"Character codes: {[ord(c) for c in problem_line[:50]]}")