#!/usr/bin/env python3
"""
Bob Skeptic High-Volume Stress Test Framework

Stress tests Bob the Skeptic with prolonged, high-volume queries
to simulate real-world city simulation with thousands of active NPCs.
"""

import asyncio
import json
import time
import random
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BobStressTestConfig:
    """Configuration for stress testing"""

    # Test duration and volume
    TEST_DURATION_MINUTES = 30  # Extended stress test duration
    QUERIES_PER_SECOND_TARGET = 10  # Target query rate
    MAX_CONCURRENT_QUERIES = 50  # Maximum concurrent queries

    # Query patterns
    QUERY_TYPES = [
        "npc_character_development",
        "narrative_consistency",
        "world_building",
        "character_relationships",
        "plot_progression",
        "emotional_states",
        "memory_consolidation",
        "behavioral_patterns"
    ]

    # Bob thresholds (can be tuned)
    BOB_COHERENCE_HIGH = 0.85
    BOB_ENTANGLEMENT_LOW = 0.30
    BOB_CONSISTENCY_THRESHOLD = 0.85

class NPCQueryGenerator:
    """Generates realistic NPC queries for stress testing"""

    def __init__(self):
        self.npc_names = [
            "Elena", "Marcus", "Sofia", "James", "Aria", "Kai", "Luna", "Orion",
            "Zara", "Finn", "Maya", "Leo", "Iris", "Rex", "Nova", "Echo"
        ]

        self.locations = [
            "Crystal Spire", "Shadow Market", "Sun Temple", "Moon Harbor",
            "Star Forge", "Dream Weavers", "Time Keepers", "Memory Palace"
        ]

        self.emotions = [
            "joyful", "melancholy", "determined", "conflicted", "hopeful",
            "anxious", "peaceful", "restless", "curious", "wary"
        ]

        self.activities = [
            "crafting", "exploring", "meditating", "negotiating", "celebrating",
            "mourning", "learning", "teaching", "defending", "healing"
        ]

    def generate_query(self, query_type: str) -> Dict[str, Any]:
        """Generate a realistic NPC query"""

        npc = random.choice(self.npc_names)
        location = random.choice(self.locations)
        emotion = random.choice(self.emotions)
        activity = random.choice(self.activities)

        queries = {
            "npc_character_development": f"How does {npc}'s {emotion} state affect their {activity} at {location}?",
            "narrative_consistency": f"What patterns emerge from {npc}'s behavior across multiple visits to {location}?",
            "world_building": f"How does {location} influence the {emotion} experiences of visitors like {npc}?",
            "character_relationships": f"Describe the evolving relationship between {npc} and others during {activity} sessions",
            "plot_progression": f"What narrative developments occur when {npc} engages in {activity} while feeling {emotion}?",
            "emotional_states": f"Trace the emotional journey of {npc} from {emotion} to other states during {activity}",
            "memory_consolidation": f"How does {npc} consolidate memories of {activity} experiences at {location}?",
            "behavioral_patterns": f"What behavioral patterns does {npc} exhibit when {emotion} during {activity} at {location}?"
        }

        return {
            "query_id": f"stress_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            "semantic": queries.get(query_type, queries["npc_character_development"]),
            "query_type": query_type,
            "npc": npc,
            "location": location,
            "emotion": emotion,
            "activity": activity,
            "hybrid": random.choice([True, False]),
            "weight_semantic": random.uniform(0.5, 0.8),
            "weight_stat7": random.uniform(0.2, 0.5)
        }

class BobStressTester:
    """Main stress testing framework for Bob the Skeptic"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.config = BobStressTestConfig()
        self.query_generator = NPCQueryGenerator()
        self.results = []
        self.start_time = None
        self.end_time = None

        # Performance tracking
        self.query_times = []
        self.bob_verdicts = {"PASSED": 0, "VERIFIED": 0, "QUARANTINED": 0}
        self.error_count = 0
        self.queries_per_second_actual = 0

    async def single_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single query and track Bob's response"""

        start_time = time.time()

        try:
            # Prepare query parameters
            params = {
                "query-id": query_data["query_id"],
                "semantic": query_data["semantic"]
            }

            if query_data["hybrid"]:
                params.update({
                    "hybrid": True,
                    "weight-semantic": query_data["weight_semantic"],
                    "weight-stat7": query_data["weight_stat7"]
                })

            # Execute query
            response = requests.get(
                f"{self.api_base_url}/query",
                params=params,
                timeout=30
            )

            query_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                # Track Bob's verdict
                bob_status = result.get("bob_status", "UNKNOWN")
                self.bob_verdicts[bob_status] = self.bob_verdicts.get(bob_status, 0) + 1

                # Store detailed result
                query_result = {
                    "timestamp": datetime.now().isoformat(),
                    "query_id": query_data["query_id"],
                    "query_type": query_data["query_type"],
                    "query_time": query_time,
                    "bob_status": bob_status,
                    "result_count": len(result.get("results", [])),
                    "npc": query_data["npc"],
                    "location": query_data["location"],
                    "emotion": query_data["emotion"],
                    "activity": query_data["activity"],
                    "hybrid": query_data["hybrid"],
                    "coherence": result.get("coherence", 0),
                    "entanglement": result.get("entanglement", 0),
                    "bob_verification_log": result.get("bob_verification_log")
                }

                self.query_times.append(query_time)
                return query_result

            else:
                self.error_count += 1
                return {
                    "timestamp": datetime.now().isoformat(),
                    "query_id": query_data["query_id"],
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query_time": time.time() - start_time
                }

        except Exception as e:
            self.error_count += 1
            return {
                "timestamp": datetime.now().isoformat(),
                "query_id": query_data["query_id"],
                "error": str(e),
                "query_time": time.time() - start_time
            }

    async def query_worker(self, worker_id: int, duration_seconds: int):
        """Worker that continuously generates and executes queries"""

        end_time = time.time() + duration_seconds
        queries_executed = 0

        logger.info(f"Worker {worker_id} started")

        while time.time() < end_time:
            # Generate query
            query_type = random.choice(self.config.QUERY_TYPES)
            query_data = self.query_generator.generate_query(query_type)

            # Execute query
            result = await self.single_query(query_data)
            self.results.append(result)
            queries_executed += 1

            # Rate limiting to achieve target QPS
            if queries_executed % 10 == 0:
                avg_time = statistics.mean(self.query_times[-10:]) if self.query_times else 0.1
                target_interval = 1.0 / (self.config.QUERIES_PER_SECOND_TARGET / self.config.MAX_CONCURRENT_QUERIES)
                sleep_time = max(0, target_interval - avg_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        logger.info(f"Worker {worker_id} completed {queries_executed} queries")

    async def run_stress_test(self, duration_minutes: int = None) -> Dict[str, Any]:
        """Run the complete stress test"""

        duration_minutes = duration_minutes or self.config.TEST_DURATION_MINUTES
        duration_seconds = duration_minutes * 60

        logger.info(f"🚀 Starting Bob Stress Test")
        logger.info(f"   Duration: {duration_minutes} minutes")
        logger.info(f"   Target QPS: {self.config.QUERIES_PER_SECOND_TARGET}")
        logger.info(f"   Max Concurrent: {self.config.MAX_CONCURRENT_QUERIES}")
        logger.info(f"   API Endpoint: {self.api_base_url}")

        self.start_time = datetime.now()

        # Start concurrent workers
        tasks = []
        for i in range(self.config.MAX_CONCURRENT_QUERIES):
            task = asyncio.create_task(self.query_worker(i, duration_seconds))
            tasks.append(task)

        # Wait for all workers to complete
        await asyncio.gather(*tasks)

        self.end_time = datetime.now()

        # Calculate final metrics
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive stress test report"""

        total_duration = (self.end_time - self.start_time).total_seconds()
        total_queries = len(self.results)
        successful_queries = len([r for r in self.results if "error" not in r])

        # Calculate QPS
        self.queries_per_second_actual = total_queries / total_duration if total_duration > 0 else 0

        # Performance metrics
        if self.query_times:
            avg_query_time = statistics.mean(self.query_times)
            median_query_time = statistics.median(self.query_times)
            p95_query_time = np.percentile(self.query_times, 95)
            p99_query_time = np.percentile(self.query_times, 99)
        else:
            avg_query_time = median_query_time = p95_query_time = p99_query_time = 0

        # Bob analysis
        total_bob_decisions = sum(self.bob_verdicts.values())
        bob_alert_rate = (self.bob_verdicts["VERIFIED"] + self.bob_verdicts["QUARANTINED"]) / total_bob_decisions if total_bob_decisions > 0 else 0
        bob_quarantine_rate = self.bob_verdicts["QUARANTINED"] / total_bob_decisions if total_bob_decisions > 0 else 0

        # Query type analysis
        query_type_stats = {}
        for result in self.results:
            if "query_type" in result:
                qtype = result["query_type"]
                if qtype not in query_type_stats:
                    query_type_stats[qtype] = {"total": 0, "errors": 0, "quarantined": 0}
                query_type_stats[qtype]["total"] += 1
                if "error" in result:
                    query_type_stats[qtype]["errors"] += 1
                if result.get("bob_status") == "QUARANTINED":
                    query_type_stats[qtype]["quarantined"] += 1

        report = {
            "test_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_seconds": total_duration,
                "duration_minutes": total_duration / 60
            },
            "volume_metrics": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": self.error_count,
                "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
                "queries_per_second_target": self.config.QUERIES_PER_SECOND_TARGET,
                "queries_per_second_actual": self.queries_per_second_actual
            },
            "performance_metrics": {
                "avg_query_time_ms": avg_query_time * 1000,
                "median_query_time_ms": median_query_time * 1000,
                "p95_query_time_ms": p95_query_time * 1000,
                "p99_query_time_ms": p99_query_time * 1000
            },
            "bob_analysis": {
                "total_decisions": total_bob_decisions,
                "passed": self.bob_verdicts["PASSED"],
                "verified": self.bob_verdicts["VERIFIED"],
                "quarantined": self.bob_verdicts["QUARANTINED"],
                "alert_rate": bob_alert_rate,
                "quarantine_rate": bob_quarantine_rate
            },
            "query_type_analysis": query_type_stats,
            "detailed_results": self.results[-100:]  # Last 100 results for detailed analysis
        }

        # Save report
        report_file = Path(__file__).parent / "results" / f"bob_stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True, parents=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Stress test report saved: {report_file}")

        return report

async def main():
    """Main entry point for Bob stress testing"""

    import argparse

    parser = argparse.ArgumentParser(description="Bob Skeptic Stress Test Framework")
    parser.add_argument("--duration", "-d", type=int, default=30, help="Test duration in minutes")
    parser.add_argument("--qps", "-q", type=int, default=10, help="Target queries per second")
    parser.add_argument("--concurrent", "-c", type=int, default=50, help="Maximum concurrent queries")
    parser.add_argument("--api-url", "-u", default="http://localhost:8000", help="API base URL")

    args = parser.parse_args()

    # Configure stress tester
    tester = BobStressTester(api_base_url=args.api_url)
    tester.config.TEST_DURATION_MINUTES = args.duration
    tester.config.QUERIES_PER_SECOND_TARGET = args.qps
    tester.config.MAX_CONCURRENT_QUERIES = args.concurrent

    try:
        # Run stress test
        report = await tester.run_stress_test()

        # Print summary
        print("\n" + "="*80)
        print("🎯 BOB STRESS TEST RESULTS")
        print("="*80)

        print(f"\n📊 Volume Metrics:")
        print(f"   Total Queries: {report['volume_metrics']['total_queries']:,}")
        print(f"   Success Rate: {report['volume_metrics']['success_rate']:.2%}")
        print(f"   QPS Target: {report['volume_metrics']['queries_per_second_target']}")
        print(f"   QPS Actual: {report['volume_metrics']['queries_per_second_actual']:.2f}")

        print(f"\n⚡ Performance Metrics:")
        print(f"   Avg Query Time: {report['performance_metrics']['avg_query_time_ms']:.2f}ms")
        print(f"   P95 Query Time: {report['performance_metrics']['p95_query_time_ms']:.2f}ms")
        print(f"   P99 Query Time: {report['performance_metrics']['p99_query_time_ms']:.2f}ms")

        print(f"\n🔍 Bob Analysis:")
        print(f"   Total Decisions: {report['bob_analysis']['total_decisions']:,}")
        print(f"   Passed: {report['bob_analysis']['passed']:,}")
        print(f"   Verified: {report['bob_analysis']['verified']:,}")
        print(f"   Quarantined: {report['bob_analysis']['quarantined']:,}")
        print(f"   Alert Rate: {report['bob_analysis']['alert_rate']:.2%}")
        print(f"   Quarantine Rate: {report['bob_analysis']['quarantine_rate']:.2%}")

        # Health assessment
        print(f"\n🏥 System Health Assessment:")
        if report['volume_metrics']['success_rate'] > 0.95:
            print("   ✅ Query Success Rate: HEALTHY")
        else:
            print("   ❌ Query Success Rate: DEGRADED")

        if report['performance_metrics']['p95_query_time_ms'] < 1000:
            print("   ✅ Query Latency: HEALTHY")
        else:
            print("   ⚠️ Query Latency: DEGRADED")

        if 0.01 <= report['bob_analysis']['quarantine_rate'] <= 0.10:
            print("   ✅ Bob Quarantine Rate: OPTIMAL")
        elif report['bob_analysis']['quarantine_rate'] > 0.10:
            print("   ⚠️ Bob Quarantine Rate: HIGH (may need tuning)")
        else:
            print("   ⚠️ Bob Quarantine Rate: LOW (may be missing issues)")

        print("\n" + "="*80)

    except KeyboardInterrupt:
        print("\n⏹️ Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Stress test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
