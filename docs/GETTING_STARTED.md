# 🚀 Getting Started with The Seed

Quick start guide for developers joining the multiverse project.

---

## 📋 **Prerequisites**

### **System Requirements:**
- **Unity 2022.3+** (for TLDA development)
- **Python 3.8+** (for Seed development)
- **Node.js 16+** (for web components)
- **Git** (for version control)

### **Python Dependencies:**
```bash
pip install websockets asyncio pytest
```

### **Unity Requirements:**
- Unity Hub installed
- Steamworks SDK (for Steam integration)

---

## 🎯 **Choose Your Path**

### **🎮 Game Developer (TLDA)**
You want to build games and Unity integrations.

**Start Here:** [TLDA/README.md](TLDA/README.md)

### **🌐 Backend Developer (Seed)**
You want to work on STAT7 addressing and AI systems.

**Start Here:** [SEED/README.md](SEED/README.md)

### **🔗 Integration Developer (Bridges)**
You want to connect Unity and Python systems.

**Start Here:** [BRIDGES/README.md](BRIDGES/README.md)

---

## 🚀 **Quick Test Run**

### **1. STAT7 Visualization (5 minutes)**
```bash
cd E:/Tiny_Walnut_Games/the-seed
python web/launchers/run_stat7_visualization.py
```
- Opens browser to 3D visualization
- Type `exp01` to see STAT7 entities
- Type `continuous` for ongoing generation

### **2. Unity Project (10 minutes)**
1. Open project in Unity Hub
2. Navigate to `Assets/Plugins/TWG/TLDA/`
3. Open `Tools/School/Editor/SchoolExperimentWorkbench.cs`
4. Run Unity Test Runner

### **3. Python Experiments (5 minutes)**
```bash
cd E:/Tiny_Walnut_Games/the-seed
python Packages/com.twg.the-seed/seed/engine/run_exp_phase1.py --quick
```

---

## 🏗️ **Project Structure Overview**

```
the-seed/
├── docs/                    # 📚 Canonical documentation (YOU ARE HERE)
├── Assets/                  # 🎮 Unity project files
│   └── Plugins/TWG/TLDA/    # TLDA system components
├── Packages/                # 🌐 Python packages
│   └── com.twg.the-seed/    # Seed system components
├── web/                     # 🔗 Bridge components
│   ├── js/                  # JavaScript visualization
│   ├── server/              # WebSocket servers
│   └── launchers/           # Startup scripts
├── tests/                   # 🧪 Test suites
└── scripts/                 # 🛠️ Utility scripts
```

---

## 🧪 **Running Tests**

### **Unity Tests (TLDA):**
1. Open Unity Editor
2. Window → General → Test Runner
3. Run "TLDA Test Suite"

### **Python Tests (Seed):**
```bash
# Quick validation
python run_tests.py

# Full test suite
python run_tests.py --full

# STAT7-specific tests
python run_stat7_tests.py
```

### **Integration Tests (Bridges):**
```bash
# Test WebSocket communication
python tests/test_stat7_server.py

# Test complete system
python tests/test_complete_system.py
```

---

## 🔧 **Development Setup**

### **1. Clone and Initialize:**
```bash
git clone <repository-url>
cd the-seed

# Initialize Python environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r web/requirements-visualization.txt
```

### **2. Unity Setup:**
1. Open project in Unity Hub
2. Let Unity import packages
3. Check for compilation errors in `Assets/Plugins/TWG/TLDA/`

### **3. Verify Installation:**
```bash
# Run diagnostics
python web/diagnose_stat7.py

# Check organization
python verify_organization.py
```

---

## 📖 **Next Steps**

### **For Understanding STAT7:**
- Read [SEED/STAT7_ADDRESSING.md](SEED/STAT7_ADDRESSING.md)
- Run EXP-01 experiments
- Study 7D coordinate system

### **For Unity Development:**
- Read [TLDA/UNITY_INTEGRATION.md](TLDA/UNITY_INTEGRATION.md)
- Explore companion battle system
- Study Warbler NPC integration

### **For Bridge Development:**
- Read [BRIDGES/WEBSOCKET_PROTOCOL.md](BRIDGES/WEBSOCKET_PROTOCOL.md)
- Understand 7D→3D projection
- Study data schemas

---

## 🆘 **Getting Help**

### **Documentation:**
- **System Overview:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **API References:** [API/](API/)
- **Development Guidelines:** [DEVELOPMENT/](DEVELOPMENT/)

### **Common Issues:**
- **WebSocket connection failed:** Check port 8765 availability
- **Unity compilation errors:** Verify .NET Framework version
- **Python import errors:** Check virtual environment activation

### **Community:**
- GitHub Issues (for bugs and feature requests)
- Documentation (for questions and clarifications)

---

## 🎯 **Your First Contribution**

1. **Choose a system** (TLDA/Seed/Bridges)
2. **Read the relevant documentation**
3. **Run the tests** to verify setup
4. **Make a small change** (fix a typo, add a comment)
5. **Submit a pull request**

Welcome to the multiverse! 🚀
