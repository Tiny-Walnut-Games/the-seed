#!/usr/bin/env python3
"""
Real System Component Testing for TWG-TLDA

Tests actual system components that exist in the repository.
"""

import os
import sys
import json
import time
import importlib.util
from typing import Dict, List, Any

class SystemComponentTester:
    """Tests actual system components in the TWG-TLDA repository."""
    
    def __init__(self, repo_root: str, output_dir: str = "system_test_results"):
        self.repo_root = repo_root
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = {}
    
    def discover_python_modules(self) -> List[Dict[str, str]]:
        """Discover actual Python modules in the repository."""
        print("🔍 Discovering Python modules in repository...")
        
        modules = []
        for root, dirs, files in os.walk(self.repo_root):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'build', 'dist']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_root)
                    module_info = {
                        "name": file[:-3],  # Remove .py extension
                        "path": rel_path,
                        "full_path": file_path,
                        "size_bytes": os.path.getsize(file_path)
                    }
                    modules.append(module_info)
        
        print(f"  📦 Found {len(modules)} Python files")
        return modules
    
    def test_file_parsing_performance(self, modules: List[Dict[str, str]]) -> Dict[str, Any]:
        """Test performance of parsing Python files."""
        print("🧠📖 Testing File Parsing Performance...")
        
        parsing_results = {
            "test_name": "file_parsing_performance",
            "description": "Actual timing of Python file parsing",
            "measurements": [],
            "timestamp": time.time()
        }
        
        # Test a sample of files (not all, to keep test reasonable)
        sample_modules = modules[:10] if len(modules) > 10 else modules
        
        for module in sample_modules:
            try:
                start_time = time.perf_counter()
                
                # Read the file
                with open(module["full_path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse as Python (compile check)
                try:
                    compile(content, module["full_path"], 'exec')
                    parse_success = True
                    parse_error = None
                except SyntaxError as e:
                    parse_success = False
                    parse_error = str(e)
                
                end_time = time.perf_counter()
                parsing_time = end_time - start_time
                
                measurement = {
                    "module_name": module["name"],
                    "file_path": module["path"],
                    "file_size_bytes": module["size_bytes"],
                    "parsing_time_seconds": parsing_time,
                    "lines_of_code": len(content.splitlines()),
                    "parse_success": parse_success,
                    "parse_error": parse_error
                }
                
                parsing_results["measurements"].append(measurement)
                status = "✅" if parse_success else "❌"
                print(f"  📖 {module['name']:<20} {module['size_bytes']:>6} bytes {parsing_time*1000:>6.2f}ms {status}")
                
            except Exception as e:
                measurement = {
                    "module_name": module["name"],
                    "file_path": module["path"],
                    "file_size_bytes": module["size_bytes"],
                    "parsing_time_seconds": 0,
                    "lines_of_code": 0,
                    "parse_success": False,
                    "parse_error": f"File access error: {str(e)}"
                }
                parsing_results["measurements"].append(measurement)
                print(f"  📖 {module['name']:<20} ERROR: {str(e)}")
        
        return parsing_results
    
    def test_directory_traversal_performance(self) -> Dict[str, Any]:
        """Test performance of directory traversal operations."""
        print("🧠📁 Testing Directory Traversal Performance...")
        
        traversal_results = {
            "test_name": "directory_traversal_performance",
            "description": "Actual timing of filesystem operations", 
            "measurements": [],
            "timestamp": time.time()
        }
        
        # Test different directory operations
        operations = [
            ("list_root", lambda: os.listdir(self.repo_root)),
            ("walk_tree", lambda: list(os.walk(self.repo_root))),
            ("stat_files", lambda: [os.stat(os.path.join(self.repo_root, f)) for f in os.listdir(self.repo_root) if os.path.isfile(os.path.join(self.repo_root, f))])
        ]
        
        for op_name, operation in operations:
            try:
                start_time = time.perf_counter()
                result = operation()
                end_time = time.perf_counter()
                
                operation_time = end_time - start_time
                result_count = len(result) if isinstance(result, list) else 1
                
                measurement = {
                    "operation": op_name,
                    "execution_time_seconds": operation_time,
                    "result_count": result_count,
                    "success": True,
                    "error": None
                }
                
                traversal_results["measurements"].append(measurement)
                print(f"  📁 {op_name:<15} {operation_time*1000:>8.2f}ms ({result_count} items)")
                
            except Exception as e:
                measurement = {
                    "operation": op_name,
                    "execution_time_seconds": 0,
                    "result_count": 0,
                    "success": False,
                    "error": str(e)
                }
                traversal_results["measurements"].append(measurement)
                print(f"  📁 {op_name:<15} ERROR: {str(e)}")
        
        return traversal_results
    
    def test_tldl_processing_performance(self) -> Dict[str, Any]:
        """Test performance of TLDL file processing."""
        print("🧠📜 Testing TLDL Processing Performance...")
        
        tldl_results = {
            "test_name": "tldl_processing_performance",
            "description": "Actual timing of TLDL file operations",
            "measurements": [],
            "timestamp": time.time()
        }
        
        tldl_dir = os.path.join(self.repo_root, "TLDL", "entries")
        
        if not os.path.exists(tldl_dir):
            tldl_results["error"] = "TLDL directory not found"
            return tldl_results
        
        try:
            # Count TLDL files
            start_time = time.perf_counter()
            tldl_files = [f for f in os.listdir(tldl_dir) if f.endswith('.md')]
            count_time = time.perf_counter() - start_time
            
            # Read and analyze a sample of TLDL files
            sample_files = tldl_files[:5] if len(tldl_files) > 5 else tldl_files
            total_size = 0
            total_lines = 0
            total_read_time = 0
            
            for tldl_file in sample_files:
                file_path = os.path.join(tldl_dir, tldl_file)
                
                start_time = time.perf_counter()
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                read_time = time.perf_counter() - start_time
                
                total_size += len(content)
                total_lines += len(content.splitlines())
                total_read_time += read_time
                
                print(f"  📜 {tldl_file:<40} {len(content):>6} chars {read_time*1000:>6.2f}ms")
            
            measurements = [
                {
                    "operation": "count_tldl_files",
                    "execution_time_seconds": count_time,
                    "file_count": len(tldl_files),
                    "success": True
                },
                {
                    "operation": "read_sample_tldl_files",
                    "execution_time_seconds": total_read_time,
                    "files_processed": len(sample_files),
                    "total_characters": total_size,
                    "total_lines": total_lines,
                    "average_read_time_ms": (total_read_time / len(sample_files) * 1000) if sample_files else 0,
                    "success": True
                }
            ]
            
            tldl_results["measurements"] = measurements
            print(f"  📜 Total TLDL files: {len(tldl_files)}")
            print(f"  📜 Sample processed: {len(sample_files)} files, {total_size} chars, {total_read_time*1000:.2f}ms")
            
        except Exception as e:
            tldl_results["error"] = str(e)
            print(f"  📜 ERROR: {str(e)}")
        
        return tldl_results
    
    def run_comprehensive_system_test(self) -> Dict[str, Any]:
        """Run comprehensive test of actual system components."""
        print("🧠🔧 Running Comprehensive System Component Test...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Discover system components
        modules = self.discover_python_modules()
        
        # Run all tests
        all_results = {
            "test_info": {
                "name": "TWG-TLDA System Component Performance Test",
                "description": "Actual performance measurements of real system components",
                "start_time": start_time,
                "repository_root": self.repo_root,
                "python_version": sys.version,
                "platform": sys.platform
            },
            "discovery": {
                "python_modules_found": len(modules),
                "sample_modules": modules[:5]  # First 5 as sample
            },
            "test_results": {}
        }
        
        # Execute tests
        all_results["test_results"]["file_parsing"] = self.test_file_parsing_performance(modules)
        all_results["test_results"]["directory_traversal"] = self.test_directory_traversal_performance()
        all_results["test_results"]["tldl_processing"] = self.test_tldl_processing_performance()
        
        end_time = time.time()
        all_results["test_info"]["end_time"] = end_time
        all_results["test_info"]["total_duration"] = end_time - start_time
        
        # Generate summary
        all_results["summary"] = self._generate_system_summary(all_results["test_results"], modules)
        
        # Save results
        timestamp = int(time.time())
        results_file = os.path.join(self.output_dir, f"system_component_test_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🧠✅ System Component Testing Complete!")
        print(f"📊 Total Duration: {all_results['test_info']['total_duration']:.3f} seconds")
        print(f"📦 Python Modules Found: {len(modules)}")
        print(f"📄 Results saved to: {results_file}")
        
        return all_results
    
    def _generate_system_summary(self, test_results: Dict[str, Any], modules: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate summary of system test results."""
        summary = {
            "repository_characteristics": {
                "total_python_files": len(modules),
                "total_python_size_bytes": sum(m["size_bytes"] for m in modules),
                "average_file_size_bytes": sum(m["size_bytes"] for m in modules) / len(modules) if modules else 0
            },
            "performance_characteristics": {},
            "system_health": {}
        }
        
        # File parsing analysis
        if "file_parsing" in test_results and "measurements" in test_results["file_parsing"]:
            parsing_data = test_results["file_parsing"]["measurements"]
            successful_parses = [m for m in parsing_data if m["parse_success"]]
            
            if successful_parses:
                summary["performance_characteristics"]["average_parse_time_ms"] = sum(m["parsing_time_seconds"] for m in successful_parses) / len(successful_parses) * 1000
                summary["performance_characteristics"]["max_parse_time_ms"] = max(m["parsing_time_seconds"] for m in successful_parses) * 1000
                summary["system_health"]["parse_success_rate"] = len(successful_parses) / len(parsing_data) * 100
        
        # Directory traversal analysis
        if "directory_traversal" in test_results and "measurements" in test_results["directory_traversal"]:
            traversal_data = test_results["directory_traversal"]["measurements"]
            successful_ops = [m for m in traversal_data if m["success"]]
            
            if successful_ops:
                summary["performance_characteristics"]["average_traversal_time_ms"] = sum(m["execution_time_seconds"] for m in successful_ops) / len(successful_ops) * 1000
        
        # TLDL processing analysis
        if "tldl_processing" in test_results and "measurements" in test_results["tldl_processing"]:
            tldl_data = test_results["tldl_processing"]["measurements"]
            read_ops = [m for m in tldl_data if m["operation"] == "read_sample_tldl_files"]
            
            if read_ops:
                summary["performance_characteristics"]["tldl_average_read_time_ms"] = read_ops[0].get("average_read_time_ms", 0)
                summary["repository_characteristics"]["tldl_files_found"] = next((m["file_count"] for m in tldl_data if m["operation"] == "count_tldl_files"), 0)
        
        return summary

if __name__ == "__main__":
    repo_root = os.path.abspath(".")
    output_dir = "experiments/cognitive-faculty-exploration/system_test_results"
    
    tester = SystemComponentTester(repo_root, output_dir)
    results = tester.run_comprehensive_system_test()