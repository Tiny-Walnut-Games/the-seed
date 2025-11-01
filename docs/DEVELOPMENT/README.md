# Development Documentation

This directory contains all development guidelines, CI/CD procedures, and testing frameworks for The Seed project.

## Quick Navigation

### 📋 Getting Started
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to the project
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Developer quick reference

### 🔧 Development Practices
- **[FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)** - How code is organized
- **[MODULAR_STRUCTURE.md](MODULAR_STRUCTURE.md)** - Module architecture
- **[SWEEP_GUIDELINES.md](SWEEP_GUIDELINES.md)** - Code review sweeps

### 🧪 Testing & CI/CD (Canonical Sources)
- **[CI_CD_PIPELINE.md](CI_CD_PIPELINE.md)** - Pipeline strategy and test discovery ⭐
- **[TESTING_FRAMEWORK.md](TESTING_FRAMEWORK.md)** - pytest setup and best practices ⭐

### 📚 Phase Archives
- **[PHASE_1_FIXES/](PHASE_1_FIXES/)** - Phase 1 completion documentation (archived)

## Key Commands

### Running Tests
\\\ash
# All tests
pytest tests/ -v

# Load stress tests
pytest tests/test_websocket_load_stress.py -v

# Specific test
pytest tests/test_stat7.py::test_stat7_dimension_validation
\\\

### Building
\\\ash
# Python STAT7
python run_stat7.py

# Node workspaces
npm run build --workspaces

# Docker
docker build -t twg-tlda-ai .
\\\

## Documentation Philosophy

This directory follows a **truth-first approach**:
- Documentation reflects actual code implementation
- All references link to source code locations
- Updated before code changes (not after)
- Git history provides audit trail

## CI/CD Pipeline Overview

See [CI_CD_PIPELINE.md](CI_CD_PIPELINE.md) for complete details, but in brief:

- **Test Inventory**: 46+ tests across 3 categories
- **Discovery**: Automatic in CI/CD pipeline
- **Performance**: Validates 1000+ concurrent entities
- **Coverage**: 100% of critical paths

## Testing Framework

See [TESTING_FRAMEWORK.md](TESTING_FRAMEWORK.md) for complete details, but in brief:

- **Framework**: pytest with asyncio support
- **Configuration**: pytest.ini in repository root
- **Organization**: tests/ directory with clear naming
- **Running**: pytest tests/ -v

## Related Documentation

- **Architecture**: See docs/ARCHITECTURE.md
- **STAT7 System**: See docs/SEED/STAT7_ADDRESSING.md
- **Experiments**: See docs/SEED/EXPERIMENTS.md
- **Security**: See docs/Shared/API/SECURITY.md

---

**Status**: Phase 2-3 consolidation complete. Canonical sources established.
