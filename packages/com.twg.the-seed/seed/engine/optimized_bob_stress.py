#!/usr/bin/env python3
"""
Hardware-Optimized Bob Stress Test for i7-6700/32GB/RTX 2060 SUPER

Optimized stress testing configuration based on system capabilities:
- 8 CPU threads (4 cores + hyperthreading)
- 32GB RAM (plenty of headroom)
- RTX 2060 SUPER (8GB VRAM for ML workloads)
- SSD storage (fast I/O)
"""

import asyncio
import json
import time
import random
import statistics
import psutil
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

class OptimizedBobStressConfig:
    """Hardware-optimized configuration for i7-6700/32GB/RTX 2060 SUPER"""

    # Hardware-based optimization
    CPU_CORES = 4  # i7-6700 has 4 physical cores
    CPU_THREADS = 8  # With hyperthreading
    RAM_GB = 32  # Available RAM
    VRAM_GB = 8  # RTX 2060 SUPER

    # Optimized test parameters
    MAX_CONCURRENT_QUERIES = 6  # Slightly under CPU thread count for headroom
    QUERIES_PER_SECOND_TARGET = 8  # Conservative but sustainable rate
    TEST_DURATION_MINUTES = 15  # Extended test for meaningful results
    QUERY_TIMEOUT_SECONDS = 30  # Generous timeout for complex queries

    # Memory management
    MAX_MEMORY_USAGE_PERCENT = 75  # Leave headroom for system
    BATCH_SIZE = 50  # Process queries in batches
    GC_INTERVAL_SECONDS = 60  # Garbage collection interval

    # Bob thresholds (tuned for high-volume testing)
    BOB_COHERENCE_HIGH = 0.85
    BOB_ENTANGLEMENT_LOW = 0.30
    BOB_CONSISTENCY_THRESHOLD = 0.85

class CitySimulationQueryGenerator:
    """Generates realistic city simulation queries for stress testing"""

    def __init__(self):
        # City districts and locations
        self.districts = [
            "Crystal Spire District", "Shadow Market Quarter", "Sun Temple Heights",
            "Moon Harbor Docks", "Star Forge Industrial", "Dream Weavers Enclave",
            "Time Keepers Plaza", "Memory Palace Gardens", "Echo Gardens",
            "Quantum Core Station", "Neon Street Market", "Sky Docks Terminal"
        ]

        # NPC archetypes with varied behaviors
        self.npc_archetypes = {
            "merchant": {
                "names": ["Silas", "Marina", "Gideon", "Lyra", "Orion"],
                "activities": ["trading", "negotiating", "appraising", "haggling", "shipping"],
                "concerns": ["profits", "reputation", "supplies", "competition", "regulations"]
            },
            "guard": {
                "names": ["Marcus", "Valeria", "Rex", "Aria", "Kai"],
                "activities": ["patrolling", "investigating", "guarding", "training", "reporting"],
                "concerns": ["security", "threats", "evidence", "procedures", "citizens"]
            },
            "scholar": {
                "names": ["Elena", "Sofia", "Dante", "Iris", "Phoenix"],
                "activities": ["researching", "teaching", "writing", "translating", "archiving"],
                "concerns": ["knowledge", "accuracy", "discoveries", "students", "resources"]
            },
            "artisan": {
                "names": ["Finn", "Maya", "Leo", "Celeste", "Ember"],
                "activities": ["crafting", "designing", "repairing", "innovating", "selling"],
                "concerns": ["materials", "techniques", "inspiration", "quality", "customers"]
            },
            "mystic": {
                "names": ["Luna", "Zara", "Atlas", "Nova", "Echo"],
                "activities": ["meditating", "divining", "healing", "consulting", "rituals"],
                "concerns": ["energies", "visions", "balance", "spirits", "prophecies"]
            }
        }

        # Time periods for temporal queries
        self.time_periods = [
            "dawn", "morning", "midday", "afternoon", "dusk", "evening", "midnight", "late night"
        ]

        # Weather and environmental conditions
        self.conditions = [
            "clear skies", "light rain", "heavy storm", "foggy", "windy", "snow", "heatwave", "cold snap"
        ]

        # Social dynamics
        self.relationships = [
            "friendship", "rivalry", "romance", "family", "mentorship", "partnership", "conflict", "alliance"
        ]

    def generate_city_query(self) -> Dict[str, Any]:
        """Generate a realistic city simulation query"""

        # Select random elements
        district = random.choice(self.districts)
        archetype = random.choice(list(self.npc_archetypes.keys()))
        npc_data = self.npc_archetypes[archetype]
        npc_name = random.choice(npc_data["names"])
        activity = random.choice(npc_data["activities"])
        concern = random.choice(npc_data["concerns"])
        time_period = random.choice(self.time_periods)
        condition = random.choice(self.conditions)
        relationship = random.choice(self.relationships)

        # Query templates based on complexity
        query_templates = [
            # Simple character queries
            f"How does {npc_name} the {archetype} handle {concern} during {activity} in {district}?",

            # Location-based queries
            f"What patterns emerge in {district} during {time_period} when {condition} affects {archetype}s?",

            # Social dynamics queries
            f"How does {relationship} between {npc_name} and others influence their {activity} in {district}?",

            # Temporal queries
            f"Describe how {npc_name}'s approach to {concern} changes from {time_period} to evening in {district}.",

            # Environmental impact queries
            f"How does {condition} in {district} affect {archetype}s performing {activity} and their {concern}?",

            # Complex multi-factor queries
            f"When {npc_name} is engaged in {activity} during {time_period} in {district} under {condition}, how does their {relationship} status impact their handling of {concern}?",

            # Narrative progression queries
            f"Trace the development of {npc_name}'s {concern} throughout a typical day in {district}, including key {activity} sessions and {relationship} interactions.",

            # System-level queries
            f"What systemic patterns emerge when analyzing {archetype}s' responses to {concern} across all districts during {condition}?"
        ]

        # Select query complexity based on probability
        complexity_roll = random.random()
        if complexity_roll < 0.3:  # 30% simple
            query_text = query_templates[0]
            query_type = "simple_character"
        elif complexity_roll < 0.6:  # 30% location-based
            query_text = random.choice(query_templates[1:3])
            query_type = "location_based"
        elif complexity_roll < 0.8:  # 20% temporal
            query_text = random.choice(query_templates[3:5])
            query_type = "temporal"
        else:  # 20% complex
            query_text = random.choice(query_templates[5:])
            query_type = "complex_system"

        return {
            "query_id": f"city_{int(time.time() * 1000)}_{random.randint(10000, 99999)}",
            "semantic": query_text,
            "query_type": query_type,
            "npc_name": npc_name,
            "archetype": archetype,
            "district": district,
            "activity": activity,
            "concern": concern,
            "time_period": time_period,
            "condition": condition,
            "relationship": relationship,
            "complexity_score": complexity_roll,
            "hybrid": random.choice([True, False]),
            "weight_semantic": random.uniform(0.6, 0.8),
            "weight_stat7": random.uniform(0.2, 0.4)
        }

class OptimizedBobStressTester:
    """Hardware-optimized stress tester for Bob the Skeptic"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.config = OptimizedBobStressConfig()
        self.query_generator = CitySimulationQueryGenerator()
        self.results = []
        self.start_time = None
        self.end_time = None

        # Performance tracking
        self.query_times = []
        self.bob_verdicts = {"PASSED": 0, "VERIFIED": 0, "QUARANTINED": 0}
        self.error_count = 0
        self.queries_per_second_actual = 0

        # Hardware monitoring
        self.cpu_usage_history = []
        self.memory_usage_history = []

        # Rate limiting
        self.query_interval = 1.0 / self.config.QUERIES_PER_SECOND_TARGET

    async def single_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single query with hardware monitoring"""

        start_time = time.time()

        # Monitor hardware before query
        cpu_before = psutil.cpu_percent(interval=None)
        memory_before = psutil.virtual_memory().percent

        try:
            # Prepare query data for POST request
            query_request = {
                "query_id": query_data["query_id"],
                "semantic_query": query_data["semantic"],
                "mode": "semantic_similarity",
                "max_results": 10,
                "confidence_threshold": 0.6,
                "stat7_hybrid": query_data["hybrid"],
                "weight_semantic": query_data["weight_semantic"],
                "weight_stat7": query_data["weight_stat7"]
            }

            # Execute query with timeout (POST request)
            response = requests.post(
                f"{self.api_base_url}/query",
                json=query_request,
                timeout=self.config.QUERY_TIMEOUT_SECONDS
            )

            query_time = time.time() - start_time

            # Monitor hardware after query
            cpu_after = psutil.cpu_percent(interval=None)
            memory_after = psutil.virtual_memory().percent

            self.cpu_usage_history.append((cpu_before + cpu_after) / 2)
            self.memory_usage_history.append((memory_before + memory_after) / 2)

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
                    "complexity_score": query_data["complexity_score"],
                    "query_time": query_time,
                    "bob_status": bob_status,
                    "result_count": len(result.get("results", [])),
                    "npc_name": query_data["npc_name"],
                    "archetype": query_data["archetype"],
                    "district": query_data["district"],
                    "cpu_usage": (cpu_before + cpu_after) / 2,
                    "memory_usage": (memory_before + memory_after) / 2,
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
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "query_time": time.time() - start_time,
                    "cpu_usage": (cpu_before + cpu_after) / 2,
                    "memory_usage": (memory_before + memory_after) / 2
                }

        except Exception as e:
            self.error_count += 1
            return {
                "timestamp": datetime.now().isoformat(),
                "query_id": query_data["query_id"],
                "error": str(e),
                "query_time": time.time() - start_time,
                "cpu_usage": (cpu_before + cpu_after) / 2,
                "memory_usage": (memory_before + memory_after) / 2
            }

    async def query_worker(self, worker_id: int, duration_seconds: int):
        """Optimized worker with hardware-aware rate limiting"""

        end_time = time.time() + duration_seconds
        queries_executed = 0
        last_gc_time = time.time()

        logger.info(f"Worker {worker_id} started (hardware-optimized)")

        while time.time() < end_time:
            # Check memory usage and throttle if needed
            current_memory = psutil.virtual_memory().percent
            if current_memory > self.config.MAX_MEMORY_USAGE_PERCENT:
                logger.warning(f"High memory usage ({current_memory:.1f}%), throttling queries")
                await asyncio.sleep(2)
                continue

            # Generate query
            query_data = self.query_generator.generate_city_query()

            # Execute query
            result = await self.single_query(query_data)
            self.results.append(result)
            queries_executed += 1

            # Hardware-aware rate limiting
            avg_cpu = np.mean(self.cpu_usage_history[-10:]) if self.cpu_usage_history else 0
            if avg_cpu > 80:  # High CPU usage
                await asyncio.sleep(self.query_interval * 1.5)  # Slow down
            else:
                await asyncio.sleep(self.query_interval)

            # Periodic garbage collection
            if time.time() - last_gc_time > self.config.GC_INTERVAL_SECONDS:
                import gc
                gc.collect()
                last_gc_time = time.time()

            # Progress reporting
            if queries_executed % 20 == 0:
                logger.info(f"Worker {worker_id}: {queries_executed} queries completed")

        logger.info(f"Worker {worker_id} completed {queries_executed} queries")

    async def run_optimized_stress_test(self, duration_minutes: int = None) -> Dict[str, Any]:
        """Run hardware-optimized stress test"""

        duration_minutes = duration_minutes or self.config.TEST_DURATION_MINUTES
        duration_seconds = duration_minutes * 60

        logger.info(f"🚀 Starting Hardware-Optimized Bob Stress Test")
        logger.info(f"   Hardware: i7-6700/32GB/RTX 2060 SUPER")
        logger.info(f"   Duration: {duration_minutes} minutes")
        logger.info(f"   Target QPS: {self.config.QUERIES_PER_SECOND_TARGET}")
        logger.info(f"   Max Concurrent: {self.config.MAX_CONCURRENT_QUERIES}")
        logger.info(f"   Memory Limit: {self.config.MAX_MEMORY_USAGE_PERCENT}%")
        logger.info(f"   API Endpoint: {self.api_base_url}")

        self.start_time = datetime.now()

        # Start optimized concurrent workers
        tasks = []
        for i in range(self.config.MAX_CONCURRENT_QUERIES):
            task = asyncio.create_task(self.query_worker(i, duration_seconds))
            tasks.append(task)

        # Wait for all workers to complete
        await asyncio.gather(*tasks)

        self.end_time = datetime.now()

        # Generate comprehensive report
        return self.generate_optimized_report()

    def generate_optimized_report(self) -> Dict[str, Any]:
        """Generate hardware-optimized stress test report"""

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

        # Hardware metrics
        avg_cpu = np.mean(self.cpu_usage_history) if self.cpu_usage_history else 0
        max_cpu = np.max(self.cpu_usage_history) if self.cpu_usage_history else 0
        avg_memory = np.mean(self.memory_usage_history) if self.memory_usage_history else 0
        max_memory = np.max(self.memory_usage_history) if self.memory_usage_history else 0

        # Bob analysis
        total_bob_decisions = sum(self.bob_verdicts.values())
        bob_alert_rate = (self.bob_verdicts["VERIFIED"] + self.bob_verdicts["QUARANTINED"]) / total_bob_decisions if total_bob_decisions > 0 else 0
        bob_quarantine_rate = self.bob_verdicts["QUARANTINED"] / total_bob_decisions if total_bob_decisions > 0 else 0

        # Query type analysis
        query_type_stats = {}
        complexity_stats = {"simple": 0, "moderate": 0, "complex": 0}

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

            # Complexity analysis
            complexity = result.get("complexity_score", 0)
            if complexity < 0.3:
                complexity_stats["simple"] += 1
            elif complexity < 0.8:
                complexity_stats["moderate"] += 1
            else:
                complexity_stats["complex"] += 1

        report = {
            "test_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_seconds": total_duration,
                "duration_minutes": total_duration / 60,
                "hardware_profile": "i7-6700/32GB/RTX 2060 SUPER"
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
            "hardware_metrics": {
                "avg_cpu_percent": avg_cpu,
                "max_cpu_percent": max_cpu,
                "avg_memory_percent": avg_memory,
                "max_memory_percent": max_memory,
                "memory_efficiency": "OPTIMAL" if max_memory < self.config.MAX_MEMORY_USAGE_PERCENT else "THROTTLED"
            },
            "bob_analysis": {
                "total_decisions": total_bob_decisions,
                "passed": self.bob_verdicts["PASSED"],
                "verified": self.bob_verdicts["VERIFIED"],
                "quarantined": self.bob_verdicts["QUARANTINED"],
                "alert_rate": bob_alert_rate,
                "quarantine_rate": bob_quarantine_rate
            },
            "query_analysis": {
                "query_type_breakdown": query_type_stats,
                "complexity_breakdown": complexity_stats
            },
            "hardware_optimization": {
                "cpu_utilization": "EFFICIENT" if avg_cpu < 70 else "HIGH",
                "memory_management": "GOOD" if max_memory < self.config.MAX_MEMORY_USAGE_PERCENT else "NEEDS_TUNING",
                "concurrency_optimal": self.config.MAX_CONCURRENT_QUERIES <= self.config.CPU_THREADS
            },
            "detailed_results": self.results[-50:]  # Last 50 results for analysis
        }

        # Save report
        report_file = Path(__file__).parent / "results" / f"optimized_bob_stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True, parents=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Optimized stress test report saved: {report_file}")

        return report

async def main():
    """Main entry point for hardware-optimized Bob stress testing"""

    import argparse

    parser = argparse.ArgumentParser(description="Hardware-Optimized Bob Stress Test")
    parser.add_argument("--duration", "-d", type=int, default=15, help="Test duration in minutes")
    parser.add_argument("--qps", "-q", type=int, default=8, help="Target queries per second")
    parser.add_argument("--concurrent", "-c", type=int, default=6, help="Maximum concurrent queries")
    parser.add_argument("--api-url", "-u", default="http://localhost:8000", help="API base URL")

    args = parser.parse_args()

    # Configure optimized stress tester
    tester = OptimizedBobStressTester(api_base_url=args.api_url)
    tester.config.TEST_DURATION_MINUTES = args.duration
    tester.config.QUERIES_PER_SECOND_TARGET = args.qps
    tester.config.MAX_CONCURRENT_QUERIES = args.concurrent

    try:
        # Run optimized stress test
        report = await tester.run_optimized_stress_test()

        # Print comprehensive results
        print("\n" + "="*80)
        print("🎯 HARDWARE-OPTIMIZED BOB STRESS TEST RESULTS")
        print("="*80)

        print(f"\n💻 Hardware Profile: {report['test_summary']['hardware_profile']}")
        print(f"⏱️ Duration: {report['test_summary']['duration_minutes']:.1f} minutes")

        print(f"\n📊 Volume Metrics:")
        print(f"   Total Queries: {report['volume_metrics']['total_queries']:,}")
        print(f"   Success Rate: {report['volume_metrics']['success_rate']:.2%}")
        print(f"   QPS Target: {report['volume_metrics']['queries_per_second_target']}")
        print(f"   QPS Actual: {report['volume_metrics']['queries_per_second_actual']:.2f}")

        print(f"\n⚡ Performance Metrics:")
        print(f"   Avg Query Time: {report['performance_metrics']['avg_query_time_ms']:.2f}ms")
        print(f"   P95 Query Time: {report['performance_metrics']['p95_query_time_ms']:.2f}ms")
        print(f"   P99 Query Time: {report['performance_metrics']['p99_query_time_ms']:.2f}ms")

        print(f"\n💻 Hardware Utilization:")
        print(f"   Avg CPU: {report['hardware_metrics']['avg_cpu_percent']:.1f}% (Max: {report['hardware_metrics']['max_cpu_percent']:.1f}%)")
        print(f"   Avg Memory: {report['hardware_metrics']['avg_memory_percent']:.1f}% (Max: {report['hardware_metrics']['max_memory_percent']:.1f}%)")
        print(f"   Memory Efficiency: {report['hardware_metrics']['memory_efficiency']}")

        print(f"\n🔍 Bob Analysis:")
        print(f"   Total Decisions: {report['bob_analysis']['total_decisions']:,}")
        print(f"   Passed: {report['bob_analysis']['passed']:,}")
        print(f"   Verified: {report['bob_analysis']['verified']:,}")
        print(f"   Quarantined: {report['bob_analysis']['quarantined']:,}")
        print(f"   Alert Rate: {report['bob_analysis']['alert_rate']:.2%}")
        print(f"   Quarantine Rate: {report['bob_analysis']['quarantine_rate']:.2%}")

        print(f"\n📈 Query Complexity:")
        complexity = report['query_analysis']['complexity_breakdown']
        print(f"   Simple: {complexity['simple']:,} ({complexity['simple']/sum(complexity.values()):.1%})")
        print(f"   Moderate: {complexity['moderate']:,} ({complexity['moderate']/sum(complexity.values()):.1%})")
        print(f"   Complex: {complexity['complex']:,} ({complexity['complex']/sum(complexity.values()):.1%})")

        print(f"\n🔧 Hardware Optimization:")
        print(f"   CPU Utilization: {report['hardware_optimization']['cpu_utilization']}")
        print(f"   Memory Management: {report['hardware_optimization']['memory_management']}")
        print(f"   Concurrency Optimal: {report['hardware_optimization']['concurrency_optimal']}")

        # Overall assessment
        print(f"\n🏥 Overall System Health:")
        health_score = 0
        if report['volume_metrics']['success_rate'] > 0.95:
            print("   ✅ Query Success Rate: EXCELLENT")
            health_score += 1
        else:
            print("   ⚠️ Query Success Rate: NEEDS ATTENTION")

        if report['performance_metrics']['p95_query_time_ms'] < 2000:
            print("   ✅ Query Latency: EXCELLENT")
            health_score += 1
        else:
            print("   ⚠️ Query Latency: DEGRADED")

        if report['hardware_metrics']['max_memory_percent'] < 80:
            print("   ✅ Memory Usage: OPTIMAL")
            health_score += 1
        else:
            print("   ⚠️ Memory Usage: HIGH")

        if 0.01 <= report['bob_analysis']['quarantine_rate'] <= 0.15:
            print("   ✅ Bob Performance: OPTIMAL")
            health_score += 1
        else:
            print("   ⚠️ Bob Performance: NEEDS TUNING")

        if health_score >= 4:
            print(f"\n🎉 SYSTEM HEALTH: EXCELLENT ({health_score}/5)")
            print("🚀 Your system is ready for production-scale city simulation!")
        elif health_score >= 3:
            print(f"\n✅ SYSTEM HEALTH: GOOD ({health_score}/5)")
            print("🔧 Minor optimizations may improve performance")
        else:
            print(f"\n⚠️ SYSTEM HEALTH: NEEDS ATTENTION ({health_score}/5)")
            print("🛠️ Consider reducing load or optimizing configuration")

        print("\n" + "="*80)

    except KeyboardInterrupt:
        print("\n⏹️ Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Stress test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
