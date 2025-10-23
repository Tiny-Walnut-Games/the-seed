#!/usr/bin/env python3
"""
Quick test to verify STAT7 visualization setup
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def test_setup():
    """Test if all required files are present."""
    print("🔍 Checking STAT7 Visualization setup...")

    required_files = [
        "stat7wsserve.py",
        "stat7threejs.html",
        "start_stat7_visualization.py",
        "requirements-visualization.txt"
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ All required files found")
    return True

def test_python_dependencies():
    """Test if required Python packages are available."""
    print("📦 Checking Python dependencies...")

    try:
        import websockets
        print("✅ websockets package found")
    except ImportError:
        print("❌ websockets package not found")
        print("Run: pip install websockets")
        return False

    return True

def test_html_file():
    """Test if the HTML file is accessible."""
    print("🌐 Testing HTML file...")

    html_path = Path("stat7threejs.html")
    if not html_path.exists():
        print("❌ HTML file not found")
        return False

    # Read and check if it contains Three.js
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "Three.js" in content or "three.min.js" in content:
            print("✅ HTML file contains Three.js")
        else:
            print("⚠️ HTML file may not contain Three.js")

    return True

def main():
    """Run all tests."""
    print("🧪 STAT7 Visualization Setup Test")
    print("=" * 40)

    tests = [
        ("File Check", test_setup),
        ("Dependencies", test_python_dependencies),
        ("HTML File", test_html_file),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the visualization:")
        print("   Option 1: Double-click start_visualization.bat")
        print("   Option 2: Run: python start_stat7_visualization.py")
        print("   Option 3: Run: python stat7wsserve.py (then open HTML manually)")
    else:
        print("❌ Some tests failed. Please fix the issues above.")

    return all_passed

if __name__ == "__main__":
    main()
