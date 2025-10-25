#!/usr/bin/env python3

print("🚀 STAT7 System Launcher")
print("=" * 25)
print()

# Just run the basic checks without subprocess
import sys
from pathlib import Path

current_dir = Path.cwd()
print(f"Working directory: {current_dir}")

required_files = ["stat7wsserve.py", "stat7threejs.html"]
all_good = True

for file in required_files:
    if Path(file).exists():
        print(f"✅ Found: {file}")
    else:
        print(f"❌ Missing: {file}")
        all_good = False

if all_good:
    print("\n✅ All STAT7 files present!")
    print("\nNext steps:")
    print("1. Run: python stat7wsserve.py")
    print("2. Run: python simple_web_server.py")
    print("3. Open: http://localhost:8000/stat7threejs.html")
else:
    print("\n❌ Some files are missing!")