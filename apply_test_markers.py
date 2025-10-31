#!/usr/bin/env python3
"""
APPLY TEST MARKERS - Adds @pytest.mark decorators to all test files

This script uses the intelligence from assign_test_markers.py to add markers.
It modifies files in-place, adding markers just before test functions/classes.

WARNING: This modifies test files. Review the --dry-run first.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional


@dataclass
class MarkerInsertion:
    file_path: Path
    line_number: int
    test_name: str
    marker: str
    text_before: str
    text_after: str


class MarkerApplier:
    """Apply markers to test files."""
    
    # Heuristic patterns for marker assignment
    DEFINITE_E2E = {
        'test_stat7_e2e.py',
        'test_stat7_e2e_optimized.py',
        'test_e2e_scenarios.py',
        'test_websocket_load_stress.py',
        'test_enhanced_visualization.py',
        'test_governance_integration.py',
        'test_complete_system.py',
    }
    
    DEFINITE_UNIT = {
        'test_simple.py',
    }
    
    MOCK_PATTERNS = [
        r'Mock\(',
        r'@mock\.',
        r'patch\(',
        r'MagicMock',
        r'PropertyMock',
        r'Mock\w+\(',
    ]
    
    REAL_CONNECTION_PATTERNS = [
        r'async_playwright',
        r'playwright\.async_api',
        r'browser\.',
        r'\.goto\(',
        r'websocket',
        r'requests\.(get|post|put|delete)',
        r'\.connect\(',
        r'asyncio\.run',
        r'EventStore\(',
        r'TickEngine\(',
        r'GovernanceEngine\(',
        r'APIGateway\(',
        r'STAT7',
        r'tempfile\.mkdtemp',
    ]
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.insertions: List[MarkerInsertion] = []
        self.files_modified = 0
        self.markers_added = 0
    
    def process_all_tests(self, root_dir: Path):
        """Process all test files."""
        test_files = sorted(root_dir.rglob("test_*.py"))
        
        print(f"\n{'[DRY RUN]' if self.dry_run else '[LIVE]'} Processing {len(test_files)} test files...")
        print("="*70)
        
        total = len(test_files)
        for idx, test_file in enumerate(test_files, 1):
            markers = self.process_file(test_file)
            if markers:
                self.markers_added += len(markers)
                self.files_modified += 1
                print(f"[{idx:2}/{total}] {test_file.name:40} → {len(markers)} markers")
        
        return self.markers_added
    
    def process_file(self, file_path: Path) -> List[MarkerInsertion]:
        """Process a single test file."""
        try:
            content = file_path.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"ERROR reading {file_path}: {e}")
            return []
        
        lines = content.split('\n')
        insertions = []
        
        # Find all test functions and classes
        for line_no, line in enumerate(lines):
            # Check for test function
            if re.match(r'\s*def test_\w+\(', line):
                # Check if previous line has @pytest.mark
                has_marker = line_no > 0 and '@pytest.mark' in lines[line_no - 1]
                
                if not has_marker:
                    test_name = re.search(r'def (test_\w+)\(', line).group(1)
                    marker = self._determine_marker(file_path, content, test_name)
                    
                    insertion = MarkerInsertion(
                        file_path=file_path,
                        line_number=line_no,
                        test_name=test_name,
                        marker=marker,
                        text_before=line,
                        text_after=f"@pytest.mark.{marker}\n{line}"
                    )
                    insertions.append(insertion)
            
            # Check for test class
            elif re.match(r'\s*class Test\w+', line):
                # Check if previous line has @pytest.mark
                has_marker = line_no > 0 and '@pytest.mark' in lines[line_no - 1]
                
                if not has_marker:
                    test_name = re.search(r'class (Test\w+)', line).group(1)
                    marker = self._determine_marker(file_path, content, test_name)
                    
                    insertion = MarkerInsertion(
                        file_path=file_path,
                        line_number=line_no,
                        test_name=test_name,
                        marker=marker,
                        text_before=line,
                        text_after=f"@pytest.mark.{marker}\n{line}"
                    )
                    insertions.append(insertion)
        
        # Apply insertions if not dry run
        if insertions and not self.dry_run:
            self._apply_insertions(file_path, insertions)
        
        self.insertions.extend(insertions)
        return insertions
    
    def _determine_marker(self, file_path: Path, content: str, test_name: str) -> str:
        """Determine marker for a test."""
        
        # Quick wins
        if file_path.name in self.DEFINITE_E2E:
            return 'e2e'
        if file_path.name in self.DEFINITE_UNIT:
            return 'unit'
        
        # Find test block
        pattern = rf'(def|class) {test_name}\('
        match = re.search(pattern, content)
        if not match:
            return 'integration'  # Default
        
        # Extract test body
        start = match.start()
        remaining = content[start:]
        next_def = re.search(r'\n\s*(def|class) ', remaining[100:])
        end = start + (next_def.start() + 100 if next_def else len(remaining))
        test_body = remaining[:end - start]
        
        # Analyze
        mock_count = sum(len(re.findall(p, test_body)) for p in self.MOCK_PATTERNS)
        real_count = sum(len(re.findall(p, test_body)) for p in self.REAL_CONNECTION_PATTERNS)
        
        if real_count > 0 and mock_count == 0:
            return 'e2e'
        elif mock_count > 0 and real_count == 0:
            return 'unit'
        else:
            return 'integration'
    
    def _apply_insertions(self, file_path: Path, insertions: List[MarkerInsertion]):
        """Apply all insertions to a file."""
        try:
            content = file_path.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"ERROR reading {file_path}: {e}")
            return
        
        lines = content.split('\n')
        
        # Apply in reverse order to preserve line numbers
        for insertion in reversed(insertions):
            indent = len(lines[insertion.line_number]) - len(lines[insertion.line_number].lstrip())
            marker_line = ' ' * indent + f'@pytest.mark.{insertion.marker}'
            lines.insert(insertion.line_number, marker_line)
        
        # Write back
        try:
            modified_content = '\n'.join(lines)
            file_path.write_text(modified_content, encoding='utf-8-sig')
        except Exception as e:
            print(f"ERROR writing {file_path}: {e}")
    
    def print_summary(self):
        """Print summary of changes."""
        print("\n" + "="*70)
        print("APPLICATION SUMMARY")
        print("="*70)
        
        if self.dry_run:
            print(f"\n[DRY RUN] Would add {self.markers_added} markers to {self.files_modified} files")
        else:
            print(f"\n[APPLIED] Added {self.markers_added} markers to {self.files_modified} files")
        
        # Count by marker
        unit_count = len([i for i in self.insertions if i.marker == 'unit'])
        integration_count = len([i for i in self.insertions if i.marker == 'integration'])
        e2e_count = len([i for i in self.insertions if i.marker == 'e2e'])
        
        print(f"\n  @pytest.mark.unit:        {unit_count}")
        print(f"  @pytest.mark.integration: {integration_count}")
        print(f"  @pytest.mark.e2e:         {e2e_count}")
        
        print("\n" + "="*70)
    
    def print_samples(self, limit: int = 10):
        """Print sample changes."""
        if not self.insertions:
            return
        
        print("\n" + "="*70)
        print(f"SAMPLE CHANGES (showing {min(limit, len(self.insertions))} of {len(self.insertions)})")
        print("="*70)
        
        for insertion in self.insertions[:limit]:
            print(f"\n📝 {insertion.file_path.name}")
            print(f"   Test: {insertion.test_name}")
            print(f"   Marker: @pytest.mark.{insertion.marker}")
            print(f"   Before: {insertion.text_before.strip()}")
            print(f"   After:  @pytest.mark.{insertion.marker}")
            print(f"           {insertion.text_before.strip()}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Apply pytest markers to test files")
    parser.add_argument('--apply', action='store_true', help='Actually apply changes (default is dry-run)')
    parser.add_argument('--root', default='.', help='Root directory to scan')
    args = parser.parse_args()
    
    root = Path(args.root)
    dry_run = not args.apply
    
    applier = MarkerApplier(dry_run=dry_run)
    
    # Process tests directory
    tests_dir = root / "tests"
    if tests_dir.exists():
        applier.process_all_tests(tests_dir)
    
    # Process WARBLER tests
    warbler_tests = root / "packages/com.twg.the-seed/The Living Dev Agent/tests"
    if warbler_tests.exists():
        applier.process_all_tests(warbler_tests)
    
    # Print results
    applier.print_samples(limit=15)
    applier.print_summary()
    
    if dry_run:
        print("\n✅ DRY RUN COMPLETE")
        print("\nTo apply these changes, run:")
        print("  python apply_test_markers.py --apply")
    else:
        print("\n✅ MARKERS APPLIED SUCCESSFULLY")


if __name__ == "__main__":
    main()