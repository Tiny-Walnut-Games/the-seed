# 🚀 Getting Started with The Seed

Quick start guide for developers joining **The Seed** - a multiverse simulation framework with STAT7 (7-dimensional) addressing, TLDA (Unity game engine layer), and Seed (Python backend with AI).

**Current Status**: ✅ Production Ready  
**Time to First Success**: ~15-30 minutes  
**Complexity**: Easy to Intermediate

---

## 📋 **Prerequisites**

### **System Requirements:**
- **Unity 2022.3+** or **Unity 6000.2.6f2 LTS** (for TLDA development)
- **Python 3.9+** (for Seed development)
- **Node.js 18+** (for web components)
- **Git** (for version control)
- **PowerShell 5.1+** (Windows) or **Bash** (Linux/Mac)

### **Python Dependencies:**
```bash
pip install websockets asyncio pytest fastapi uvicorn aiohttp
```

### **Unity Requirements:**
- Unity Hub installed
- Steamworks SDK (for Steam integration)
- .NET Framework 4.7.1+ or .NET 6.0+

### **Verification:**
```bash
# Verify Python
python --version          # Should be 3.9+

# Verify Node (if doing web work)
node --version            # Should be 18+

# Verify Git
git --version             # Should be 2.35+
```

---

## 🎯 **Choose Your Development Path**

The Seed has three distinct systems. **Choose the one that matches your work:**

### **🎮 Path 1: Game Developer (TLDA)**
You want to build games, gameplay mechanics, and Unity integrations.

**What you'll work on:**
- Unity editor tools and plugins
- Gameplay mechanics and systems
- NPC behavior (Warbler integration)
- UI/UX in Unity

**Start Here:**
1. Read: [TLDA/README.md](TLDA/README.md)
2. Open `the-seed.sln` in Visual Studio
3. Open project in Unity Editor
4. Explore `Assets/Plugins/TWG/TLDA/`

---

### **🌐 Path 2: Backend Developer (Seed + STAT7)**
You want to work on STAT7 addressing, Python backend, and AI systems.

**What you'll work on:**
- STAT7 7-dimensional addressing system
- Python experiments and validation
- Living Dev Agent (AI) integration
- WebSocket communication
- Database and data models

**Start Here:**
1. Read: [SEED/README.md](SEED/README.md)
2. Read: [SEED/STAT7_VALIDATION_RESULTS.md](SEED/STAT7_VALIDATION_RESULTS.md)
3. Run: `python run_stat7.py` (launches STAT7 system)
4. Run experiments: `python scripts/run_exp_phase1.py --quick`

---

### **🔗 Path 3: Integration Developer (Bridges)**
You want to connect Unity and Python systems via WebSocket/REST APIs.

**What you'll work on:**
- WebSocket protocols and communication
- REST API design and implementation
- 7D→3D visualization projections
- Cross-system data schemas
- Event coordination

**Start Here:**
1. Read: [BRIDGES/README.md](BRIDGES/README.md)
2. Read: [BRIDGES/WEBSOCKET_PROTOCOL.md](BRIDGES/WEBSOCKET_PROTOCOL.md)
3. Run: `python web/launchers/run_stat7_visualization.py`
4. Study: `websocket/stat7-websocket.js`

---

### **🔐 Path 4: Security/DevOps Engineer (CI/CD + Security)**
You want to set up pipelines, security scanning, and deployment automation.

**What you'll work on:**
- GitHub Actions workflows
- Security scanning and patching
- CI/CD pipeline configuration
- Deployment automation
- Monitoring and alerting

**Start Here:**
1. Read: [API/SECURITY.md](API/SECURITY.md)
2. Read: [DEVELOPMENT/CI_CD.md](DEVELOPMENT/CI_CD.md)
3. Review: `.github/workflows/`
4. Run: `./scripts/validate-documentation-structure.ps1`

---

---

## 🚀 **Quick Test Run (Pick One)**

### **Option 1: STAT7 Visualization (5 minutes)** ⭐ RECOMMENDED
Perfect for your first experience with The Seed.

```bash
cd E:/Tiny_Walnut_Games/the-seed
python web/launchers/run_stat7_visualization.py
```

**Then in your browser:**
1. Opens 3D visualization at `localhost:8765`
2. Type `exp01` to see STAT7 entities being generated
3. Type `continuous` for real-time entity generation
4. Type `help` for other commands

**What you'll see:**
- 7-dimensional addressing system in action
- Real-time entity creation and visualization
- Performance metrics showing query speeds (sub-microsecond)

---

### **Option 2: Python Experiments (5 minutes)**
Validate that STAT7 experiments are working.

```bash
cd E:/Tiny_Walnut_Games/the-seed
python scripts/run_exp_phase1.py --quick
```

**Expected Output:**
```
✅ EXP-01: Address Uniqueness     PASSED
✅ EXP-02: Retrieval Efficiency   PASSED
✅ EXP-03: Dimension Necessity    PASSED
✅ EXP-04: Scalability            PASSED
...
All experiments passed!
```

---

### **Option 3: Run Python Tests (2 minutes)**
```bash
cd E:/Tiny_Walnut_Games/the-seed
python -m pytest tests/test_stat7.py -v
```

**Expected Output:**
```
test_stat7_addressing PASSED           [ 20%]
test_entity_creation PASSED            [ 40%]
test_determinism PASSED                [ 60%]
test_performance PASSED                [ 80%]
test_integration PASSED                [100%]

5 passed in 1.23s ✅
```

---

### **Option 4: Open in Unity (10 minutes)**
1. Open Unity Hub
2. Open project: `E:/Tiny_Walnut_Games/the-seed`
3. Let Unity import all packages (~2-3 min)
4. Navigate to `Assets/Plugins/TWG/TLDA/`
5. Explore the game systems
6. Try: Window → General → Test Runner (run TLDA tests)

---

## 🏗️ **Project Structure Overview**

```
the-seed/
├── docs/                           # 📚 Canonical Documentation (ALWAYS CHECK HERE FIRST)
│   ├── GETTING_STARTED.md          # ← You are here
│   ├── API/
│   │   ├── SECURITY.md             # Security policies & implementation
│   │   ├── REST_API.md             # REST API reference
│   │   └── README.md
│   ├── SEED/
│   │   ├── README.md               # Seed system overview
│   │   ├── STAT7_VALIDATION_RESULTS.md  # Validation proof
│   │   ├── STAT7_ADDRESSING.md     # STAT7 specification
│   │   └── EXPERIMENTS.md          # Experiment catalog
│   ├── TLDA/
│   │   ├── README.md               # TLDA/Unity overview
│   │   └── UNITY_INTEGRATION.md    # How to integrate with Unity
│   ├── BRIDGES/
│   │   ├── README.md               # Bridge systems overview
│   │   └── WEBSOCKET_PROTOCOL.md   # WebSocket specification
│   └── DEVELOPMENT/
│       ├── README.md               # Development guidelines
│       ├── TESTING.md              # How to write and run tests
│       └── CI_CD.md                # Pipeline and automation
│
├── Assets/                         # 🎮 Unity Project Files
│   ├── Plugins/TWG/TLDA/           # TLDA core systems
│   ├── Resources/                  # Game assets
│   └── Editor/                     # Editor scripts
│
├── packages/com.twg.the-seed/      # 🌐 Python/C# Packages
│   ├── seed/engine/                # STAT7 core + experiments
│   ├── seed/docs/                  # Seed documentation
│   └── warbler-core/               # Warbler NPC system
│
├── web/                            # 🔗 Bridge Layer
│   ├── server/                     # WebSocket servers
│   ├── js/                         # JavaScript visualization
│   ├── launchers/                  # Startup scripts
│   └── stat7threejs.html           # 3D visualization
│
├── tests/                          # 🧪 Test Suites (50+ tests)
│   ├── test_stat7*.py              # STAT7 tests
│   ├── test_api*.py                # API tests
│   └── test_integration*.py        # Integration tests
│
├── scripts/                        # 🛠️ Automation & Utilities
│   ├── run_exp_phase1.py           # Run STAT7 experiments
│   ├── validate-documentation-structure.ps1  # Doc validation
│   └── *.py                        # Other utilities
│
└── .github/workflows/              # ⚙️ GitHub Actions CI/CD
    ├── test.yml                    # Run tests
    ├── security.yml                # Security scanning
    └── deploy.yml                  # Deployment automation
```

---

## 📊 **Three Independent Systems (Keep Them Separate)**

**⚠️ IMPORTANT**: The Seed has three distinct systems that rarely interact directly:

| System | Language | Purpose | Location | Learn From |
|--------|----------|---------|----------|-----------|
| **TLDA** | C#/Unity | Game engine, gameplay mechanics, UI | `Assets/` | [TLDA/README.md](TLDA/README.md) |
| **STAT7** | Python | 7D addressing, validation, experiments | `packages/com.twg.the-seed/seed/` | [SEED/README.md](SEED/README.md) |
| **Bridges** | Python/JS | WebSocket/REST APIs, visualization | `web/` | [BRIDGES/README.md](BRIDGES/README.md) |

**When to use each:**
- Use **TLDA** for gameplay, UI, and game logic
- Use **STAT7** for addressing, entity management, and data models
- Use **Bridges** to connect TLDA and STAT7 via WebSocket/REST

---

---

## 🧪 **Running Tests**

### **All Tests (Everything at Once):**
```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=packages/com.twg.the-seed
```

---

### **STAT7 System Tests (Python Backend):**
```bash
# Quick validation (5 seconds)
pytest tests/test_stat7.py::test_determinism -v

# All STAT7 core tests
pytest tests/test_stat7*.py -v

# Validation experiments (10 seconds)
pytest tests/test_stat7_validation.py -v
```

---

### **API & Security Tests:**
```bash
# REST API security tests
pytest tests/test_phase6b_rest_api_security.py -v

# API contract tests
pytest tests/test_api_contract.py -v
```

---

### **Integration Tests:**
```bash
# WebSocket communication
pytest tests/test_stat7_server.py -v

# Complete end-to-end system
pytest tests/test_complete_system.py -v

# Load testing (warning: slow)
pytest tests/test_websocket_load_stress.py -v
```

---

### **Unity Tests (TLDA):**
1. Open Unity Editor
2. Window → General → Test Runner
3. Click "Run All" or select specific test suites
4. Results appear in the Test Runner panel

---

## 🔧 **Development Setup**

### **Step 1: Clone and Initialize (5 minutes)**

```bash
# Clone repository
git clone https://github.com/TinyWalnutGames/the-seed.git
cd the-seed

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r web/requirements-visualization.txt
pip install -r requirements-gpu.txt        # Optional: for GPU support
```

---

### **Step 2: Verify Installation (2 minutes)**

```bash
# Run diagnostics
python web/diagnose_stat7.py

# Check project organization
python verify_organization.py

# Quick validation test
pytest tests/test_stat7.py::test_determinism -v
```

Expected output:
```
✅ STAT7 system ready
✅ All dependencies installed
✅ Tests passing
```

---

### **Step 3: Unity Setup (if doing game development)**

1. Install Unity Hub (if not already installed)
2. Add Unity 6000.2.6f2 LTS to your library
3. Open this project from Unity Hub: `E:/Tiny_Walnut_Games/the-seed`
4. Let Unity import all packages (~2-3 minutes)
5. Check Console for any errors (should be none)

---

### **Step 4: Environment Configuration**

Create `.env` file in project root:
```bash
# JWT Security (if using REST API)
JWT_SECRET=your-very-secure-secret-key-here
JWT_EXPIRY_HOURS=24

# File Operations
SNAPSHOT_BASE_DIR=./snapshots

# Optional: GPU Support
USE_GPU=false
GPU_DEVICE=0
```

---

## 📖 **Learning Paths (Choose One)**

### **Path A: I want to understand STAT7 (Backend Developer)**

**Time**: 2-4 hours

1. ✅ Read this page (5 min) - YOU ARE HERE
2. ✅ Read [SEED/README.md](SEED/README.md) (15 min)
3. ✅ Read [SEED/STAT7_VALIDATION_RESULTS.md](SEED/STAT7_VALIDATION_RESULTS.md) (20 min)
4. ✅ Run experiments: `python scripts/run_exp_phase1.py --quick` (10 min)
5. ✅ Read [SEED/STAT7_ADDRESSING.md](SEED/STAT7_ADDRESSING.md) (30 min)
6. ✅ Study experiment code: `packages/com.twg.the-seed/seed/engine/stat7_experiments.py` (1 hour)
7. ✅ Run WebSocket server: `python run_stat7.py` (5 min)
8. ✅ Play with 3D visualization (10 min)

---

### **Path B: I want to develop in Unity (Game Developer)**

**Time**: 2-3 hours

1. ✅ Read this page (5 min) - YOU ARE HERE
2. ✅ Read [TLDA/README.md](TLDA/README.md) (20 min)
3. ✅ Open `the-seed.sln` in Visual Studio (5 min)
4. ✅ Open the-seed in Unity Editor (3 min)
5. ✅ Navigate to `Assets/Plugins/TWG/TLDA/` and explore (15 min)
6. ✅ Read [TLDA/UNITY_INTEGRATION.md](TLDA/UNITY_INTEGRATION.md) (20 min)
7. ✅ Run Unity Test Runner and see tests pass (5 min)
8. ✅ Study a small gameplay system (30 min)

---

### **Path C: I want to set up CI/CD and Security (DevOps Engineer)**

**Time**: 2-3 hours

1. ✅ Read this page (5 min) - YOU ARE HERE
2. ✅ Read [API/SECURITY.md](API/SECURITY.md) (30 min)
3. ✅ Review `.github/workflows/` structure (15 min)
4. ✅ Read [DEVELOPMENT/CI_CD.md](DEVELOPMENT/CI_CD.md) (30 min)
5. ✅ Run validation script: `./scripts/validate-documentation-structure.ps1` (5 min)
6. ✅ Study GitHub Actions workflows (30 min)
7. ✅ Set up branch protection rules (10 min)

---

## 🆘 **Getting Help**

### **Where to Find Information:**

| Problem | Find Help In |
|---------|-------------|
| How do I run STAT7? | [SEED/README.md](SEED/README.md) |
| How do I use Unity? | [TLDA/README.md](TLDA/README.md) |
| How do I fix a test? | [DEVELOPMENT/TESTING.md](DEVELOPMENT/TESTING.md) |
| How is security set up? | [API/SECURITY.md](API/SECURITY.md) |
| How does WebSocket work? | [BRIDGES/WEBSOCKET_PROTOCOL.md](BRIDGES/WEBSOCKET_PROTOCOL.md) |
| What's the project structure? | [ARCHITECTURE.md](ARCHITECTURE.md) |
| How do I set up CI/CD? | [DEVELOPMENT/CI_CD.md](DEVELOPMENT/CI_CD.md) |

---

### **Troubleshooting:**

**Q: WebSocket connection failed**
- Check port 8765 is not in use: `netstat -ano | findstr :8765`
- Restart WebSocket server: `python run_stat7.py`
- Check firewall settings

**Q: Python "ModuleNotFoundError"**
- Verify venv is activated: `which python` should show `.venv` path
- Reinstall dependencies: `pip install -r web/requirements-visualization.txt`

**Q: Unity won't compile**
- Check .NET version matches requirements (4.7.1+)
- Delete `Library/` folder and let Unity reimport
- Check Console panel for specific errors

**Q: Tests failing**
- Make sure virtual environment is activated
- Run: `pip install -r requirements-gpu.txt` to ensure all deps
- Check that ports 8765, 8000 are available

---

## 🎯 **Your First Contribution**

1. **Choose your path** (Backend/Game/DevOps)
2. **Follow the learning path** above
3. **Run the tests** to verify everything works
4. **Make a small change** (fix a typo, add a comment, write a test)
5. **Create a pull request** with your change

**Example PR ideas:**
- Fix typo in documentation
- Add a unit test for an untested function
- Improve error message in existing code
- Update a README with clearer instructions
- Add a code comment explaining a complex section

---

## ✨ **Success Checklist**

You're ready to start contributing when:

- [ ] You can run `pytest tests/test_stat7.py -v` successfully
- [ ] You understand which of the 3 systems you're working on
- [ ] You know where to find documentation for your system
- [ ] You've read at least one core documentation file for your system
- [ ] You've run a quick test/visualization and seen it work
- [ ] You understand the folder structure

---

## 📞 **Quick Command Reference**

```bash
# See what's happening
python web/diagnose_stat7.py           # System health check
python verify_organization.py           # Check project structure

# Run things
python run_stat7.py                    # Start STAT7 backend
python web/launchers/run_stat7_visualization.py  # 3D visualization
python scripts/run_exp_phase1.py --quick  # Run experiments

# Test things
pytest tests/ -v                       # Run all tests
pytest tests/test_stat7.py::test_determinism -v  # Single test

# Validate
./scripts/validate-documentation-structure.ps1  # Check docs

# Debug
python web/debug_websocket_data.py     # WebSocket debugging
```

---

**Welcome to The Seed! 🚀**

Start with **Option 1: STAT7 Visualization** above for the best first experience.

Then pick your learning path and dive in!
