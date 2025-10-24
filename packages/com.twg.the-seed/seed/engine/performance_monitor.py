#!/usr/bin/env python3
"""
Performance Monitor for Bob Stress Testing

Real-time monitoring of API performance, bottlenecks, and system health
during high-volume Bob Skeptic stress testing.
"""

import time
import json
import psutil
import requests
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Real-time performance monitoring for Bob stress testing"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.monitoring = False
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 data points
        self.start_time = None

        # Performance counters
        self.query_times = deque(maxlen=100)
        self.error_count = 0
        self.success_count = 0
        self.bob_decisions = defaultdict(int)

        # System metrics
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)

    def start_monitoring(self):
        """Start background monitoring"""
        self.monitoring = True
        self.start_time = datetime.now()

        # Start monitoring threads
        self.system_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.api_thread = threading.Thread(target=self._monitor_api, daemon=True)

        self.system_thread.start()
        self.api_thread.start()

        logger.info("🔍 Performance monitoring started")

    def stop_monitoring(self):
        """Stop monitoring and generate report"""
        self.monitoring = False
        logger.info("⏹️ Performance monitoring stopped")
        return self.generate_report()

    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()

                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory_info.percent)

                time.sleep(1)
            except Exception as e:
                logger.error(f"System monitoring error: {e}")

    def _monitor_api(self):
        """Monitor API performance"""
        while self.monitoring:
            try:
                # Check API health
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()

                    metric = {
                        "timestamp": datetime.now().isoformat(),
                        "api_uptime": health_data.get("uptime", 0),
                        "total_queries": health_data.get("total_queries", 0),
                        "concurrent_queries": health_data.get("concurrent_queries", 0),
                        "errors": health_data.get("errors", 0),
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent
                    }

                    self.metrics_history.append(metric)

                time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logger.error(f"API monitoring error: {e}")
                time.sleep(5)

    def record_query(self, query_time: float, success: bool, bob_status: str = None):
        """Record query performance"""
        self.query_times.append(query_time)

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        if bob_status:
            self.bob_decisions[bob_status] += 1

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""

        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        # Calculate query statistics
        if self.query_times:
            avg_query_time = sum(self.query_times) / len(self.query_times)
            min_query_time = min(self.query_times)
            max_query_time = max(self.query_times)
        else:
            avg_query_time = min_query_time = max_query_time = 0

        # Calculate system statistics
        if self.cpu_history:
            avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
            max_cpu = max(self.cpu_history)
        else:
            avg_cpu = max_cpu = 0

        if self.memory_history:
            avg_memory = sum(self.memory_history) / len(self.memory_history)
            max_memory = max(self.memory_history)
        else:
            avg_memory = max_memory = 0

        # Calculate API statistics
        if self.metrics_history:
            latest_metrics = self.metrics_history[-1]
            total_queries = latest_metrics.get("total_queries", 0)
            api_errors = latest_metrics.get("errors", 0)
        else:
            total_queries = api_errors = 0

        # Bob analysis
        total_bob_decisions = sum(self.bob_decisions.values())
        bob_quarantine_rate = (self.bob_decisions.get("QUARANTINED", 0) / total_bob_decisions) if total_bob_decisions > 0 else 0

        report = {
            "monitoring_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "duration_seconds": duration,
                "duration_minutes": duration / 60
            },
            "query_performance": {
                "total_queries": self.success_count + self.error_count,
                "successful_queries": self.success_count,
                "failed_queries": self.error_count,
                "success_rate": self.success_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0,
                "avg_query_time_ms": avg_query_time * 1000,
                "min_query_time_ms": min_query_time * 1000,
                "max_query_time_ms": max_query_time * 1000,
                "queries_per_second": (self.success_count + self.error_count) / duration if duration > 0 else 0
            },
            "system_performance": {
                "avg_cpu_percent": avg_cpu,
                "max_cpu_percent": max_cpu,
                "avg_memory_percent": avg_memory,
                "max_memory_percent": max_memory
            },
            "api_performance": {
                "total_api_queries": total_queries,
                "api_errors": api_errors,
                "api_error_rate": api_errors / total_queries if total_queries > 0 else 0
            },
            "bob_analysis": {
                "total_decisions": total_bob_decisions,
                "decisions_breakdown": dict(self.bob_decisions),
                "quarantine_rate": bob_quarantine_rate
            },
            "bottlenecks": self._identify_bottlenecks()
        }

        return report

    def _identify_bottlenecks(self) -> List[str]:
        """Identify potential performance bottlenecks"""
        bottlenecks = []

        # Check CPU usage
        if self.cpu_history and max(self.cpu_history) > 90:
            bottlenecks.append("High CPU usage detected (>90%)")

        # Check memory usage
        if self.memory_history and max(self.memory_history) > 85:
            bottlenecks.append("High memory usage detected (>85%)")

        # Check query times
        if self.query_times and max(self.query_times) > 5.0:  # 5 seconds
            bottlenecks.append("Slow query responses detected (>5s)")

        # Check error rates
        total_queries = self.success_count + self.error_count
        if total_queries > 0 and (self.error_count / total_queries) > 0.1:  # 10% error rate
            bottlenecks.append("High query error rate detected (>10%)")

        # Check Bob quarantine rate
        total_bob_decisions = sum(self.bob_decisions.values())
        if total_bob_decisions > 0:
            quarantine_rate = self.bob_decisions.get("QUARANTINED", 0) / total_bob_decisions
            if quarantine_rate > 0.2:  # 20% quarantine rate
                bottlenecks.append("High Bob quarantine rate detected (>20%)")

        return bottlenecks

    def print_live_stats(self):
        """Print current performance statistics"""
        if not self.metrics_history:
            print("📊 No metrics available yet")
            return

        latest = self.metrics_history[-1]
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        print(f"\n📊 Live Performance Stats (Running {duration:.1f}s)")
        print("=" * 60)
        print(f"Queries: {self.success_count + self.error_count} (Success: {self.success_count}, Errors: {self.error_count})")
        print(f"API Total: {latest.get('total_queries', 0)}, API Errors: {latest.get('errors', 0)}")
        print(f"CPU: {latest.get('cpu_percent', 0):.1f}%, Memory: {latest.get('memory_percent', 0):.1f}%")

        if self.query_times:
            avg_time = sum(self.query_times) / len(self.query_times) * 1000
            print(f"Avg Query Time: {avg_time:.2f}ms")

        if self.bob_decisions:
            total_bob = sum(self.bob_decisions.values())
            print(f"Bob Decisions: {total_bob} (Quarantined: {self.bob_decisions.get('QUARANTINED', 0)})")

        bottlenecks = self._identify_bottlenecks()
        if bottlenecks:
            print(f"⚠️ Bottlenecks: {', '.join(bottlenecks)}")
        else:
            print("✅ No bottlenecks detected")


def main():
    """Main entry point for performance monitoring"""

    import argparse

    parser = argparse.ArgumentParser(description="Performance Monitor for Bob Stress Testing")
    parser.add_argument("--duration", "-d", type=int, default=10, help="Monitoring duration in minutes")
    parser.add_argument("--api-url", "-u", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")

    args = parser.parse_args()

    monitor = PerformanceMonitor(api_url=args.api_url)

    try:
        print(f"🔍 Starting performance monitoring for {args.duration} minutes...")
        monitor.start_monitoring()

        # Monitor for specified duration
        start_time = time.time()
        while time.time() - start_time < args.duration * 60:
            monitor.print_live_stats()
            time.sleep(10)  # Update every 10 seconds

        # Stop monitoring and generate report
        report = monitor.stop_monitoring()

        print(f"\n📊 Final Performance Report")
        print("=" * 60)

        print(f"\n🎯 Query Performance:")
        print(f"   Total Queries: {report['query_performance']['total_queries']}")
        print(f"   Success Rate: {report['query_performance']['success_rate']:.2%}")
        print(f"   QPS: {report['query_performance']['queries_per_second']:.2f}")
        print(f"   Avg Query Time: {report['query_performance']['avg_query_time_ms']:.2f}ms")

        print(f"\n💻 System Performance:")
        print(f"   Avg CPU: {report['system_performance']['avg_cpu_percent']:.1f}%")
        print(f"   Max CPU: {report['system_performance']['max_cpu_percent']:.1f}%")
        print(f"   Avg Memory: {report['system_performance']['avg_memory_percent']:.1f}%")
        print(f"   Max Memory: {report['system_performance']['max_memory_percent']:.1f}%")

        print(f"\n🔍 Bob Analysis:")
        print(f"   Total Decisions: {report['bob_analysis']['total_decisions']}")
        print(f"   Quarantine Rate: {report['bob_analysis']['quarantine_rate']:.2%}")

        if report['bottlenecks']:
            print(f"\n⚠️ Bottlenecks Detected:")
            for bottleneck in report['bottlenecks']:
                print(f"   • {bottleneck}")
        else:
            print(f"\n✅ No bottlenecks detected")

        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {args.output}")

    except KeyboardInterrupt:
        print("\n⏹️ Monitoring interrupted by user")
        report = monitor.stop_monitoring()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {args.output}")

    except Exception as e:
        print(f"\n💥 Monitoring failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
