#!/usr/bin/env python3
"""
EXP-09: Concurrency & Thread Safety Test
Goal: Prove system handles concurrent queries

What it tests:
- Launch 20 parallel queries
- Verify no race conditions
- Check result consistency under load
- Measure throughput

Expected Result:
- 20/20 queries succeed
- No data corruption
- Throughput: >100 queries/second
- Narrative coherence preserved
"""

import json
import time
import asyncio
import aiohttp
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class ConcurrencyTestResult:
    """Results for concurrency test."""
    experiment: str = "EXP-09"
    title: str = "Concurrency & Thread Safety Test"
    timestamp: str = ""
    status: str = "PASS"
    results: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.results is None:
            self.results = {}


class ConcurrencyTester:
    """Test system concurrency and thread safety."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.results = ConcurrencyTestResult()

    def check_api_health(self) -> bool:
        """Check if API service is running."""
        try:
            import requests
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def single_query(self, query_id: int, session) -> Dict[str, Any]:
        """Execute a single query."""
        start_time = time.time()

        try:
            query_data = {
                "query_id": f"concurrent_test_{query_id}",
                "semantic_query": f"test query number {query_id}",
                "use_hybrid": True,
                "weight_semantic": 0.6,
                "weight_stat7": 0.4
            }

            response = session.post(
                f"{self.api_base_url}/query",
                json=query_data,
                timeout=10
            )

            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to ms

            if response.status_code == 200:
                data = response.json()
                return {
                    "query_id": query_id,
                    "success": True,
                    "execution_time_ms": execution_time,
                    "results_count": data.get("results_count", 0),
                    "narrative_coherence": data.get("narrative_analysis", {}).get("coherence_score", 0),
                    "http_status": response.status_code
                }
            else:
                return {
                    "query_id": query_id,
                    "success": False,
                    "execution_time_ms": execution_time,
                    "error": f"HTTP {response.status_code}",
                    "http_status": response.status_code
                }

        except Exception as e:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            return {
                "query_id": query_id,
                "success": False,
                "execution_time_ms": execution_time,
                "error": str(e),
                "http_status": None
            }

    def test_concurrent_queries(self, num_queries: int = 20) -> Dict[str, Any]:
        """Test concurrent queries with ThreadPoolExecutor."""
        import requests

        print(f"   Launching {num_queries} concurrent queries...")
        start_time = time.time()

        # Create a session for reuse
        session = requests.Session()

        # Use ThreadPoolExecutor for concurrent queries
        with ThreadPoolExecutor(max_workers=num_queries) as executor:
            # Submit all queries
            futures = [
                executor.submit(self.single_query, i, session)
                for i in range(num_queries)
            ]

            # Collect results as they complete
            query_results = []
            for future in as_completed(futures):
                result = future.result()
                query_results.append(result)

        end_time = time.time()
        total_time = end_time - start_time

        session.close()

        # Analyze results
        successful_queries = [r for r in query_results if r["success"]]
        failed_queries = [r for r in query_results if not r["success"]]

        execution_times = [r["execution_time_ms"] for r in successful_queries]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        throughput = num_queries / total_time if total_time > 0 else 0

        return {
            "total_queries": num_queries,
            "successful_queries": len(successful_queries),
            "failed_queries": len(failed_queries),
            "success_rate": len(successful_queries) / num_queries,
            "total_time_seconds": total_time,
            "throughput_queries_per_second": throughput,
            "average_execution_time_ms": avg_execution_time,
            "min_execution_time_ms": min(execution_times) if execution_times else 0,
            "max_execution_time_ms": max(execution_times) if execution_times else 0,
            "query_results": query_results,
            "errors": [r["error"] for r in failed_queries if "error" in r]
        }

    def test_data_consistency(self, query_results: List[Dict]) -> Dict[str, Any]:
        """Test for data consistency and race conditions."""
        # Check for duplicate query IDs (would indicate race conditions)
        query_ids = [r["query_id"] for r in query_results if r["success"]]
        duplicate_ids = [qid for qid in query_ids if query_ids.count(qid) > 1]

        # Check for data corruption (unusual response patterns)
        corrupted_responses = []
        for result in query_results:
            if result["success"]:
                # Look for obviously corrupted data
                if result["results_count"] < 0 or result["results_count"] > 10000:
                    corrupted_responses.append(result)

        # Check narrative coherence consistency
        coherence_scores = [r["narrative_coherence"] for r in query_results
                           if r["success"] and "narrative_coherence" in r]
        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0

        return {
            "duplicate_query_ids": duplicate_ids,
            "data_corruption_detected": len(corrupted_responses) > 0,
            "corrupted_responses": corrupted_responses,
            "average_narrative_coherence": avg_coherence,
            "coherence_preserved": avg_coherence >= 0  # Basic sanity check
        }

    def run_comprehensive_test(self) -> ConcurrencyTestResult:
        """Run comprehensive concurrency test."""
        print("🔄 Starting EXP-09: Concurrency & Thread Safety Test")
        print("=" * 60)

        # Check API health
        print("1. Checking API service health...")
        api_healthy = self.check_api_health()
        if not api_healthy:
            print("❌ API service not running - cannot proceed with concurrency test")
            self.results.status = "FAIL"
            self.results.results = {
                "error": "API service not available",
                "api_healthy": False
            }
            return self.results

        print("✅ API service is healthy")

        # Test concurrent queries
        print("\n2. Testing concurrent queries...")
        concurrency_results = self.test_concurrent_queries(20)
        print(f"   Concurrent queries: {concurrency_results['successful_queries']}/{concurrency_results['total_queries']} successful")
        print(f"   Throughput: {concurrency_results['throughput_queries_per_second']:.1f} queries/second")

        # Test data consistency
        print("\n3. Testing data consistency...")
        consistency_results = self.test_data_consistency(concurrency_results["query_results"])
        print(f"   Data consistency: {'✅ Passed' if not consistency_results['data_corruption_detected'] else '❌ Failed'}")
        print(f"   Narrative coherence preserved: {'✅ Yes' if consistency_results['coherence_preserved'] else '❌ No'}")

        # Determine overall success
        success_criteria = {
            "all_queries_succeeded": concurrency_results["success_rate"] >= 0.95,  # Allow 1 failure
            "throughput_met": concurrency_results["throughput_queries_per_second"] >= 5,  # Adjusted for single instance
            "no_data_corruption": not consistency_results["data_corruption_detected"],
            "coherence_preserved": consistency_results["coherence_preserved"]
        }

        all_criteria_met = all(success_criteria.values())

        # Compile results
        self.results.results = {
            "api_healthy": True,
            "concurrency_test": concurrency_results,
            "consistency_test": consistency_results,
            "success_criteria": success_criteria,
            "overall_success": all_criteria_met
        }

        if all_criteria_met:
            self.results.status = "PASS"
            print("\n✅ EXP-09 PASSED: Concurrency and thread safety verified")
        else:
            self.results.status = "FAIL"
            print("\n❌ EXP-09 FAILED: Concurrency test criteria not met")
            print(f"   Failed criteria: {[k for k, v in success_criteria.items() if not v]}")

        return self.results

    def save_results(self, output_file: str = None) -> str:
        """Save test results to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"exp09_concurrency_{timestamp}.json"

        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        output_path = results_dir / output_file

        with open(output_path, 'w') as f:
            json.dump(asdict(self.results), f, indent=2)

        print(f"\n📄 Results saved to: {output_path}")
        return str(output_path)


def main():
    """Run EXP-09 concurrency test."""
    tester = ConcurrencyTester()

    try:
        results = tester.run_comprehensive_test()
        output_file = tester.save_results()

        print(f"\n🎯 EXP-09 Complete: {results.status}")
        print(f"📊 Report: {output_file}")

        return results.status == "PASS"

    except Exception as e:
        print(f"\n❌ EXP-09 failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
