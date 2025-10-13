#!/usr/bin/env python3
"""
🔌 Ollama Connection Validation Script
Sacred Mission: Validate Ollama AI service connectivity and response capabilities

Author: Bootstrap Sentinel & Living Dev Agent
Chronicle: Part of the Warbler AI Project Orchestrator implementation
"""

import requests
import json
import time
import sys
import argparse
from typing import Dict, Any, Optional, Tuple


class OllamaConnectionTester:
    """🧪 Ollama connectivity and capability tester"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Set connection timeout to 10s, read timeout to 90s for testing
        self.session.timeout = (10, 90)
        
    def test_basic_connectivity(self) -> Tuple[bool, str]:
        """Test basic connectivity to Ollama API"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                return True, f"✅ Ollama API responding (HTTP {response.status_code})"
            else:
                return False, f"❌ Ollama API returned HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"❌ Connection failed: Cannot connect to {self.base_url}"
        except requests.exceptions.Timeout:
            return False, f"❌ Connection timeout: Ollama not responding within timeout"
        except Exception as e:
            return False, f"❌ Unexpected error: {e}"
    
    def test_api_tags(self) -> Tuple[bool, str]:
        """Test /api/tags endpoint to see available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                if models:
                    model_names = [model.get('name', 'unknown') for model in models]
                    return True, f"✅ Available models: {', '.join(model_names)}"
                else:
                    return False, "❌ No models available in Ollama"
            else:
                return False, f"❌ Tags endpoint returned HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "❌ Tags request timed out"
        except Exception as e:
            return False, f"❌ Tags request failed: {e}"
    
    def test_simple_generation(self, model: str = "llama2", timeout: int = 60) -> Tuple[bool, str]:
        """Test simple text generation with progressive timeout"""
        try:
            # Use a very simple prompt to minimize processing time
            payload = {
                "model": model,
                "prompt": "Say 'Hello' in one word:",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.1,
                    "max_tokens": 5
                }
            }
            
            start_time = time.time()
            
            # Override session timeout for this specific test
            original_timeout = self.session.timeout
            self.session.timeout = (10, timeout)
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get('response', '').strip()
                    return True, f"✅ Generation successful ({elapsed:.1f}s): '{generated_text}'"
                else:
                    return False, f"❌ Generation failed: HTTP {response.status_code}"
                    
            finally:
                # Restore original timeout
                self.session.timeout = original_timeout
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return False, f"❌ Generation timeout after {elapsed:.1f}s (limit: {timeout}s)"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"❌ Generation failed after {elapsed:.1f}s: {e}"
    
    def test_streaming_capability(self, model: str = "llama2", timeout: int = 30) -> Tuple[bool, str]:
        """Test streaming response capability"""
        try:
            payload = {
                "model": model,
                "prompt": "Count: 1, 2, 3",
                "stream": True,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 10
                }
            }
            
            start_time = time.time()
            
            original_timeout = self.session.timeout
            self.session.timeout = (10, timeout)
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    stream=True
                )
                
                if response.status_code == 200:
                    chunks_received = 0
                    for line in response.iter_lines():
                        if line:
                            chunks_received += 1
                            if chunks_received >= 3:  # Get a few chunks then stop
                                break
                    
                    elapsed = time.time() - start_time
                    return True, f"✅ Streaming works ({chunks_received} chunks in {elapsed:.1f}s)"
                else:
                    return False, f"❌ Streaming failed: HTTP {response.status_code}"
                    
            finally:
                self.session.timeout = original_timeout
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return False, f"❌ Streaming timeout after {elapsed:.1f}s"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"❌ Streaming failed after {elapsed:.1f}s: {e}"
    
    def run_comprehensive_test(self, model: str = "llama2") -> Dict[str, Any]:
        """Run all connectivity tests"""
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'model': model,
            'tests': {}
        }
        
        print(f"🧪 Testing Ollama connectivity at {self.base_url}")
        print(f"🎯 Target model: {model}")
        print("-" * 50)
        
        # Test 1: Basic connectivity
        print("1️⃣ Testing basic connectivity...")
        success, message = self.test_basic_connectivity()
        results['tests']['connectivity'] = {'success': success, 'message': message}
        print(f"   {message}")
        
        if not success:
            print("\n❌ Basic connectivity failed. Cannot proceed with other tests.")
            return results
        
        # Test 2: API tags
        print("\n2️⃣ Testing API tags endpoint...")
        success, message = self.test_api_tags()
        results['tests']['tags'] = {'success': success, 'message': message}
        print(f"   {message}")
        
        # Test 3: Simple generation with escalating timeouts
        for timeout in [30, 60, 120]:
            print(f"\n3️⃣ Testing simple generation (timeout: {timeout}s)...")
            success, message = self.test_simple_generation(model, timeout)
            results['tests'][f'generation_{timeout}s'] = {'success': success, 'message': message}
            print(f"   {message}")
            
            if success:
                break  # Success at this timeout level
        
        # Test 4: Streaming capability
        print(f"\n4️⃣ Testing streaming capability...")
        success, message = self.test_streaming_capability(model)
        results['tests']['streaming'] = {'success': success, 'message': message}
        print(f"   {message}")
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 OLLAMA CONNECTION TEST SUMMARY")
        print("=" * 50)
        
        tests = results['tests']
        passed = sum(1 for test in tests.values() if test['success'])
        total = len(tests)
        
        print(f"📈 Tests passed: {passed}/{total}")
        print(f"🎯 Model tested: {results['model']}")
        print(f"🔗 Endpoint: {results['base_url']}")
        print(f"⏰ Timestamp: {results['timestamp']}")
        
        print("\n📝 Recommendations:")
        
        if tests.get('connectivity', {}).get('success'):
            print("✅ Ollama is accessible")
        else:
            print("❌ Fix Ollama connectivity first")
            print("   - Ensure Ollama is running: ollama serve")
            print("   - Check firewall settings")
            return
        
        if tests.get('tags', {}).get('success'):
            print("✅ API endpoints working")
        else:
            print("❌ API endpoints not responding properly")
            return
        
        # Check generation results
        generation_success = False
        recommended_timeout = 120
        
        for timeout in [30, 60, 120]:
            test_key = f'generation_{timeout}s'
            if tests.get(test_key, {}).get('success'):
                generation_success = True
                recommended_timeout = timeout
                break
        
        if generation_success:
            print(f"✅ Text generation works (recommended timeout: {recommended_timeout}s)")
        else:
            print("❌ Text generation failed at all timeout levels")
            print("   - Model may not be loaded: ollama pull llama2")
            print("   - Try a smaller/faster model")
            print("   - Check system resources (RAM/CPU)")
        
        if tests.get('streaming', {}).get('success'):
            print("✅ Streaming responses supported")
        else:
            print("⚠️ Streaming may not work reliably")
        
        print(f"\n🎯 For Warbler integration, use timeout >= {recommended_timeout}s")


def main():
    """CLI interface for Ollama connection testing"""
    parser = argparse.ArgumentParser(description="🔌 Test Ollama AI connectivity")
    parser.add_argument('--url', default='http://localhost:11434',
                        help='Ollama base URL (default: http://localhost:11434)')
    parser.add_argument('--model', default='llama2',
                        help='Model to test (default: llama2)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    parser.add_argument('--quick', action='store_true',
                        help='Run only basic connectivity tests')
    
    args = parser.parse_args()
    
    tester = OllamaConnectionTester(args.url)
    
    if args.quick:
        # Quick test mode
        success, message = tester.test_basic_connectivity()
        if args.json:
            print(json.dumps({'success': success, 'message': message}))
        else:
            print(message)
        sys.exit(0 if success else 1)
    
    # Comprehensive test
    results = tester.run_comprehensive_test(args.model)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        tester.print_summary(results)
    
    # Exit with error code if any critical tests failed
    connectivity_ok = results['tests'].get('connectivity', {}).get('success', False)
    generation_ok = any(
        results['tests'].get(f'generation_{timeout}s', {}).get('success', False)
        for timeout in [30, 60, 120]
    )
    
    if connectivity_ok and generation_ok:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()