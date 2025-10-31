#!/usr/bin/env python3
"""Quick test of simple_web_server.py"""

import sys
import os

os.chdir("E:/Tiny_Walnut_Games/the-seed/web")
sys.path.insert(0, "E:/Tiny_Walnut_Games/the-seed/web/server")

try:
    from simple_web_server import main
    print("[TEST] Running simple_web_server.main()...")
    main()
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()