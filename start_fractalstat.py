#!/usr/bin/env python3
"""
FractalStat Visualization System - Quick Start Launcher
Simply run this file from the project root to start the visualization system.
"""

import os
import sys
import subprocess


def main():
    """Launch the FractalStat visualization system."""
    print("🚀 FractalStat Visualization System")
    print("=" * 40)

    # Check if web directory exists
    web_dir = os.path.join(os.path.dirname(__file__), "web")
    if not os.path.exists(web_dir):
        print("❌ Web directory not found!")
        print("   Expected:", web_dir)
        return 1

    # Check if launcher exists
    launcher_path = os.path.join(web_dir, "launchers", "run_fractalstat_visualization.py")
    if not os.path.exists(launcher_path):
        print("❌ Launcher not found!")
        print("   Expected:", launcher_path)
        return 1

    print("✅ Found FractalStat visualization system")
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
