#!/usr/bin/env python3
"""
Perceptual Faculty Test Scenarios

Tests the system's ability to process, parse, and understand various forms of input.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

class PerceptualFacultyTester:
    """Test the perceptual faculty's input processing capabilities."""
    
    def __init__(self, output_dir: str = "results/perceptual"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = []
    
    def test_intent_recognition_ambiguity(self) -> Dict[str, Any]:
        """Test intent processing with ambiguous inputs."""
        print("🧠 Testing Intent Recognition under Ambiguity...")
        
        test_cases = [
            {
                "input": "I want to help",
                "ambiguity": "help what/whom?",
                "expected_confidence": "medium"
            },
            {
                "input": "This is broken",
                "ambiguity": "what is broken?",
                "expected_confidence": "low"
            },
            {
                "input": "Can you do something about the thing?",
                "ambiguity": "vague references to 'something' and 'thing'",
                "expected_confidence": "very_low"
            },
            {
                "input": "The quick brown fox jumps over the lazy dog",
                "ambiguity": "unrelated to typical development context",
                "expected_confidence": "low"
            }
        ]
        
        results = {
            "test_name": "intent_recognition_ambiguity",
            "description": "Test intent processing with increasingly ambiguous inputs",
            "test_cases": [],
            "timestamp": time.time()
        }
        
        for case in test_cases:
            # Simulate intent processing (would integrate with actual warbler-core)
            processed_result = self._simulate_intent_processing(case["input"])
            
            case_result = {
                "input": case["input"],
                "expected_ambiguity": case["ambiguity"],
                "expected_confidence": case["expected_confidence"],
                "actual_result": processed_result,
                "passed": self._evaluate_ambiguity_handling(case, processed_result)
            }
            
            results["test_cases"].append(case_result)
            print(f"  📝 '{case['input'][:30]}...' -> Confidence: {processed_result.get('confidence', 'unknown')}")
        
        self.results.append(results)
        return results
    
    def test_context_boundary_detection(self) -> Dict[str, Any]:
        """Test ability to detect context boundaries and scope."""
        print("🧠 Testing Context Boundary Detection...")
        
        test_cases = [
            {
                "input": "Fix the login bug in the authentication module",
                "expected_scope": "specific_module",
                "expected_boundaries": ["authentication", "login"]
            },
            {
                "input": "Improve the entire system",
                "expected_scope": "system_wide",
                "expected_boundaries": ["system"]
            },
            {
                "input": "Update React components and also the database schema and maybe the API",
                "expected_scope": "multi_domain",
                "expected_boundaries": ["frontend", "backend", "database"]
            }
        ]
        
        results = {
            "test_name": "context_boundary_detection",
            "description": "Test ability to identify scope and boundaries in requests",
            "test_cases": [],
            "timestamp": time.time()
        }
        
        for case in test_cases:
            processed_result = self._simulate_context_parsing(case["input"])
            
            case_result = {
                "input": case["input"],
                "expected_scope": case["expected_scope"],
                "expected_boundaries": case["expected_boundaries"],
                "actual_result": processed_result,
                "passed": self._evaluate_boundary_detection(case, processed_result)
            }
            
            results["test_cases"].append(case_result)
            print(f"  🎯 Scope: {processed_result.get('scope', 'unknown')}, Boundaries: {processed_result.get('boundaries', [])}")
        
        self.results.append(results)
        return results
    
    def test_noise_resistance(self) -> Dict[str, Any]:
        """Test ability to extract signal from noisy inputs."""
        print("🧠 Testing Noise Resistance...")
        
        test_cases = [
            {
                "input": "umm, well, I think maybe we should, like, fix the... you know... the thing that's not working?",
                "signal": "fix something broken",
                "noise_level": "high_filler_words"
            },
            {
                "input": "FIX LOGIN BUG ASAP!!!!!!",
                "signal": "fix login bug",
                "noise_level": "high_emotion"
            },
            {
                "input": "The authentication system needs attention (see issue #123, also mentioned in Slack, ref: login-problems.md)",
                "signal": "authentication system needs work",
                "noise_level": "low_references"
            }
        ]
        
        results = {
            "test_name": "noise_resistance",
            "description": "Test ability to extract meaningful signal from noisy inputs",
            "test_cases": [],
            "timestamp": time.time()
        }
        
        for case in test_cases:
            processed_result = self._simulate_noise_processing(case["input"])
            
            case_result = {
                "input": case["input"],
                "expected_signal": case["signal"],
                "noise_level": case["noise_level"],
                "actual_result": processed_result,
                "passed": self._evaluate_noise_resistance(case, processed_result)
            }
            
            results["test_cases"].append(case_result)
            print(f"  🔊 Signal extracted: {processed_result.get('extracted_signal', 'none')}")
        
        self.results.append(results)
        return results
    
    def test_multimodal_understanding(self) -> Dict[str, Any]:
        """Test processing of different input modalities."""
        print("🧠 Testing Multimodal Understanding...")
        
        test_cases = [
            {
                "modality": "code_snippet",
                "input": "def broken_function():\n    return None  # TODO: implement",
                "expected_understanding": "incomplete_function"
            },
            {
                "modality": "error_message", 
                "input": "TypeError: 'NoneType' object is not callable at line 42",
                "expected_understanding": "runtime_error"
            },
            {
                "modality": "structured_data",
                "input": {"issue": 123, "priority": "high", "component": "auth"},
                "expected_understanding": "issue_metadata"
            }
        ]
        
        results = {
            "test_name": "multimodal_understanding",
            "description": "Test processing of different input types and modalities",
            "test_cases": [],
            "timestamp": time.time()
        }
        
        for case in test_cases:
            processed_result = self._simulate_multimodal_processing(case["input"], case["modality"])
            
            case_result = {
                "modality": case["modality"],
                "input": str(case["input"])[:100] + "..." if len(str(case["input"])) > 100 else str(case["input"]),
                "expected_understanding": case["expected_understanding"],
                "actual_result": processed_result,
                "passed": self._evaluate_multimodal_understanding(case, processed_result)
            }
            
            results["test_cases"].append(case_result)
            print(f"  📊 {case['modality']}: {processed_result.get('understanding_type', 'unknown')}")
        
        self.results.append(results)
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all perceptual faculty tests and generate report."""
        print("🧠📜 Running Perceptual Faculty Test Suite...")
        
        start_time = time.time()
        
        # Run individual tests
        self.test_intent_recognition_ambiguity()
        self.test_context_boundary_detection()
        self.test_noise_resistance()
        self.test_multimodal_understanding()
        
        end_time = time.time()
        
        # Generate summary report
        summary = {
            "faculty": "perceptual",
            "test_suite": "comprehensive_perceptual_analysis",
            "total_tests": len(self.results),
            "execution_time": end_time - start_time,
            "results": self.results,
            "summary_stats": self._calculate_summary_stats(),
            "timestamp": end_time
        }
        
        # Save results
        output_file = os.path.join(self.output_dir, f"perceptual_faculty_test_results_{int(end_time)}.json")
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"🧠✅ Perceptual Faculty tests complete. Results saved to {output_file}")
        return summary
    
    # Simulation methods (would integrate with actual components)
    def _simulate_intent_processing(self, input_text: str) -> Dict[str, Any]:
        """Simulate intent processing (placeholder for actual integration)."""
        # This would integrate with packages/warbler-core/src/intents.ts
        word_count = len(input_text.split())
        question_marks = input_text.count('?')
        
        confidence = 0.9 if word_count > 5 and question_marks == 0 else 0.3
        
        return {
            "intent_type": "help_request" if "help" in input_text.lower() else "general_inquiry",
            "confidence": confidence,
            "processing_time": 0.01,
            "metadata": {"word_count": word_count, "question_marks": question_marks}
        }
    
    def _simulate_context_parsing(self, input_text: str) -> Dict[str, Any]:
        """Simulate context boundary detection."""
        keywords = ["system", "module", "component", "service", "api", "database", "frontend", "backend"]
        found_keywords = [kw for kw in keywords if kw in input_text.lower()]
        
        if len(found_keywords) > 2:
            scope = "multi_domain"
        elif len(found_keywords) == 1:
            scope = "specific_module"
        else:
            scope = "system_wide" if "system" in input_text.lower() else "unclear"
        
        return {
            "scope": scope,
            "boundaries": found_keywords,
            "complexity": len(found_keywords)
        }
    
    def _simulate_noise_processing(self, input_text: str) -> Dict[str, Any]:
        """Simulate noise filtering and signal extraction."""
        filler_words = ["umm", "well", "like", "you know", "maybe", "I think"]
        emotion_indicators = ["!!!", "ASAP", "urgent", "critical"]
        
        cleaned_text = input_text
        for filler in filler_words:
            cleaned_text = cleaned_text.replace(filler, "")
        
        noise_level = sum(1 for filler in filler_words if filler in input_text.lower())
        emotion_level = sum(1 for emotion in emotion_indicators if emotion in input_text)
        
        return {
            "extracted_signal": cleaned_text.strip(),
            "noise_level": noise_level,
            "emotion_level": emotion_level,
            "signal_clarity": max(0.1, 1.0 - (noise_level * 0.2))
        }
    
    def _simulate_multimodal_processing(self, input_data: Any, modality: str) -> Dict[str, Any]:
        """Simulate processing of different input modalities."""
        if modality == "code_snippet":
            return {
                "understanding_type": "code_analysis",
                "contains_todo": "TODO" in str(input_data),
                "estimated_completeness": 0.3 if "TODO" in str(input_data) else 0.8
            }
        elif modality == "error_message":
            return {
                "understanding_type": "error_analysis",
                "error_type": "TypeError" if "TypeError" in str(input_data) else "unknown",
                "severity": "high" if "Error" in str(input_data) else "medium"
            }
        elif modality == "structured_data":
            return {
                "understanding_type": "metadata_analysis",
                "structure_complexity": len(input_data) if isinstance(input_data, dict) else 1,
                "data_completeness": 0.9
            }
        
        return {"understanding_type": "unknown", "processed": False}
    
    # Evaluation methods
    def _evaluate_ambiguity_handling(self, test_case: Dict, result: Dict) -> bool:
        """Evaluate how well ambiguity was handled."""
        expected_confidence = test_case["expected_confidence"]
        actual_confidence = result.get("confidence", 0)
        
        if expected_confidence == "very_low":
            return actual_confidence < 0.3
        elif expected_confidence == "low":
            return actual_confidence < 0.5
        elif expected_confidence == "medium":
            return 0.3 <= actual_confidence <= 0.7
        
        return True
    
    def _evaluate_boundary_detection(self, test_case: Dict, result: Dict) -> bool:
        """Evaluate boundary detection accuracy."""
        expected_scope = test_case["expected_scope"]
        actual_scope = result.get("scope", "")
        return expected_scope == actual_scope
    
    def _evaluate_noise_resistance(self, test_case: Dict, result: Dict) -> bool:
        """Evaluate noise filtering effectiveness."""
        signal_clarity = result.get("signal_clarity", 0)
        noise_level = test_case["noise_level"]
        
        if noise_level == "high_filler_words" or noise_level == "high_emotion":
            return signal_clarity > 0.5
        else:
            return signal_clarity > 0.7
    
    def _evaluate_multimodal_understanding(self, test_case: Dict, result: Dict) -> bool:
        """Evaluate multimodal processing accuracy."""
        expected = test_case["expected_understanding"]
        actual = result.get("understanding_type", "")
        
        # Flexible matching for different understanding types
        if expected == "incomplete_function":
            return "code" in actual and result.get("contains_todo", False)
        elif expected == "runtime_error":
            return "error" in actual
        elif expected == "issue_metadata":
            return "metadata" in actual
        
        return False
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics across all tests."""
        total_test_cases = sum(len(test["test_cases"]) for test in self.results)
        passed_test_cases = sum(
            sum(1 for case in test["test_cases"] if case["passed"]) 
            for test in self.results
        )
        
        return {
            "total_test_cases": total_test_cases,
            "passed_test_cases": passed_test_cases,
            "pass_rate": passed_test_cases / total_test_cases if total_test_cases > 0 else 0,
            "test_categories": len(self.results)
        }

if __name__ == "__main__":
    tester = PerceptualFacultyTester()
    results = tester.run_all_tests()
    
    print(f"\n🧠📊 Perceptual Faculty Test Summary:")
    print(f"  Total Tests: {results['summary_stats']['total_test_cases']}")
    print(f"  Pass Rate: {results['summary_stats']['pass_rate']:.1%}")
    print(f"  Execution Time: {results['execution_time']:.2f}s")