---
description: Repository Information Overview
alwaysApply: true
---

# The Seed - Multiverse Simulation System

## Repository Summary

**The Seed** is an open-source multiverse simulation framework providing STAT7 (7-dimensional addressing) for interconnected virtual worlds. It integrates three main systems: TLDA (Unity game engine), Seed (Python backend), and Bridge components. Targets seamless player interaction across different game universes with narrative latency optimization and decentralized architecture.

**Type**: Multi-project hybrid (Unity C# + Python + JavaScript/Node)  
**License**: MIT  
**targetFramework**: Playwright (frontend E2E testing)

## Repository Structure

- **Assets/** - Unity game assets, editor tools, plugins
- **packages/** - npm workspaces, NuGet packages, Python seed engine
- **web/** - Python/JavaScript WebSocket servers and visualization
- **tests/** - Comprehensive test suite (46+ scenarios)
- **scripts/** - Automation and CI/CD utilities
- **docs/** - Canonical architecture and API documentation
  - **Shared/** - Cross-system APIs and shared resources
  - **SEED/** - Python backend documentation
  - **TLDA/** - Unity game engine documentation
  - **BRIDGES/** - WebSocket and inter-system protocols
  - **DEVELOPMENT/** - Development guidelines, CI/CD, and testing
  - **ARCHIVE/** - Historical documentation snapshots
- **ProjectSettings/** - Unity project configuration

## Projects

### 1. TLDA (Unity Game Engine - C#)

**Configuration**: the-seed.sln, Assembly-CSharp.csproj

**Language**: C# with Unity 6+  
**Build System**: MSBuild (Visual Studio)  
**Package Manager**: NuGet

**Core Dependencies**:
- Unity.Entities, Unity.Collections, Unity.Transforms
- Facepunch.Steamworks (2.3.3), CSharpToJsonSchema (3.10.1)
- System.Text.Json (9.0.0), System.IO.Pipelines (9.0.0)

**Main Components**:
- Companion battle system, Warbler NPC integration
- Scribe documentation tools, GameManager
- Steam bridge, visualization bridges

**Testing**: Unity Test Runner, Assets/Editor/ test assemblies

---

### 2. Seed (Python Backend)

**Configuration**: pyproject.toml, pytest.ini, requirements.txt

**Language**: Python >=3.9  
**Build System**: setuptools, wheel  
**Package Manager**: pip

**Core Stack**:
- PyTorch (>=2.0.0), Transformers (>=4.30.0), FAISS (>=1.7.0)
- FastAPI (>=0.100.0), uvicorn, websockets (>=11.0)
- Pydantic (>=2.0), NumPy, pytest

**Main Components**:
- STAT7 addressing system (7-dimensional coordinates)
- Validation experiments (EXP-01 through EXP-10)
- WebSocket server, API gateway, event store
- Tick engine, governance, RAG bridge

**Entry Points**:
- run_stat7.py - STAT7 system launcher
- stat7wsserve.py - WebSocket server (28KB)
- Visualization: run_stat7_visualization.py

**Testing**: pytest with 16+ test files covering 46+ scenarios

---

### 3. Web/WebSocket Layer

**Languages**: Python (FastAPI/uvicorn) + JavaScript (Node.js)

**Server Components**:
- stat7wsserve.py - WebSocket streaming
- api_gateway.py - REST routing
- event_store.py - Persistence
- tick_engine.py - Game loop
- governance.py - Access control

**Frontend**: Three.js-based 7D visualization (stat7threejs.html)

**Requirements**: websockets, jupyter, ipywidgets, pytest-asyncio

---

### 4. JavaScript/Node Workspace

**Configuration**: package.json (npm workspaces)

**Runtime**: Node.js >=18.0.0

**Key Packages**:
- Playwright MCP (0.0.37), TypeScript (^5.3.0)
- Vitest (^3.2.4), ESLint (^9.35.0)

**Workspaces**: warbler-core, packs/*

---

### 5. Docker Configuration

**Dockerfile**: Python 3.12-slim base

**Build**: docker build -t twg-tlda-ai .

**Ports**: 8080, 9998

**Environment**:
- LLM_BRIDGE_MODE=gemma3
- LLM_ENDPOINT=http://host.docker.internal:9998
- WARBLER_AI_ENABLED=true

---

## Documentation

**Canonical Location**: docs/ with single source of truth per topic

### System Documentation
- docs/GETTING_STARTED.md - Developer onboarding
- docs/ARCHITECTURE.md - System overview
- docs/SEED/STAT7_ADDRESSING.md - 7D addressing specification
- docs/SEED/EXPERIMENTS.md - Validation test suite

### Shared Resources
- docs/Shared/API/ - Cross-system API references
- docs/Shared/API/SECURITY.md - Security policies

### Development & Operations
- docs/DEVELOPMENT/CI_CD_PIPELINE.md - Test discovery and pipeline strategy
- docs/DEVELOPMENT/TESTING_FRAMEWORK.md - pytest setup and best practices
- docs/DEVELOPMENT/CONTRIBUTING.md - Contribution guidelines

### Inter-System Communication
- docs/BRIDGES/ - WebSocket and cross-system protocols

**Truth-First Approach**: All documentation reflects actual code implementation with references to source locations.

---

## Build & Test Commands

### PowerShell (Windows - Recommended)

```powershell
# Setup (one time)
Set-Location "E:\Tiny_Walnut_Games\the-seed"
pip install -r requirements.txt

# HTTP Auth Server with TEST MODE (start in one PowerShell tab)
$env:STAT7_TEST_MODE = "true"
python web/server/run_server.py

# Run E2E tests (in another PowerShell tab while server is running)
python -m pytest tests/test_stat7_auth_http_endpoints.py::TestTestModeAdminAccess -v
python -m pytest tests/test_stat7_auth_http_endpoints.py -k TestTestMode -v

# Python - STAT7 system (optional)
python -m pytest tests/ -v
python -m pytest tests/test_websocket_load_stress.py -v
python run_stat7.py
python web/launchers/run_stat7_visualization.py

# Node/npm (if needed)
npm run build --workspaces
npm run test --workspaces
```

### Docker (Optional - not required for initial setup)

```bash
# Build Docker image
docker build -t twg-tlda-ai .

# Run with TEST MODE enabled (for E2E testing)
STAT7_TEST_MODE=true docker-compose up -d

# Run without TEST MODE (production)
STAT7_TEST_MODE=false docker-compose up -d

# Check logs
docker-compose logs mmo-orchestrator | grep "TEST MODE"
```

### Unity

```
Open the-seed.sln in Visual Studio or Unity Editor
```

---

## Key Architecture Features

- **STAT7 Addressing**: 7-dimensional system (Realm, Lineage, Adjacency, Horizon, Luminosity, Polarity, Dimensionality)
- **Comprehensive Testing**: 46+ tests covering load stress, integration, and feature validation
- **Async-First**: WebSocket communication with async/await patterns
- **Multi-Modal**: Unity, Python, JavaScript, C# integration
- **Validated**: Phase 1 experiments proven at 1000+ concurrent entities
- **Hybrid Encoding**: Maps legacy systems to STAT7 coordinates

---

## Consolidation Status

- **Phase 1**: ✅ Complete (Security, Getting Started, repo.md)
- **Phase 2**: ✅ Complete (STAT7 addressing, experiments, directory restructuring)
- **Phase 3**: ✅ Complete (CI/CD pipeline, testing framework consolidation)
- **Phase 4**: ✅ Complete (Archive cleanup, documentation consolidation)

**Documentation Fragmentation**: Reduced from 54 scattered files to ~15 canonical locations (72% reduction).

**Truth Status**: All information validated against current code implementation.
