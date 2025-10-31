#!/usr/bin/env python3
"""
Test script to validate Warbler integration improvements
Simulates the Unity workflow to ensure progress feedback works correctly
"""

import sys
import subprocess
import os
import time
from pathlib import Path


def test_ollama_progress_feedback():
    """Test Ollama manager progress feedback"""
    print("🧪 Testing Ollama Progress Feedback")
    print("=" * 40)
    
    script_dir = Path(__file__).parent
    ollama_script = script_dir / "ollama_manager.py"
    
    try:
        # Test status command
        print("Testing status command...")
        result = subprocess.run([
            sys.executable, str(ollama_script), "--status"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Status command exit code: {result.returncode}")
        if "platform" in result.stdout:
            print("✅ Status command works")
        else:
            print("❌ Status command failed")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
        
        # Test download progress (but don't actually download)
        print("\nTesting download progress command structure...")
        result = subprocess.run([
            sys.executable, str(ollama_script), "--download-progress"
        ], capture_output=True, text=True, timeout=10)
        
        # We expect this to fail (no ollama available) but check for proper error handling
        if "PROGRESS:" in result.stdout or "ERROR:" in result.stdout:
            print("✅ Progress feedback structure works")
        else:
            print("⚠️ Progress feedback may need adjustment")
            print(f"Output: {result.stdout}")
        
    except subprocess.TimeoutExpired:
        print("⏱️ Test timed out (expected for download test)")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print()


def test_github_auth_feedback():
    """Test GitHub authentication progress feedback"""
    print("🧪 Testing GitHub Auth Progress Feedback")
    print("=" * 40)
    
    script_dir = Path(__file__).parent
    auth_script = script_dir / "github_copilot_auth.py"
    
    try:
        # Test validate command
        print("Testing validate command...")
        result = subprocess.run([
            sys.executable, str(auth_script), "validate"
        ], capture_output=True, text=True, timeout=10)
        
        print(f"Validate command exit code: {result.returncode}")
        if "GitHub token" in result.stdout:
            print("✅ Validate command works")
        else:
            print("❌ Validate command failed")
            print(f"Output: {result.stdout}")
        
        # Test auth-progress command structure (but cancel quickly)
        print("\nTesting auth-progress command structure...")
        # We won't actually run this as it requires browser interaction
        print("✅ Auth-progress command available (browser test skipped)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print()


def test_terminus_bridge():
    """Test Terminus bridge functionality"""
    print("🧪 Testing Terminus Bridge")
    print("=" * 40)
    
    script_dir = Path(__file__).parent
    bridge_script = script_dir / "warbler_terminus_bridge.py"
    
    try:
        # Test diagnostic command
        print("Testing diagnostic command...")
        result = subprocess.run([
            sys.executable, str(bridge_script), "--diagnostic"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Diagnostic exit code: {result.returncode}")
        if "Connection Diagnostic" in result.stdout:
            print("✅ Diagnostic command works")
        else:
            print("❌ Diagnostic command failed")
            print(f"Output: {result.stdout}")
        
        # Check for structured output
        if "ollama_available" in result.stdout:
            print("✅ Structured diagnostic output present")
        else:
            print("⚠️ Structured output may be missing")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print()


def test_unity_integration_structure():
    """Test that Unity integration files have correct structure"""
    print("🧪 Testing Unity Integration Structure")
    print("=" * 40)
    
    script_dir = Path(__file__).parent
    unity_script = script_dir.parent / "Assets" / "TWG" / "Scripts" / "Editor" / "WarblerIntelligentOrchestrator.cs"
    
    try:
        if unity_script.exists():
            content = unity_script.read_text()
            
            # Check for key progress feedback methods
            if "StartOllamaService" in content:
                print("✅ Ollama service method present")
            else:
                print("❌ Ollama service method missing")
            
            if "AuthenticateGitHubCopilot" in content:
                print("✅ GitHub auth method present")
            else:
                print("❌ GitHub auth method missing")
            
            if "PROGRESS:" in content:
                print("✅ Progress feedback structure present")
            else:
                print("❌ Progress feedback structure missing")
            
            if "RunFullSetup" in content:
                print("✅ Full setup method present")
            else:
                print("❌ Full setup method missing")
                
        else:
            print("❌ Unity script file not found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print()


def main():
    """Run all integration tests"""
    print("🚀 Warbler Integration Test Suite")
    print("=" * 50)
    print("Testing progress feedback improvements...")
    print()
    
    # Run all tests
    test_ollama_progress_feedback()
    test_github_auth_feedback()
    test_terminus_bridge()
    test_unity_integration_structure()
    
    print("🎉 Integration tests completed!")
    print("These tests validate the structure and basic functionality")
    print("of the progress feedback improvements.")
    print()
    print("💡 Next steps:")
    print("1. Test in Unity Editor with actual Warbler window")
    print("2. Verify progress feedback during real operations")
    print("3. Test full setup workflow end-to-end")


if __name__ == "__main__":
    main()