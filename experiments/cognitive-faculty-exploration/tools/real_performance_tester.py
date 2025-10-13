#!/usr/bin/env python3
"""
Real Performance Testing for Cognitive Faculty Exploration

This module performs actual measurements on real system components rather than simulations.
"""

import os
import sys
import json
import time
import gc
import tracemalloc
from typing import Dict, List, Any, Tuple

class RealPerformanceTester:
    """Performs actual performance measurements on system components."""
    
    def __init__(self, output_dir: str = "real_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = {}
        
    def test_python_import_performance(self) -> Dict[str, Any]:
        """Test actual import performance of system modules."""
        print("🧠📊 Testing Python Import Performance...")
        
        modules_to_test = [
            "json",
            "os", 
            "sys",
            "time",
            "typing"
        ]
        
        import_results = {
            "test_name": "python_import_performance",
            "description": "Actual timing of Python module imports",
            "measurements": [],
            "timestamp": time.time()
        }
        
        for module_name in modules_to_test:
            # Measure import time
            start_time = time.perf_counter()
            try:
                __import__(module_name)
                end_time = time.perf_counter()
                import_time = end_time - start_time
                success = True
                error = None
            except ImportError as e:
                end_time = time.perf_counter()
                import_time = end_time - start_time
                success = False
                error = str(e)
            
            measurement = {
                "module": module_name,
                "import_time_seconds": import_time,
                "success": success,
                "error": error
            }
            
            import_results["measurements"].append(measurement)
            print(f"  📦 {module_name}: {import_time*1000:.2f}ms {'✅' if success else '❌'}")
        
        return import_results
    
    def test_file_io_performance(self) -> Dict[str, Any]:
        """Test actual file I/O performance."""
        print("🧠💾 Testing File I/O Performance...")
        
        test_data = "x" * 1000  # 1KB test data
        test_file = os.path.join(self.output_dir, "io_test.tmp")
        
        io_results = {
            "test_name": "file_io_performance", 
            "description": "Actual file I/O timing measurements",
            "measurements": [],
            "timestamp": time.time()
        }
        
        # Test write performance
        start_time = time.perf_counter()
        with open(test_file, 'w') as f:
            f.write(test_data)
        write_time = time.perf_counter() - start_time
        
        # Test read performance  
        start_time = time.perf_counter()
        with open(test_file, 'r') as f:
            read_data = f.read()
        read_time = time.perf_counter() - start_time
        
        # Verify data integrity
        data_match = read_data == test_data
        
        measurements = [
            {"operation": "write", "time_seconds": write_time, "data_size_bytes": len(test_data)},
            {"operation": "read", "time_seconds": read_time, "data_size_bytes": len(read_data)},
            {"operation": "verify", "success": data_match, "data_match": data_match}
        ]
        
        io_results["measurements"] = measurements
        
        for measurement in measurements:
            if "time_seconds" in measurement:
                print(f"  📁 {measurement['operation']}: {measurement['time_seconds']*1000:.3f}ms")
            else:
                print(f"  📁 {measurement['operation']}: {'✅' if measurement['success'] else '❌'}")
        
        # Cleanup
        os.remove(test_file)
        
        return io_results
    
    def test_memory_usage_pattern(self) -> Dict[str, Any]:
        """Test actual memory usage patterns."""
        print("🧠🔢 Testing Memory Usage Patterns...")
        
        memory_results = {
            "test_name": "memory_usage_pattern",
            "description": "Actual memory consumption measurements using tracemalloc",
            "measurements": [],
            "timestamp": time.time()
        }
        
        # Start memory tracing
        tracemalloc.start()
        
        # Baseline memory
        baseline_current, baseline_peak = tracemalloc.get_traced_memory()
        baseline_memory = baseline_current / 1024 / 1024  # MB
        
        measurements = [{"phase": "baseline", "memory_mb": baseline_memory}]
        
        # Allocate memory in steps
        data_arrays = []
        for i in range(5):
            # Allocate data
            data_arrays.append([0] * (1024 * 100))  # ~100KB per step
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            current_memory_mb = current_memory / 1024 / 1024
            measurements.append({
                "phase": f"allocation_step_{i+1}",
                "memory_mb": current_memory_mb,
                "memory_increase_mb": current_memory_mb - baseline_memory
            })
            print(f"  📊 Step {i+1}: {current_memory_mb:.2f}MB (+{current_memory_mb - baseline_memory:.2f}MB)")
        
        # Clear memory and force garbage collection
        data_arrays.clear()
        gc.collect()
        final_current, final_peak = tracemalloc.get_traced_memory()
        final_memory = final_current / 1024 / 1024
        measurements.append({
            "phase": "after_cleanup",
            "memory_mb": final_memory,
            "memory_difference_from_baseline": final_memory - baseline_memory
        })
        
        tracemalloc.stop()
        
        memory_results["measurements"] = measurements
        print(f"  📊 Final: {final_memory:.2f}MB (baseline: {baseline_memory:.2f}MB)")
        
        return memory_results
    
    def test_json_processing_performance(self) -> Dict[str, Any]:
        """Test actual JSON processing performance."""
        print("🧠🔧 Testing JSON Processing Performance...")
        
        # Create test data of various sizes
        test_cases = [
            {"name": "small", "data": {"key": "value", "number": 42}},
            {"name": "medium", "data": {"items": [{"id": i, "value": f"item_{i}"} for i in range(100)]}},
            {"name": "large", "data": {"matrix": [[j for j in range(50)] for i in range(50)]}}
        ]
        
        json_results = {
            "test_name": "json_processing_performance",
            "description": "Actual JSON serialization/deserialization timing",
            "measurements": [],
            "timestamp": time.time()
        }
        
        for test_case in test_cases:
            data = test_case["data"]
            
            # Test serialization
            start_time = time.perf_counter()
            json_str = json.dumps(data)
            serialize_time = time.perf_counter() - start_time
            
            # Test deserialization
            start_time = time.perf_counter()
            parsed_data = json.loads(json_str)
            deserialize_time = time.perf_counter() - start_time
            
            # Verify data integrity
            data_match = parsed_data == data
            
            measurement = {
                "test_case": test_case["name"],
                "json_size_bytes": len(json_str),
                "serialize_time_seconds": serialize_time,
                "deserialize_time_seconds": deserialize_time,
                "total_time_seconds": serialize_time + deserialize_time,
                "data_integrity": data_match
            }
            
            json_results["measurements"].append(measurement)
            print(f"  🔧 {test_case['name']}: {len(json_str)} bytes, {(serialize_time + deserialize_time)*1000:.3f}ms total")
        
        return json_results
    
    def run_comprehensive_performance_suite(self) -> Dict[str, Any]:
        """Run complete performance test suite and generate report."""
        print("🧠🚀 Running Comprehensive Performance Test Suite...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        all_results = {
            "suite_info": {
                "name": "Comprehensive Performance Test Suite",
                "description": "Actual performance measurements of system components",
                "start_time": start_time,
                "python_version": sys.version,
                "platform": sys.platform
            },
            "test_results": {}
        }
        
        # Execute tests
        all_results["test_results"]["import_performance"] = self.test_python_import_performance()
        all_results["test_results"]["file_io_performance"] = self.test_file_io_performance()
        all_results["test_results"]["memory_usage"] = self.test_memory_usage_pattern()
        all_results["test_results"]["json_processing"] = self.test_json_processing_performance()
        
        end_time = time.time()
        all_results["suite_info"]["end_time"] = end_time
        all_results["suite_info"]["total_duration"] = end_time - start_time
        
        # Generate summary statistics
        all_results["summary"] = self._generate_performance_summary(all_results["test_results"])
        
        # Save results
        timestamp = int(time.time())
        results_file = os.path.join(self.output_dir, f"real_performance_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🧠✅ Performance Testing Complete!")
        print(f"📊 Total Duration: {all_results['suite_info']['total_duration']:.3f} seconds")
        print(f"📄 Results saved to: {results_file}")
        
        # Generate visual charts
        self._generate_performance_charts(all_results["test_results"])
        
        return all_results
    
    def _generate_performance_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        summary = {
            "total_tests_run": 0,
            "performance_metrics": {},
            "system_characteristics": {}
        }
        
        # Count total tests
        for test_category, results in test_results.items():
            if "measurements" in results:
                summary["total_tests_run"] += len(results["measurements"])
        
        # Extract key metrics
        if "import_performance" in test_results:
            import_times = [m["import_time_seconds"] for m in test_results["import_performance"]["measurements"] if m["success"]]
            if import_times:
                summary["performance_metrics"]["average_import_time_ms"] = sum(import_times) / len(import_times) * 1000
                summary["performance_metrics"]["max_import_time_ms"] = max(import_times) * 1000
            else:
                summary["performance_metrics"]["average_import_time_ms"] = 0
                summary["performance_metrics"]["max_import_time_ms"] = 0
        
        if "file_io_performance" in test_results:
            io_measurements = test_results["file_io_performance"]["measurements"]
            for m in io_measurements:
                if m["operation"] == "write":
                    summary["performance_metrics"]["file_write_time_ms"] = m["time_seconds"] * 1000
                elif m["operation"] == "read":
                    summary["performance_metrics"]["file_read_time_ms"] = m["time_seconds"] * 1000
        
        if "memory_usage" in test_results:
            memory_measurements = test_results["memory_usage"]["measurements"]
            baseline = None
            final = None
            for m in memory_measurements:
                if m["phase"] == "baseline":
                    baseline = m["memory_mb"]
                elif m["phase"] == "after_cleanup":
                    final = m["memory_mb"]
            
            if baseline is not None:
                summary["system_characteristics"]["baseline_memory_mb"] = baseline
                if final is not None:
                    summary["system_characteristics"]["memory_cleanup_efficiency"] = (final - baseline) / baseline * 100 if baseline > 0 else 0
        
        return summary
    
    def _generate_performance_charts(self, test_results: Dict[str, Any]) -> None:
        """Generate simple text-based charts of performance data."""
        try:
            # Simple text-based charts since matplotlib is not available
            charts_file = os.path.join(self.output_dir, "performance_charts.txt")
            
            with open(charts_file, 'w') as f:
                f.write("=== PERFORMANCE CHARTS ===\n\n")
                
                # Memory usage chart
                if "memory_usage" in test_results:
                    f.write("Memory Usage Pattern:\n")
                    memory_data = test_results["memory_usage"]["measurements"]
                    max_memory = max(m["memory_mb"] for m in memory_data)
                    
                    for m in memory_data:
                        bar_length = int((m["memory_mb"] / max_memory) * 40) if max_memory > 0 else 0
                        bar = "█" * bar_length + "░" * (40 - bar_length)
                        f.write(f"{m['phase']:<20} [{bar}] {m['memory_mb']:.2f}MB\n")
                    f.write("\n")
                
                # Import performance chart
                if "import_performance" in test_results:
                    f.write("Import Performance:\n")
                    import_data = [m for m in test_results["import_performance"]["measurements"] if m["success"]]
                    max_time = max(m["import_time_seconds"] for m in import_data) if import_data else 0
                    
                    for m in import_data:
                        bar_length = int((m["import_time_seconds"] / max_time) * 40) if max_time > 0 else 0
                        bar = "█" * bar_length + "░" * (40 - bar_length)
                        f.write(f"{m['module']:<15} [{bar}] {m['import_time_seconds']*1000:.3f}ms\n")
                    f.write("\n")
                
                # JSON processing chart
                if "json_processing" in test_results:
                    f.write("JSON Processing Performance:\n")
                    json_data = test_results["json_processing"]["measurements"]
                    max_time = max(m["total_time_seconds"] for m in json_data) if json_data else 0
                    
                    for m in json_data:
                        bar_length = int((m["total_time_seconds"] / max_time) * 40) if max_time > 0 else 0
                        bar = "█" * bar_length + "░" * (40 - bar_length)
                        f.write(f"{m['test_case']:<12} [{bar}] {m['total_time_seconds']*1000:.3f}ms ({m['json_size_bytes']} bytes)\n")
                    f.write("\n")
            
            print(f"📊 Performance charts saved to: {charts_file}")
                
        except Exception as e:
            print(f"📊 Chart generation failed: {e}")

if __name__ == "__main__":
    tester = RealPerformanceTester("experiments/cognitive-faculty-exploration/real_results")
    results = tester.run_comprehensive_performance_suite()