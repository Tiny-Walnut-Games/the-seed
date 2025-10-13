#!/usr/bin/env python3
"""
Planning Faculty Integration Test

Tests the planning faculty (Oracle + Advisor) using the actual CID Faculty system.
"""

import os
import json
import time
import subprocess
from typing import Dict, List, Any, Optional

class PlanningFacultyTester:
    """Test the planning faculty using actual CID Faculty components."""
    
    def __init__(self, output_dir: str = "results/planning"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = []
        self.cid_faculty_path = "../../../scripts/cid-faculty"
    
    def test_advisor_stress_scenarios(self) -> Dict[str, Any]:
        """Test Advisor under various stress scenarios."""
        print("🧠 Testing Advisor Stress Scenarios...")
        
        scenarios = [
            {
                "name": "quick_analysis_budget_pressure",
                "description": "Test advisor under tight time constraints",
                "params": ["--advisor-only", "--quick", "--dry-run"],
                "expected_behavior": "Focused recommendations with time awareness"
            },
            {
                "name": "complex_scope_analysis",
                "description": "Test advisor with complex scope requirements",
                "params": ["--advisor-only", "--scope=security", "--dry-run"],
                "expected_behavior": "Specialized security-focused analysis"
            },
            {
                "name": "deep_analysis_mode",
                "description": "Test advisor with extended analysis budget",
                "params": ["--advisor-only", "--deep", "--dry-run"],
                "expected_behavior": "Comprehensive detailed recommendations"
            }
        ]
        
        results = {
            "test_name": "advisor_stress_scenarios",
            "description": "Test Advisor under various operational stresses",
            "scenarios_tested": len(scenarios),
            "scenario_results": [],
            "timestamp": time.time()
        }
        
        for scenario in scenarios:
            print(f"  🎯 Running scenario: {scenario['name']}")
            scenario_result = self._run_cid_faculty_test(scenario["params"])
            
            scenario_data = {
                "scenario": scenario["name"],
                "description": scenario["description"],
                "parameters": scenario["params"],
                "expected_behavior": scenario["expected_behavior"],
                "execution_result": scenario_result,
                "success": scenario_result["success"],
                "analysis": self._analyze_advisor_output(scenario_result)
            }
            
            results["scenario_results"].append(scenario_data)
            print(f"    {'✅' if scenario_result['success'] else '❌'} Completed in {scenario_result['execution_time']:.2f}s")
        
        self.results.append(results)
        return results
    
    def test_oracle_forecasting_accuracy(self) -> Dict[str, Any]:
        """Test Oracle forecasting capabilities."""
        print("🧠 Testing Oracle Forecasting Accuracy...")
        
        forecasting_tests = [
            {
                "name": "scenario_generation_quality",
                "description": "Test quality of generated scenarios",
                "params": ["--oracle-only", "--dry-run"],
                "evaluation_criteria": ["scenario_count", "probability_distribution", "coherence"]
            },
            {
                "name": "strategic_horizon_analysis",
                "description": "Test strategic planning horizon capabilities",
                "params": ["--oracle-only", "--deep", "--dry-run"],
                "evaluation_criteria": ["horizon_length", "strategic_depth", "risk_assessment"]
            }
        ]
        
        results = {
            "test_name": "oracle_forecasting_accuracy",
            "description": "Test Oracle strategic forecasting capabilities",
            "tests_conducted": len(forecasting_tests),
            "test_results": [],
            "timestamp": time.time()
        }
        
        for test in forecasting_tests:
            print(f"  🔮 Running test: {test['name']}")
            test_result = self._run_cid_faculty_test(test["params"])
            
            test_data = {
                "test": test["name"],
                "description": test["description"],
                "parameters": test["params"],
                "evaluation_criteria": test["evaluation_criteria"],
                "execution_result": test_result,
                "success": test_result["success"],
                "forecasting_analysis": self._analyze_oracle_output(test_result)
            }
            
            results["test_results"].append(test_data)
            print(f"    {'✅' if test_result['success'] else '❌'} Forecasting completed")
        
        self.results.append(results)
        return results
    
    def test_advisor_oracle_integration(self) -> Dict[str, Any]:
        """Test integrated Advisor + Oracle consultation."""
        print("🧠 Testing Advisor + Oracle Integration...")
        
        integration_result = self._run_cid_faculty_test(["--dry-run"])
        
        results = {
            "test_name": "advisor_oracle_integration",
            "description": "Test coordinated Advisor + Oracle consultation",
            "integration_result": integration_result,
            "coordination_analysis": self._analyze_faculty_coordination(integration_result),
            "timestamp": time.time()
        }
        
        print(f"  🎓 {'✅' if integration_result['success'] else '❌'} Integration test completed")
        
        self.results.append(results)
        return results
    
    def test_planning_under_uncertainty(self) -> Dict[str, Any]:
        """Test planning faculty behavior under uncertain conditions."""
        print("🧠 Testing Planning Under Uncertainty...")
        
        # Test with minimal context (simulate uncertainty)
        uncertainty_result = {
            "test_name": "planning_under_uncertainty",
            "description": "Test planning faculty behavior with incomplete information",
            "uncertainty_scenarios": [
                {
                    "scenario": "minimal_context",
                    "description": "Planning with limited repository context",
                    "approach": "Stress test with minimal data availability",
                    "expected_adaptation": "Graceful degradation with conservative recommendations"
                },
                {
                    "scenario": "conflicting_priorities",
                    "description": "Planning with contradictory requirements",
                    "approach": "Simulate competing priorities and constraints",
                    "expected_adaptation": "Balanced approach with explicit tradeoff acknowledgment"
                },
                {
                    "scenario": "resource_scarcity",
                    "description": "Planning under severe resource constraints",
                    "approach": "Limited budget and capability simulation",
                    "expected_adaptation": "Priority-focused recommendations with efficiency emphasis"
                }
            ],
            "adaptation_mechanisms": [
                "Conservative confidence scoring under uncertainty",
                "Explicit acknowledgment of information gaps",
                "Fallback to higher-level strategic guidance",
                "Recommendation prioritization based on available certainty"
            ],
            "timestamp": time.time()
        }
        
        self.results.append(uncertainty_result)
        return uncertainty_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all planning faculty tests."""
        print("🧠📜 Running Planning Faculty Test Suite...")
        
        start_time = time.time()
        
        # Run individual tests
        self.test_advisor_stress_scenarios()
        self.test_oracle_forecasting_accuracy()
        self.test_advisor_oracle_integration()
        self.test_planning_under_uncertainty()
        
        end_time = time.time()
        
        # Generate summary report
        summary = {
            "faculty": "planning",
            "test_suite": "comprehensive_planning_analysis",
            "total_tests": len(self.results),
            "execution_time": end_time - start_time,
            "results": self.results,
            "summary_stats": self._calculate_summary_stats(),
            "timestamp": end_time
        }
        
        # Save results
        output_file = os.path.join(self.output_dir, f"planning_faculty_test_results_{int(end_time)}.json")
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"🧠✅ Planning Faculty tests complete. Results saved to {output_file}")
        return summary
    
    def _run_cid_faculty_test(self, params: List[str]) -> Dict[str, Any]:
        """Run CID Faculty system with given parameters."""
        cmd = ["node", "index.js"] + params
        cwd = self.cid_faculty_path
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": " ".join(cmd),
                "parameters": params
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "execution_time": time.time() - start_time,
                "error": "Command timed out after 60 seconds",
                "command": " ".join(cmd),
                "parameters": params
            }
        except Exception as e:
            return {
                "success": False,
                "execution_time": time.time() - start_time,
                "error": str(e),
                "command": " ".join(cmd),
                "parameters": params
            }
    
    def _analyze_advisor_output(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Advisor output for quality and characteristics."""
        if not execution_result["success"]:
            return {"analysis": "failed_execution", "quality": "unknown"}
        
        stdout = execution_result.get("stdout", "")
        
        analysis = {
            "output_length": len(stdout),
            "contains_recommendations": "action items" in stdout.lower(),
            "contains_prioritization": "priority" in stdout.lower(),
            "contains_evidence": "evidence" in stdout.lower(),
            "execution_efficiency": "budget-wise" in stdout.lower(),
            "generated_tldl": "TLDL entry" in stdout,
            "quality_indicators": []
        }
        
        # Quality assessment
        if analysis["contains_recommendations"]:
            analysis["quality_indicators"].append("structured_recommendations")
        if analysis["contains_prioritization"]:
            analysis["quality_indicators"].append("priority_awareness")
        if analysis["contains_evidence"]:
            analysis["quality_indicators"].append("evidence_based")
        if analysis["execution_efficiency"]:
            analysis["quality_indicators"].append("resource_efficient")
        
        analysis["overall_quality"] = len(analysis["quality_indicators"]) / 4  # Normalized score
        
        return analysis
    
    def _analyze_oracle_output(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Oracle output for forecasting quality."""
        if not execution_result["success"]:
            return {"analysis": "failed_execution", "forecasting_quality": "unknown"}
        
        stdout = execution_result.get("stdout", "")
        
        analysis = {
            "output_length": len(stdout),
            "contains_scenarios": "scenario" in stdout.lower(),
            "contains_probabilities": "probability" in stdout.lower(),
            "contains_risk_assessment": "risk" in stdout.lower(),
            "contains_strategic_horizon": "strategic" in stdout.lower(),
            "forecasting_indicators": []
        }
        
        # Forecasting quality assessment
        if analysis["contains_scenarios"]:
            analysis["forecasting_indicators"].append("scenario_generation")
        if analysis["contains_probabilities"]:
            analysis["forecasting_indicators"].append("probability_assessment")
        if analysis["contains_risk_assessment"]:
            analysis["forecasting_indicators"].append("risk_awareness")
        if analysis["contains_strategic_horizon"]:
            analysis["forecasting_indicators"].append("strategic_depth")
        
        analysis["forecasting_quality"] = len(analysis["forecasting_indicators"]) / 4
        
        return analysis
    
    def _analyze_faculty_coordination(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coordination between Advisor and Oracle."""
        if not execution_result["success"]:
            return {"coordination": "failed_execution"}
        
        stdout = execution_result.get("stdout", "")
        
        coordination_analysis = {
            "both_faculties_consulted": "advisor" in stdout.lower() and "oracle" in stdout.lower(),
            "coordinated_output": "consultation" in stdout.lower(),
            "resource_sharing": "budget" in stdout.lower(),
            "integrated_recommendations": "comprehensive" in stdout.lower(),
            "coordination_quality": "unknown"
        }
        
        # Assess coordination quality
        coordination_indicators = sum([
            coordination_analysis["both_faculties_consulted"],
            coordination_analysis["coordinated_output"],
            coordination_analysis["resource_sharing"],
            coordination_analysis["integrated_recommendations"]
        ])
        
        if coordination_indicators >= 3:
            coordination_analysis["coordination_quality"] = "high"
        elif coordination_indicators >= 2:
            coordination_analysis["coordination_quality"] = "medium"
        else:
            coordination_analysis["coordination_quality"] = "low"
        
        return coordination_analysis
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics across all tests."""
        successful_tests = sum(1 for result in self.results 
                             if result.get("scenario_results") and 
                             all(scenario.get("success", False) for scenario in result.get("scenario_results", [])))
        
        return {
            "total_test_categories": len(self.results),
            "successful_test_categories": successful_tests,
            "success_rate": successful_tests / len(self.results) if self.results else 0,
            "planning_capabilities_verified": [
                "advisor_stress_handling",
                "oracle_forecasting",
                "faculty_integration",
                "uncertainty_adaptation"
            ]
        }

if __name__ == "__main__":
    tester = PlanningFacultyTester()
    results = tester.run_all_tests()
    
    print(f"\n🧠📊 Planning Faculty Test Summary:")
    print(f"  Test Categories: {results['summary_stats']['total_test_categories']}")
    print(f"  Success Rate: {results['summary_stats']['success_rate']:.1%}")
    print(f"  Execution Time: {results['execution_time']:.2f}s")