# Quick Reference - Import Patterns in The Seed

## ⚡ TL;DR - Copy This Pattern

**For ANY new Python script in this project:**

```python
#!/usr/bin/env python3

import sys
import os

# ALWAYS add this at the top (not inside functions)
try:
    from path_utils import ensure_project_paths
    ensure_project_paths()
except ImportError:
    # Fallback - you're in a weird location
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NOW you can import anything
from stat7wsserve import STAT7EventStreamer
from admin_api_server import AdminAPIServer
from governance import GovernanceMiddleware
# ... etc
```

---

## ✅ Working Examples

### From Root Directory
```bash
$ cd /the-seed
$ python stress_test_mmo.py
✅ Works - path_utils finds everything
```

### From Tests Directory
```bash
$ cd /the-seed/tests
$ python -m pytest test_stat7_server.py -v
✅ Works - path_utils set up at module load
```

### From Different Location
```bash
$ cd /some/other/path
$ python /the-seed/stress_test_mmo.py
✅ Works - absolute path used by path_utils
```

### From Different IDE
```
# In VS Code, Rider, PyCharm
Run: python verify_import_paths.py
✅ Works - all paths verified
```

---

## 🎯 What's Now Importable (No sys.path Hacks Needed)

```python
from stat7wsserve import (
    STAT7EventStreamer,           # Main WebSocket server
    ExperimentVisualizer,          # Visualization wrapper
    generate_random_bitchain,      # BitChain factory
    VisualizationEvent             # Event data class
)

from admin_api_server import AdminAPIServer  # Admin REST/WS API

from governance import GovernanceMiddleware  # Policy validator

from event_store import EventStore          # Append-only log

from tick_engine import TickEngine           # Cascade processor

from api_gateway import APIGateway           # Unified API layer

from e2e_simulation import E2ESimulationHarness  # Full simulation
```

---

## ❌ Don't Do This

```python
# ❌ WRONG - Fragile, breaks from different directories
sys.path.append('../web/server')
from stat7wsserve import STAT7EventStreamer

# ❌ WRONG - Uses append not insert (lower priority)
sys.path.append(path)

# ❌ WRONG - Relative imports for cross-module deps
from ..web.server.stat7wsserve import STAT7EventStreamer

# ❌ WRONG - Path setup inside functions (late binding)
def my_func():
    sys.path.insert(0, ...)
```

---

## ✅ Do This Instead

```python
# ✅ CORRECT - Single line, handles everything
from path_utils import ensure_project_paths
ensure_project_paths()

# ✅ CORRECT - Works if path_utils missing
try:
    from path_utils import ensure_project_paths
    ensure_project_paths()
except ImportError:
    # Manual fallback
    sys.path.insert(0, os.path.dirname(...))
```

---

## 🧪 Quick Test

```bash
# Verify everything works
python verify_import_paths.py

# Should see: ✅ PASS for all 5-6 checks

# If not, check:
# 1. Is path_utils.py in root? ls path_utils.py
# 2. Do test files exist? ls tests/test_*.py
# 3. Does web/server exist? ls web/server/stat7wsserve.py
```

---

## 📋 Path Resolution Order

When you use `path_utils.ensure_project_paths()`:

```
1. Detect project root (where pytest.ini is)
2. Add to sys.path (in order):
   - web/server/        ← stat7wsserve here
   - seed/engine/       ← stat7_experiments here
   - root/              ← fallback location
3. All imports now work! ✅
```

---

## 🚀 For Your Stress Test

```python
# stress_test_mmo.py - YOUR NEW FILE
#!/usr/bin/env python3

from path_utils import ensure_project_paths
ensure_project_paths()  # ONE LINE - everything else works

import asyncio
from stat7wsserve import STAT7EventStreamer
from admin_api_server import AdminAPIServer
# Your Warbler CDA here

class MMOStressTest:
    async def assault_with_population(self, count=1000):
        # Create 1000 concurrent players/NPCs
        # Warbler CDA creates stories
        # Admin API monitors
        # STAT7 visualizes
        pass
```

**That's it.** Just the one import line, then everything else works.

---

## 🎓 Path Reference

```
/the-seed/
├── path_utils.py                          ← Import resolver
├── verify_import_paths.py                 ← Verification tool
├── pytest.ini                             ← Test config
├── web/
│   ├── server/
│   │   ├── stat7wsserve.py               ← WebSocket server
│   │   ├── admin_api_server.py            ← Admin API
│   │   ├── governance.py                  ← Policies
│   │   ├── event_store.py                 ← Event log
│   │   ├── tick_engine.py                 ← Cascade engine
│   │   └── api_gateway.py                 ← API layer
│   ├── launchers/
│   │   └── launch_stat7_complete.py      ← Server launcher
│   └── js/                                ← Visualization client
├── tests/
│   ├── test_stat7_server.py
│   ├── test_websocket_load_stress.py
│   └── ... (394+ tests)
└── packages/
    └── com.twg.the-seed/
        └── The Living Dev Agent/
            └── ... (Warbler CDA)
```

---

## 💡 Pro Tips

1. **Always import at module level, not in functions**
   ```python
   # ✅ Good
   from path_utils import ensure_project_paths
   ensure_project_paths()
   
   def my_function():
       from stat7wsserve import STAT7EventStreamer  # Uses configured paths
   ```

2. **Use sys.path.insert(0, ...) not append()**
   ```python
   sys.path.insert(0, path)   # ✅ Searches here first
   sys.path.append(path)      # ❌ Searches here last
   ```

3. **Test from different locations regularly**
   ```bash
   cd /the-seed && python script.py         # From root
   cd /the-seed/tests && python script.py   # From subdir
   cd / && python /the-seed/script.py       # From completely elsewhere
   ```

4. **Always provide fallback imports**
   ```python
   try:
       from path_utils import ensure_project_paths
       ensure_project_paths()
   except ImportError:
       # Manual setup if path_utils not found
       sys.path.insert(0, os.path.join(root, 'web', 'server'))
   ```

---

## 🆘 When Imports Fail

```
Error: ModuleNotFoundError: No module named 'stat7wsserve'
│
├─→ Check 1: Is path_utils.py in root?
│   $ ls -la path_utils.py
│   $ python path_utils.py  # Should show OK
│
├─→ Check 2: Does web/server/stat7wsserve.py exist?
│   $ ls -la web/server/stat7wsserve.py
│
├─→ Check 3: Run verification
│   $ python verify_import_paths.py
│
└─→ Check 4: Manual sys.path test
    $ python -c "import sys; sys.path.insert(0, 'web/server'); from stat7wsserve import STAT7EventStreamer; print('OK')"
```

---

**Remember**: One line at the top of every script:
```python
from path_utils import ensure_project_paths
ensure_project_paths()
```

Everything else just works. 🎮