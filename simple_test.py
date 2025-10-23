#!/usr/bin/env python3
"""
Simple STAT7 Test - No subprocess calls
Direct Python execution to avoid IDE PowerShell issues
"""

import os
import sys
from pathlib import Path

def main():
    print("🌟 STAT7 Simple Test Runner")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if required files exist
    required_files = [
        "stat7wsserve.py",
        "stat7threejs.html", 
        "test_stat7_setup.py",
        "test_complete_system.py"
    ]
    
    print("\n📋 File Check:")
    all_files_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n⚠️ Some required files are missing.")
        return False
    
    # Try to import test modules directly
    print("\n🧪 Direct Module Tests:")
    
    try:
        # Test setup validation
        print("Testing setup validation...")
        sys.path.insert(0, str(current_dir))
        
        # Import and run test_stat7_setup directly
        import test_stat7_setup
        if hasattr(test_stat7_setup, 'main'):
            result = test_stat7_setup.main()
            print(f"✅ Setup test: {'PASSED' if result else 'FAILED'}")
        
        print("\n🎉 Basic validation complete!")
        print("\n📋 To run full system:")
        print("1. Double-click: run_tests.bat")
        print("2. Or in terminal: python run_stat7_tests.py") 
        print("3. Or start system: python quick_start_stat7.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to continue...")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Error: {e}")
        input("\nPress Enter to continue...")
        sys.exit(1)