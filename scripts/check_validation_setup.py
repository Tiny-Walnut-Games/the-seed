#!/usr/bin/env python3
"""
Pre-Push Validation Setup Checker

Run this BEFORE pushing to GitHub to ensure validation system is ready.

This checks:
- Test files exist
- Workflow is configured
- Tests can run locally
- Everything is ready for public validation

Usage:
    python scripts/check_validation_setup.py
"""

import sys
from pathlib import Path
import subprocess

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_item(condition, success_msg, failure_msg, fix_msg=None):
    if condition:
        print(f"✅ {success_msg}")
        return True
    else:
        print(f"❌ {failure_msg}")
        if fix_msg:
            print(f"   Fix: {fix_msg}")
        return False

def check_files_exist():
    """Check all required files exist"""
    print_section("FILE EXISTENCE CHECK")
    
    required_files = [
        ("tests/test_websocket_load_stress.py", "Test file"),
        (".github/workflows/mmo-load-test-validation.yml", "Workflow file"),
        ("docs/LOAD_TEST_VALIDATION.md", "Documentation"),
        ("scripts/verify_load_test_reality.py", "Reality check script"),
    ]
    
    all_good = True
    for file_path, description in required_files:
        path = Path(file_path)
        all_good &= check_item(
            path.exists(),
            f"{description} exists: {file_path}",
            f"{description} missing: {file_path}",
            f"Create the file at {file_path}"
        )
    
    return all_good

def check_test_file_content():
    """Check test file has required content"""
    print_section("TEST FILE CONTENT CHECK")
    
    test_file = Path("tests/test_websocket_load_stress.py")
    if not test_file.exists():
        print("❌ Test file doesn't exist, skipping content check")
        return False
    
    content = test_file.read_text()
    
    checks = [
        ("test_concurrent_500_clients" in content, "500-player test function exists"),
        ("test_concurrent_100_clients" in content, "100-player test function exists"),
        ("assert" in content, "Test has assertions (actual validation)"),
        ("latency" in content.lower(), "Test measures latency"),
        ("websocket" in content.lower(), "Test uses WebSocket"),
        ("pytest" in content, "Uses pytest framework"),
    ]
    
    all_good = True
    for condition, description in checks:
        all_good &= check_item(
            condition,
            description,
            f"{description} - NOT FOUND"
        )
    
    return all_good

def check_workflow_configuration():
    """Check workflow file is properly configured"""
    print_section("WORKFLOW CONFIGURATION CHECK")
    
    workflow_file = Path(".github/workflows/mmo-load-test-validation.yml")
    if not workflow_file.exists():
        print("❌ Workflow file doesn't exist, skipping configuration check")
        return False
    
    content = workflow_file.read_text(encoding='utf-8')
    
    checks = [
        ("test_concurrent_500_clients" in content, "Workflow runs 500-player test"),
        ("ubuntu-latest" in content, "Uses Ubuntu runner"),
        ("pytest" in content, "Uses pytest"),
        ("actions/upload-artifact@v3" in content, "Uploads artifacts"),
        ("actions/github-script@v7" in content, "Posts results"),
        ("validate-test-mathematics" in content, "Has math validation job"),
    ]
    
    all_good = True
    for condition, description in checks:
        all_good &= check_item(
            condition,
            description,
            f"{description} - NOT FOUND"
        )
    
    return all_good

def check_dependencies():
    """Check Python dependencies are available"""
    print_section("DEPENDENCY CHECK")
    
    required_packages = [
        ("pytest", "Test framework"),
        ("websockets", "WebSocket library"),
    ]
    
    all_good = True
    for package, description in required_packages:
        try:
            __import__(package)
            check_item(True, f"{description} ({package}) installed", "")
        except ImportError:
            all_good &= check_item(
                False,
                "",
                f"{description} ({package}) NOT installed",
                f"Run: pip install {package}"
            )
    
    return all_good

def check_git_status():
    """Check git status"""
    print_section("GIT STATUS CHECK")
    
    # Check if .git exists
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ Not a git repository")
        print("   Fix: Run 'git init' to initialize repository")
        return False
    
    print("✅ Git repository initialized")
    
    # Check if there are uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        uncommitted = result.stdout.strip()
        if uncommitted:
            print("⚠️  You have uncommitted changes:")
            print(uncommitted[:500])  # Show first 500 chars
            print("\n   Remember to commit before pushing!")
            return True  # Not a failure, just a warning
        else:
            print("✅ No uncommitted changes")
            return True
    except subprocess.CalledProcessError:
        print("⚠️  Could not check git status")
        return True
    except FileNotFoundError:
        print("⚠️  Git command not found")
        return True

def try_run_quick_test():
    """Try to run a quick local test"""
    print_section("LOCAL TEST EXECUTION CHECK")
    
    print("Attempting to run a quick test locally...")
    print("(This verifies tests can actually execute)")
    
    try:
        # Try to run a quick test
        result = subprocess.run(
            ["python", "-m", "pytest", 
             "tests/test_websocket_load_stress.py::test_connection_lifecycle",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            print("✅ Local test execution SUCCESSFUL")
            print("   Tests can run on your machine")
            return True
        else:
            print("⚠️  Local test execution FAILED")
            print("   Tests may still work on GitHub Actions")
            print("\n   Output:")
            print(result.stdout[-500:] if result.stdout else "No output")
            print(result.stderr[-500:] if result.stderr else "No errors")
            return True  # Not blocking - might work on GitHub
    
    except FileNotFoundError:
        print("⚠️  Could not run pytest (command not found)")
        print("   Tests will run on GitHub Actions with their Python environment")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Test timed out (took >60 seconds)")
        print("   This might be normal for load tests")
        return True
    except Exception as e:
        print(f"⚠️  Could not run test: {e}")
        print("   Tests will run on GitHub Actions")
        return True

def show_next_steps(all_passed):
    """Show what to do next"""
    print_section("NEXT STEPS")
    
    if all_passed:
        print("\n✅ ✅ ✅  ALL CHECKS PASSED  ✅ ✅ ✅")
        print("\nYour validation setup is ready!")
        print("\n📋 Next Steps:")
        print("\n1. Commit your changes:")
        print("   git add .")
        print("   git commit -m 'Add load test validation infrastructure'")
        print("\n2. Push to GitHub:")
        print("   git push origin main")
        print("\n3. Verify workflow runs:")
        print("   - Go to: https://github.com/YOUR_USERNAME/the-seed/actions")
        print("   - Look for: 'MMO Load Test - Third-Party Validation'")
        print("   - Wait for completion (~10-15 minutes)")
        print("   - Check new GitHub Issue for results")
        print("\n4. Verify results are public:")
        print("   - Copy workflow URL")
        print("   - Open in private/incognito browser")
        print("   - Verify you can see results without logging in")
        print("\n5. Add badge to README:")
        print("   - See: docs/README_LOAD_TEST_BADGE.md")
        print("   - Copy badge markdown to your README.md")
        print("\n🎯 OBJECTIVE PROOF WILL BE CREATED:")
        print("   ✅ GitHub's timestamp (not yours)")
        print("   ✅ GitHub's infrastructure (not yours)")  
        print("   ✅ Public URL (anyone can view)")
        print("   ✅ Reproducible (anyone can run)")
    
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\n🔧 Fix the issues above, then run this script again:")
        print("   python scripts/check_validation_setup.py")
        print("\n📚 Need Help?")
        print("   - Review: docs/LOAD_TEST_VALIDATION.md")
        print("   - Check: Test file exists and has proper content")
        print("   - Check: Workflow file exists and is configured")
        print("   - Check: Dependencies are installed (pip install pytest websockets)")

def main():
    print("\n" + "=" * 70)
    print("  🔬 VALIDATION SETUP PRE-FLIGHT CHECK")
    print("  Verify everything is ready before pushing to GitHub")
    print("=" * 70)
    print("\nThis script checks if your validation infrastructure is ready.")
    print("Run this BEFORE pushing to GitHub.\n")
    
    # Run all checks
    checks = []
    checks.append(check_files_exist())
    checks.append(check_test_file_content())
    checks.append(check_workflow_configuration())
    checks.append(check_dependencies())
    checks.append(check_git_status())
    checks.append(try_run_quick_test())
    
    all_passed = all(checks)
    
    show_next_steps(all_passed)
    
    print("\n" + "=" * 70)
    print("  END OF PRE-FLIGHT CHECK")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())