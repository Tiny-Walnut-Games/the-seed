#!/usr/bin/env python3
"""
STAT7 Visualization Test Runner

Comprehensive test runner for the complete STAT7 visualization system.
Runs unit tests, system tests, and E2E tests in sequence.
"""

import asyncio
import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description, timeout=60):
    """Run a command and return success status."""
    print(f"🚀 {description}")
    print("-" * 50)
    
    # Windows PowerShell quoting fix
    if sys.platform == "win32" and isinstance(command, list):
        # Use cmd.exe instead of PowerShell to avoid quoting issues
        if command[0] == sys.executable:
            command = ["cmd", "/c", "python"] + command[1:]
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
            shell=(sys.platform == "win32")
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"💥 {description} failed with error: {e}")
        return False

async def run_async_test(test_file, description):
    """Run an async test file."""
    print(f"🚀 {description}")
    print("-" * 50)
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, test_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        print(stdout.decode())
        if stderr:
            print(f"Warnings: {stderr.decode()}")
            
        if process.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed with exit code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"💥 {description} failed with error: {e}")
        return False

async def main():
    """Main test runner."""
    print("🌟 STAT7 Visualization Complete Test Suite")
    print("=" * 60)
    print("Testing all components of the STAT7 visualization system...")
    print()
    
    # Check if we're in the right directory
    if not Path("stat7wsserve.py").exists():
        print("❌ Error: stat7wsserve.py not found in current directory")
        print("Please run this script from the STAT7 project root directory")
        sys.exit(1)
    
    # Test sequence
    tests = []
    passed = 0
    failed = 0
    
    # Phase 1: Setup and Prerequisites
    print("📋 Phase 1: Setup and Prerequisites")
    print("=" * 40)
    
    test_result = run_command(
        [sys.executable, "test_stat7_setup.py"],
        "Setup Validation Test"
    )
    tests.append(("Setup Validation", test_result))
    
    # Phase 2: System Component Tests  
    print(f"\n📊 Phase 2: System Component Tests")
    print("=" * 40)
    
    test_result = await run_async_test(
        "test_complete_system.py",
        "Complete System Test"
    )
    tests.append(("Complete System", test_result))
    
    test_result = await run_async_test(
        "test_server_data.py", 
        "Server Data Generation Test"
    )
    tests.append(("Server Data", test_result))
    
    # Phase 3: Integration Tests (Optional - requires servers to be running)
    print(f"\n🔗 Phase 3: Integration Tests (Optional)")
    print("=" * 40)
    print("Note: These tests require running servers. Starting in background...")
    
    # Try to run integration test but don't fail if servers aren't running
    try:
        test_result = await run_async_test(
            "test_enhanced_visualization.py",
            "Enhanced Visualization Test"
        )
        tests.append(("Enhanced Visualization", test_result))
    except Exception:
        print("⚠️ Integration test skipped (servers not running)")
        tests.append(("Enhanced Visualization", None))
    
    # Phase 4: E2E Tests (Optional - requires Playwright)
    print(f"\n🎭 Phase 4: End-to-End Tests (Optional)")
    print("=" * 40)
    
    try:
        import playwright
        print("✅ Playwright available")
        
        # Ask user if they want to run E2E tests
        run_e2e = input("Run E2E tests? (y/n): ").lower().startswith('y')
        
        if run_e2e:
            test_result = await run_async_test(
                "test_stat7_e2e.py",
                "Complete E2E Test Suite"
            )
            tests.append(("E2E Tests", test_result))
        else:
            print("⏭️ E2E tests skipped by user")
            tests.append(("E2E Tests", None))
            
    except ImportError:
        print("⚠️ Playwright not installed. E2E tests skipped.")
        print("Install with: pip install playwright")
        print("Then run: playwright install chromium")
        tests.append(("E2E Tests", None))
    
    # Calculate results
    for test_name, result in tests:
        if result is True:
            passed += 1
        elif result is False:
            failed += 1
        # None results are skipped tests
    
    # Final Summary
    print(f"\n📈 Final Test Results")
    print("=" * 60)
    
    for test_name, result in tests:
        if result is True:
            print(f"✅ {test_name}: PASSED")
        elif result is False:
            print(f"❌ {test_name}: FAILED")
        else:
            print(f"⏭️ {test_name}: SKIPPED")
    
    total_run = passed + failed
    skipped = len([t for t in tests if t[1] is None])
    
    print(f"\n📊 Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️ Skipped: {skipped}")
    
    if total_run > 0:
        success_rate = (passed / total_run) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Final status
    if failed == 0 and passed > 0:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("🚀 STAT7 Visualization System is ready!")
        print()
        print("📋 Quick Start:")
        print("1. Run: python stat7wsserve.py")
        print("2. Run: python simple_web_server.py")  
        print("3. Open: http://localhost:8000/stat7threejs.html")
        print("4. Test experiments EXP01-EXP10")
        return True
    elif failed == 0 and passed == 0:
        print(f"\n⚠️ No tests were executed successfully.")
        print("Please check your environment and dependencies.")
        return False
    else:
        print(f"\n⚠️ {failed} test(s) failed.")
        print("Please review the failed tests and fix any issues.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)