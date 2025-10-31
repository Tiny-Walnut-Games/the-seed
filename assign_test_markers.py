#!/usr/bin/env python3
"""
INTELLIGENT TEST MARKER ASSIGNMENT

Scans all test files and adds @pytest.mark decorators based on:
- Mock usage (mocks = unit)
- Real system connections (real connections = e2e)
- Hybrid patterns (mixed = integration)

This ensures ALL 561 tests are properly categorized for release.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple


@dataclass
class TestAnalysis:
    file_path: Path
    test_name: str
    existing_markers: List[str]
    uses_mock: bool
    uses_real_connection: bool
    is_class: bool
    recommended_marker: str
    reasoning: str


class MarkerAssigner:
    """Intelligently assign pytest markers to tests."""
    
    # Patterns for detection
    MOCK_PATTERNS = [
        r'Mock\(',
        r'@mock\.',
        r'patch\(',
        r'MagicMock',
        r'PropertyMock',
        r'Mock\w+\(',  # MockEventStore, MockSTAT7, etc.
        r'unittest\.mock',
        r'from unittest\.mock',
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
        r'serve\(',
        r'start_server',
        r'EventStoreContract\(',
        r'EventStore\(',
        r'TickEngine\(',
        r'GovernanceEngine\(',
        r'APIGateway\(',
        r'STAT7',
        r'tempfile\.mkdtemp',  # Real file system ops
    ]
    
    # Files that are definitively E2E
    DEFINITE_E2E = {
        'test_stat7_e2e.py',
        'test_stat7_e2e_optimized.py',
        'test_e2e_scenarios.py',
        'test_websocket_load_stress.py',
        'test_enhanced_visualization.py',
    }
    
    # Files that are definitely UNIT
    DEFINITE_UNIT = {
        'test_simple.py',
    }
    
    def __init__(self):
        self.results: List[TestAnalysis] = []
        self.files_to_update: Dict[Path, List[Tuple[int, str]]] = {}
    
    def scan_all_tests(self, root_dir: Path) -> List[TestAnalysis]:
        """Scan all test files."""
        test_files = sorted(root_dir.rglob("test_*.py"))
        
        total = len(test_files)
        for idx, test_file in enumerate(test_files, 1):
            print(f"[{idx}/{total}] Scanning {test_file.name}...", end=" ")
            analyses = self._analyze_file(test_file)
            self.results.extend(analyses)
            print(f"✓ {len(analyses)} tests")
        
        return self.results
    
    def _analyze_file(self, file_path: Path) -> List[TestAnalysis]:
        """Analyze a single test file."""
        analyses = []
        
        try:
            content = file_path.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"ERROR reading {file_path}: {e}")
            return analyses
        
        # Find all test functions and classes
        test_functions = re.finditer(r'@pytest\.mark\.(\w+\s+)*def (test_\w+)\(', content)
        test_classes = re.finditer(r'@pytest\.mark\.(\w+\s+)*class (Test\w+)\(', content)
        
        for match in test_functions:
            test_name = match.group(2)
            existing = self._extract_existing_markers(match.group(1) or "")
            analysis = self._analyze_test(file_path, test_name, content, existing, is_class=False)
            analyses.append(analysis)
        
        # Also find unmarked test functions
        for match in re.finditer(r'def (test_\w+)\(', content):
            test_name = match.group(1)
            # Check if this test is already marked
            if not any(a.test_name == test_name for a in analyses):
                analysis = self._analyze_test(file_path, test_name, content, [], is_class=False)
                analyses.append(analysis)
        
        return analyses
    
    def _extract_existing_markers(self, marker_str: str) -> List[str]:
        """Extract existing markers from decorator string."""
        markers = []
        if marker_str:
            for match in re.finditer(r'@pytest\.mark\.(\w+)', marker_str):
                markers.append(match.group(1))
        return markers
    
    def _analyze_test(
        self,
        file_path: Path,
        test_name: str,
        content: str,
        existing_markers: List[str],
        is_class: bool = False
    ) -> TestAnalysis:
        """Analyze a single test."""
        
        # Quick wins: check filename
        if file_path.name in self.DEFINITE_E2E:
            return TestAnalysis(
                file_path=file_path,
                test_name=test_name,
                existing_markers=existing_markers,
                uses_mock=False,
                uses_real_connection=True,
                is_class=is_class,
                recommended_marker='e2e',
                reasoning=f"File {file_path.name} is definitively E2E"
            )
        
        if file_path.name in self.DEFINITE_UNIT:
            return TestAnalysis(
                file_path=file_path,
                test_name=test_name,
                existing_markers=existing_markers,
                uses_mock=False,
                uses_real_connection=False,
                is_class=is_class,
                recommended_marker='unit',
                reasoning=f"File {file_path.name} is definitively UNIT"
            )
        
        # Extract test block (simplified)
        if is_class:
            pattern = rf'class {test_name}\(.*?\):'
        else:
            pattern = rf'def {test_name}\('
        
        match = re.search(pattern, content)
        if not match:
            return TestAnalysis(
                file_path=file_path,
                test_name=test_name,
                existing_markers=existing_markers,
                uses_mock=False,
                uses_real_connection=False,
                is_class=is_class,
                recommended_marker='unit',
                reasoning="Could not find test definition"
            )
        
        # Extract test body (next ~2000 chars or until next def/class)
        start = match.start()
        remaining = content[start:]
        next_def = re.search(r'\n\s*(def|class) ', remaining[100:])
        end = start + (next_def.start() + 100 if next_def else len(remaining))
        test_body = remaining[:end - start]
        
        # Check for mock usage
        mock_count = sum(len(re.findall(pattern, test_body)) for pattern in self.MOCK_PATTERNS)
        uses_mock = mock_count > 0
        
        # Check for real connections
        real_count = sum(len(re.findall(pattern, test_body)) for pattern in self.REAL_CONNECTION_PATTERNS)
        uses_real_connection = real_count > 0
        
        # Recommend marker
        if uses_real_connection and not uses_mock:
            marker = 'e2e'
            reasoning = "Uses real connections (playwright, requests, asyncio, etc.) without mocks"
        elif uses_mock and not uses_real_connection:
            marker = 'unit'
            reasoning = "Uses only mocks, no real system connections"
        elif uses_mock and uses_real_connection:
            marker = 'integration'
            reasoning = "Mixes mock and real connections (integration test)"
        else:
            marker = 'integration'
            reasoning = "No clear mock/real pattern detected, defaulting to integration"
        
        return TestAnalysis(
            file_path=file_path,
            test_name=test_name,
            existing_markers=existing_markers,
            uses_mock=uses_mock,
            uses_real_connection=uses_real_connection,
            is_class=is_class,
            recommended_marker=marker,
            reasoning=reasoning
        )
    
    def print_summary(self):
        """Print classification summary."""
        unit = [a for a in self.results if a.recommended_marker == 'unit']
        integration = [a for a in self.results if a.recommended_marker == 'integration']
        e2e = [a for a in self.results if a.recommended_marker == 'e2e']
        
        print("\n" + "="*70)
        print("MARKER ASSIGNMENT SUMMARY")
        print("="*70)
        
        print(f"\nTOTAL TESTS: {len(self.results)}")
        print(f"  Unit Tests (@pytest.mark.unit): {len(unit)} ({100*len(unit)//len(self.results)}%)")
        print(f"  Integration Tests (@pytest.mark.integration): {len(integration)} ({100*len(integration)//len(self.results)}%)")
        print(f"  E2E Tests (@pytest.mark.e2e): {len(e2e)} ({100*len(e2e)//len(self.results)}%)")
        
        print(f"\nBY FILE:")
        files_by_count = {}
        for analysis in self.results:
            file_name = analysis.file_path.name
            if file_name not in files_by_count:
                files_by_count[file_name] = {'unit': 0, 'integration': 0, 'e2e': 0}
            files_by_count[file_name][analysis.recommended_marker] += 1
        
        for file_name in sorted(files_by_count.keys()):
            counts = files_by_count[file_name]
            total = sum(counts.values())
            summary = f"  {file_name}: {total} tests "
            parts = []
            if counts['unit'] > 0:
                parts.append(f"unit={counts['unit']}")
            if counts['integration'] > 0:
                parts.append(f"integration={counts['integration']}")
            if counts['e2e'] > 0:
                parts.append(f"e2e={counts['e2e']}")
            print(summary + "(" + ", ".join(parts) + ")")
        
        print("\n" + "="*70)
    
    def print_recommendations(self, limit: int = 20):
        """Print sample of recommendations."""
        print("\n" + "="*70)
        print("SAMPLE RECOMMENDATIONS (first 20)")
        print("="*70)
        
        for analysis in self.results[:limit]:
            marker_emoji = {
                'unit': '🔲',
                'integration': '🔗',
                'e2e': '🚀'
            }.get(analysis.recommended_marker, '?')
            
            print(f"\n{marker_emoji} {analysis.test_name}")
            print(f"   File: {analysis.file_path.name}")
            print(f"   Recommended: @pytest.mark.{analysis.recommended_marker}")
            print(f"   Reasoning: {analysis.reasoning}")
            print(f"   Mock: {'Yes' if analysis.uses_mock else 'No'} | Real: {'Yes' if analysis.uses_real_connection else 'No'}")


def main():
    """Run marker assignment."""
    root = Path(__file__).parent
    
    assigner = MarkerAssigner()
    
    print("🔍 SCANNING ALL TEST FILES...")
    print("="*70)
    
    # Scan both test directories
    assigner.scan_all_tests(root / "tests")
    
    # Also scan WARBLER tests
    warbler_tests = root / "packages/com.twg.the-seed/The Living Dev Agent/tests"
    if warbler_tests.exists():
        assigner.scan_all_tests(warbler_tests)
    
    # Print results
    assigner.print_summary()
    assigner.print_recommendations()
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print("\nNEXT STEP:")
    print("  python apply_test_markers.py")
    print("\nThis will ADD @pytest.mark decorators to all test files.")


if __name__ == "__main__":
    main()