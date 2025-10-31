#!/usr/bin/env python3
"""
STAT7 Visualization System - Quick Start Launcher
Simply run this file from the project root to start the visualization system.
"""

import os
import sys
import subprocess
import io

# Fix for Windows console encoding (emoji support)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    """Launch the STAT7 visualization system."""
    print("🚀 STAT7 Visualization System")
    print("=" * 40)

    # Check if web directory exists
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    if not os.path.exists(web_dir):
        print("❌ Web directory not found!")
        print("   Expected:", web_dir)
        return 1

    # Check if launcher exists
    launcher_path = os.path.join(web_dir, 'launchers', 'run_stat7_visualization.py')
    if not os.path.exists(launcher_path):
        print("❌ Launcher not found!")
        print("   Expected:", launcher_path)
        return 1

    print("✅ Found STAT7 visualization system")
    print("🚀 Starting visualization system...")

    # Run the visualization system
    try:
        subprocess.run([sys.executable, launcher_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Launcher failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
