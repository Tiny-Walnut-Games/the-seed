---
description: Repository Information Overview
alwaysApply: true
---

# The Seed - Multiverse Simulation System Information

## Repository Summary

**The Seed** is an open-source multiverse simulation framework providing STAT7 (7-dimensional addressing) for interconnected virtual worlds. It integrates three main systems: TLDA (Unity game engine layer), Seed (Python backend with AI), and Bridge components for cross-system communication. The project targets seamless player interaction across different game universes with narrative latency optimization.

**Repository Type**: Multi-project hybrid (Unity + Python + JavaScript/Node + C# + Web)
**License**: MIT
**Main Vision**: Decentralized virtual multiverse backbone with developer-friendly addressing and narrative coordination

## Repository Structure

### Main Components
- **Assets/** - Unity game assets, editor tools, plugins, and UI Toolkit resources
- **packages/** - npm workspaces and NuGet packages (Ollama, System libraries, CSharpToJsonSchema)
- **web/** - Python/JavaScript visualization layer with WebSocket servers
- **tests/** - Comprehensive test suite covering 46+ test scenarios
- **scripts/** - Automation and CI/CD utilities
- **docs/** - Architecture, API, and development documentation
- **.github/** - Workflows, issue templates, and CI configuration
- **ProjectSettings/** - Unity project configuration and build settings
- **Library/** - Unity build cache and dependencies

---

## Projects

### 1. TLDA (Unity Game Engine)
**Configuration Files**: 	the-seed.sln, Assembly-CSharp.csproj, ProjectSettings/ProjectVersion.txt

#### Language & Runtime
- **Language**: C# / C++
- **Runtime**: Unity 6000.2.6f2 (LTS)
- **Build System**: MSBuild (Visual Studio project files)
- **Package Manager**: NuGet (.NET Framework)

#### Key Dependencies
- **Main**: Unity.Entities, Unity.Collections, Unity.Transforms, Unity.Scenes
- **Plugins**: Facepunch.Steamworks (2.3.3), CSharpToJsonSchema (3.10.1)
- **System**: System.Text.Json (9.0.0), System.IO.Pipelines (9.0.0), System.Memory (4.5.5)
- **Editor**: Unity.PerformanceTesting, LivingDevAgent.Editor, TWG.TLDA.TestSuite.Editor

#### Build & Installation
`ash
# Open in Unity Hub or load .sln in Visual Studio
# Build configuration: Release/Debug via Visual Studio or Unity Editor
# Asset location: Assets/TWG/TLDA/ (core game mechanics)
# Steam integration: Facepunch.Steamworks bridge
`

#### Testing
- **Framework**: Unity Test Runner
- **Test Location**: Assets/Editor/ and packages/com.twg.the-seed/The Living Dev Agent/tests/
- **Configuration**: Unity test assemblies with editor-only scripts
- **Run**: Through Unity Editor Test Runner or command line

---

### 2. The Seed (Python Backend)
**Configuration Files**: pyproject.toml, pytest.ini, 
equirements-gpu.txt

#### Language & Runtime
- **Language**: Python
- **Version**: >=3.9
- **Build System**: setuptools, wheel
- **Package Manager**: pip, setuptools

#### Core Dependencies
**ML/AI Stack**: 
- PyTorch (>=2.0.0), torchvision (>=0.15.0)
- Transformers (>=4.30.0), sentence-transformers (>=2.2.0)
- FAISS (CPU/GPU variants, >=1.7.0), Datasets (>=2.12.0)

**Backend/Web**:
- FastAPI (>=0.100.0), uvicorn (>=0.22.0)
- websockets (>=11.0), aiohttp (>=3.8.0)
- Pydantic (>=2.0), PyYAML (>=6.0)

**Utilities**:
- NumPy (>=1.20), psutil (>=5.9.0), requests (>=2.28.0)
- Click (>=8.1.0), tqdm (>=4.64.0), python-multipart (>=0.0.6)

**Testing**: pytest (>=7.0), pytest-cov (>=4.0), pytest-xdist (>=3.0)

#### Build & Installation
```Bash
# Install dependencies
pip install -r pyproject.toml
# or for GPU support:
pip install -r requirements-gpu.txt

# Run STAT7 system
python run_stat7.py

# Run specific experiments
python packages/com.twg.the-seed/seed/engine/run_exp_phase1.py --quick
```

#### Main Entry Points
- run_stat7.py - STAT7 system launcher
- start_stat7.py - Alternate startup
- run_tests.py - Test runner
- web/launchers/run_stat7_visualization.py - Visualization server
- web/server/stat7wsserve.py - WebSocket server (28KB, main server)

#### Testing
- **Framework**: pytest
- **Test Location**: 	ests/ (16+ test files covering 46+ scenarios)
- **Test Categories**: Unit, integration, E2E, load/stress, mathematical validation
- **Markers**: exp01-exp10 (experiments), unit, integration, e2e, load, math, robustness
- **Configuration**: pytest.ini with comprehensive test discovery
- **Run**: pytest tests/ or python run_tests.py

---

### 3. Web/WebSocket Layer
**Configuration Files**: web/server/*.py, websocket/, web/js/

#### Language & Runtime
- **Languages**: Python + JavaScript
- **Python Servers**: FastAPI + uvicorn + websockets
- **JavaScript**: Node.js (ES6+)

#### Components
- **stat7wsserve.py** - Main WebSocket server with async support
- **api_gateway.py** - API routing and request handling
- **event_store.py** - Event persistence layer
- **tick_engine.py** - Game tick/update cycle engine
- **governance.py** - System governance and access control
- **e2e_simulation.py** - End-to-end scenario testing

#### Visualization Stack
- **Frontend**: Three.js-based 7D visualization (stat7threejs.html)
- **Jupyter Integration**: stat7_visualization_demo.ipynb
- **Requirements**: websockets, jupyter, ipywidgets, pytest-asyncio, psutil

---

### 4. Docker Configuration
**Dockerfile**: Python 3.12-slim base image

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install -r scripts/requirements.txt
EXPOSE 8080 9998
ENV LLM_BRIDGE_MODE=gemma3
ENV LLM_ENDPOINT=http://host.docker.internal:9998
ENV WARBLER_AI_ENABLED=true
CMD ["python", "scripts/warbler_gemma3_bridge.py"]
```

**Build**: docker build -t twg-tlda-ai .
**Run**: docker run --rm -p 8080:8080 -p 9998:9998 twg-tlda-ai

---

### 5. JavaScript/Node Workspace
**Configuration**: package.json (npm workspaces)

- **Node Version**: >=18.0.0
- **Package Manager**: npm with workspaces
- **Main Packages**: 
  - Playwright MCP (0.0.37)
  - TypeScript (^5.3.0), ESLint (^9.35.0)
  - Vitest (^3.2.4), Playwright Test (^1.40.0)
- **Workspaces**: warbler-core, packs/*
- **Scripts**: build, lint, test, publish, release cycles

---

## Test Coverage & CI/CD

### Test Suite Organization
- **Total Test Files**: 16+ in 	ests/ directory
- **Test Coverage**: 46+ test scenarios across all components
- **Test Markers**: 10 experiment categories (EXP-01 to EXP-10)
- **CI Workflows**: GitHub Actions (.github/workflows/)
- **Load Testing**: WebSocket stress tests, 1000+ concurrent connection tests

### Key Test Files
- 	est_stat7.py, 	est_stat7_e2e.py, 	est_stat7_server.py
- 	est_websocket_load_stress.py - Stress testing
- 	est_complete_system.py - Integration testing
- 	est_api_contract.py - API validation
- 	est_governance_integration.py - Governance system

---

## Key Build Commands

```Bash
# Python project
pytest                                    # Run all tests
python run_stat7.py                      # Start STAT7 system
python web/launchers/run_stat7_visualization.py  # Visualization

# Node/npm workspace
npm run build --workspaces               # Build all packages
npm run test --workspaces                # Test all
npm run lint                             # ESLint check

# Docker
docker build -t twg-tlda-ai .
docker run -p 8080:8080 -p 9998:9998 twg-tlda-ai

# C#/Unity
# Open the-seed.sln in Visual Studio or Unity Editor
# Build via MSBuild or Unity Editor build pipeline
```

---

## Architecture Highlights

- **STAT7 Addressing**: 7-dimensional system (Realm, Lineage, Adjacency, Horizon, Resonance, Velocity, Density)
- **Async-First**: WebSocket communication with async/await patterns
- **Multi-Modal**: Supports Unity, Python, JavaScript, and C# components
- **AI Integration**: Living Dev Agent + Warbler NPC system
- **Narrative Optimization**: Latency reduction for cross-world entity coordination
- **Containerized**: Docker support for deployment
