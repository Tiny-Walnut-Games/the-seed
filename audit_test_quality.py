#!/usr/bin/env python3
"""
TEST AUDIT TOOL: Categorize tests by quality and mock usage.

This tool identifies which tests are:
- Real (connect to actual systems)
- Mock-based (use fake data)
- Mixed (some real, some mock)

Helps determine what's ready for release and what needs work.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict


@dataclass
class TestInfo:
    """Information about a single test."""
    file_path: str
    test_name: str
    is_marked: bool  # Has @pytest.mark.* decorator
    mark_type: str  # unit, integration, e2e, load, etc.
    uses_mock: bool  # Uses Mock(), patch(), mock objects
    uses_real_connection: bool  # Connects to actual server/db
    description: str
    quality_score: float  # 0-10 (10 = real, no mocks)


class TestAuditor:
    """Audit test files for real vs mock usage."""
    
    # Patterns to detect
    MOCK_PATTERNS = [
        r'Mock\(',
        r'@mock\.',
        r'patch\(',
        r'MagicMock',
        r'PropertyMock',
        r'call\(',
        r'unittest\.mock',
        r'from unittest.mock',
        r'Mock\w+',  # MockEmbedding, MockSTAT7, etc.
    ]
    
    REAL_PATTERNS = [
        r'async_playwright',
        r'playwright\.async_api',
        r'browser\.goto',
        r'database\.query',
        r'\.connect\(',
        r'requests\.post',
        r'requests\.get',
        r'websocket',
        r'asyncio\.',
        r'start_server',
        r'serve',
        r'BaseHTTPServer',
    ]
    
    MARK_PATTERNS = {
        'unit': r'@pytest\.mark\.unit',
        'integration': r'@pytest\.mark\.integration',
        'e2e': r'@pytest\.mark\.e2e',
        'load': r'@pytest\.mark\.load',
        'stress': r'@pytest\.mark\.stress',
    }
    
    def __init__(self):
        self.results: List[TestInfo] = []
        self.stats = defaultdict(int)
    
    def scan_file(self, file_path: Path) -> List[TestInfo]:
        """Scan a test file and extract test info."""
        tests = []
        
        try:
            content = file_path.read_text(encoding='utf-8-sig')
        except Exception as e:
            print(f"  [ERROR] Cannot read {file_path}: {e}")
            return tests
        
        # Find all test functions and classes
        test_functions = re.findall(r'def (test_\w+)\(.*?\):', content)
        test_classes = re.findall(r'class (Test\w+)', content)
        
        for test_name in test_functions:
            test_info = self._analyze_test(content, test_name, file_path)
            tests.append(test_info)
        
        for test_class in test_classes:
            # For classes, mark as class-level test
            test_info = self._analyze_test(content, test_class, file_path, is_class=True)
            tests.append(test_info)
        
        return tests
    
    def _analyze_test(self, content: str, test_name: str, file_path: Path, is_class: bool = False) -> TestInfo:
        """Analyze a single test for mock/real patterns."""
        
        # Find test block (simplified - looks for decorators above test)
        pattern = rf'(@pytest\.mark\.\w+\s+)*def {test_name}\('
        match = re.search(pattern, content)
        
        if not match:
            pattern = rf'(class {test_name})'
            match = re.search(pattern, content)
        
        # Extract docstring if available
        docstring_pattern = rf'def {test_name}\(.*?\):\s*"""(.*?)"""'
        doc_match = re.search(docstring_pattern, content, re.DOTALL)
        description = doc_match.group(1).strip()[:100] if doc_match else ""
        
        # Check for pytest markers
        mark_type = "unmarked"
        is_marked = False
        for marker_name, marker_pattern in self.MARK_PATTERNS.items():
            if re.search(marker_pattern, content[:content.find(test_name) + 500]):
                mark_type = marker_name
                is_marked = True
                break
        
        # Count mock usage
        mock_count = sum(len(re.findall(pattern, content)) for pattern in self.MOCK_PATTERNS)
        uses_mock = mock_count > 0
        
        # Count real connection usage
        real_count = sum(len(re.findall(pattern, content)) for pattern in self.REAL_PATTERNS)
        uses_real_connection = real_count > 0
        
        # Calculate quality score
        quality_score = self._calculate_quality(is_marked, uses_mock, uses_real_connection)
        
        return TestInfo(
            file_path=str(file_path.relative_to(Path.cwd())),
            test_name=test_name,
            is_marked=is_marked,
            mark_type=mark_type,
            uses_mock=uses_mock,
            uses_real_connection=uses_real_connection,
            description=description,
            quality_score=quality_score
        )
    
    def _calculate_quality(self, is_marked: bool, uses_mock: bool, uses_real: bool) -> float:
        """Calculate quality score (0-10)."""
        score = 5.0  # Base score
        
        if is_marked:
            score += 2.0  # +2 for proper marking
        
        if uses_mock:
            score -= 2.0  # -2 for using mocks
        
        if uses_real:
            score += 2.0  # +2 for real connections
        
        return max(0.0, min(10.0, score))
    
    def audit_directory(self, test_dir: Path):
        """Audit all test files in a directory."""
        py_files = list(test_dir.rglob("test_*.py"))
        
        for py_file in py_files:
            tests = self.scan_file(py_file)
            self.results.extend(tests)
    
    def print_summary(self):
        """Print audit summary."""
        if not self.results:
            print("[INFO] No tests found")
            return
        
        # Categorize results
        unmarked = [t for t in self.results if t.mark_type == "unmarked"]
        unit = [t for t in self.results if t.mark_type == "unit"]
        integration = [t for t in self.results if t.mark_type == "integration"]
        e2e = [t for t in self.results if t.mark_type == "e2e"]
        
        only_mock = [t for t in self.results if t.uses_mock and not t.uses_real_connection]
        real_tests = [t for t in self.results if t.uses_real_connection]
        high_quality = [t for t in self.results if t.quality_score >= 8.0]
        
        print("\n" + "="*70)
        print("TEST AUDIT SUMMARY")
        print("="*70)
        
        print(f"\nTOTAL TESTS: {len(self.results)}")
        print(f"  [MARKED] {len([t for t in self.results if t.is_marked])}")
        print(f"  [UNMARKED] {len(unmarked)}")
        
        print(f"\nBY CATEGORY:")
        print(f"  Unit Tests: {len(unit)}")
        print(f"  Integration Tests: {len(integration)}")
        print(f"  E2E Tests: {len(e2e)}")
        print(f"  Other: {len([t for t in self.results if t.mark_type not in ['unit', 'integration', 'e2e']])}")
        
        print(f"\nQUALITY METRICS:")
        print(f"  Real Connection Tests: {len(real_tests)}")
        print(f"  Mock-Only Tests: {len(only_mock)}")
        print(f"  High Quality (≥8.0): {len(high_quality)}")
        
        avg_quality = sum(t.quality_score for t in self.results) / len(self.results)
        print(f"  Average Quality Score: {avg_quality:.1f}/10.0")
        
        print(f"\n⚠️ CONCERNS FOR RELEASE:")
        
        if unmarked:
            print(f"\n  [WARNING] {len(unmarked)} tests are UNMARKED (missing @pytest.mark)")
            print(f"    These need categorization:")
            for t in unmarked[:5]:
                print(f"      - {t.test_name} ({Path(t.file_path).name})")
            if len(unmarked) > 5:
                print(f"      ... and {len(unmarked) - 5} more")
        
        if only_mock:
            print(f"\n  [WARNING] {len(only_mock)} tests use ONLY mocks (no real connections)")
            print(f"    These must be UNIT tests, not E2E:")
            for t in only_mock[:5]:
                print(f"      - {t.test_name} ({t.mark_type})")
            if len(only_mock) > 5:
                print(f"      ... and {len(only_mock) - 5} more")
        
        e2e_with_mock = [t for t in e2e if t.uses_mock]
        if e2e_with_mock:
            print(f"\n  [ERROR] {len(e2e_with_mock)} E2E tests use MOCKS")
            print(f"    E2E tests must be 100% real for release:")
            for t in e2e_with_mock[:5]:
                print(f"      - {t.test_name}")
            if len(e2e_with_mock) > 5:
                print(f"      ... and {len(e2e_with_mock) - 5} more")
        
        print(f"\n✅ READY FOR RELEASE:")
        if high_quality:
            print(f"  {len(high_quality)} high-quality tests ready")
        else:
            print(f"  No high-quality tests yet")
        
        print("\n" + "="*70)
    
    def print_detailed_report(self, filter_type=None):
        """Print detailed report of all tests."""
        print("\n" + "="*70)
        print("DETAILED TEST REPORT")
        print("="*70)
        
        for result in sorted(self.results, key=lambda t: (-t.quality_score, t.file_path)):
            if filter_type and result.mark_type != filter_type:
                continue
            
            quality_emoji = "🟢" if result.quality_score >= 8 else "🟡" if result.quality_score >= 6 else "🔴"
            mark_emoji = "✓" if result.is_marked else "✗"
            mock_emoji = "🎭" if result.uses_mock else "✓"
            real_emoji = "🔌" if result.uses_real_connection else " "
            
            print(f"\n{quality_emoji} {result.test_name}")
            print(f"   File: {result.file_path}")
            print(f"   Mark: {mark_emoji} {result.mark_type}")
            print(f"   Mock: {mock_emoji}  Real: {real_emoji}")
            print(f"   Quality: {result.quality_score:.1f}/10.0")
            if result.description:
                print(f"   Note: {result.description[:60]}...")


def main():
    """Run audit."""
    root = Path(__file__).parent
    
    auditor = TestAuditor()
    
    # Audit both test directories
    print("[SCANNING] The Seed tests...")
    auditor.audit_directory(root / "tests")
    
    print("[SCANNING] WARBLER tests...")
    auditor.audit_directory(root / "packages/com.twg.the-seed/The Living Dev Agent/tests")
    
    # Print summary
    auditor.print_summary()
    
    # Print detailed report (first time)
    print("\nPrinting sample of detailed report...\n")
    auditor.print_detailed_report()
    
    print("\n✅ Audit complete. Review the summary above.")
    print("\nNEXT STEPS:")
    print("1. Mark all unmarked tests with @pytest.mark.{unit|integration|e2e|load}")
    print("2. Move mock-only tests to UNIT category")
    print("3. Remove mocks from E2E tests (replace with real server connections)")
    print("4. Run this audit again to verify improvements")


if __name__ == "__main__":
    main()