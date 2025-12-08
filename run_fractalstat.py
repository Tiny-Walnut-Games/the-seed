#!/usr/bin/env python3

print("🚀 FractalStat System Launcher")
print("=" * 30)
print()

# Just run the basic checks without subprocess
import sys
from pathlib import Path

current_dir = Path.cwd()
print(f"Working directory: {current_dir}")

required_files = ["fractalstatwsserve.py", "fractalstatthreejs.html"]
all_good = True

for file in required_files:
    if Path(file).exists():
        print(f"✅ Found: {file}")
    else:
        print(f"❌ Missing: {file}")
        all_good = False

if all_good:
    print("\n✅ All FractalStat files present!")
    print("\nNext steps:")
    print("1. Run: python fractalstatwsserve.py")
    print("2. Run: python simple_web_server.py")
    print("3. Open: http://localhost:8000/fractalstatthreejs.html")
else:
    print("\n❌ Some files are missing!")
