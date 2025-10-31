# SWEEP.md - The Seed Project Commands & Preferences

## Project Overview
**The Seed** - A fractal, multidimensional addressing and retrieval system for infinitely extensible data and narrative storage with STAT7 integration.

## Development Commands

### Python/STAT7 Commands
```bash
# Run STAT7 visualization server
python run_stat7.py
python start_stat7.py

# Start STAT7 WebSocket server
python web/server/stat7wsserve.py

# Run tests
python run_tests.py
python -m pytest tests/ -v
python -m pytest tests/test_stat7*.py -v

# Run specific STAT7 tests
python run_stat7_tests.py
python -m pytest tests/ -m "exp01 or exp02 or stat7" -v

# Validate workflows and organization
python validate_workflows.py
python verify_organization.py
python verify_behavioral_system.py
```

### Node.js/Warbler Commands
```bash
# Build all workspaces
npm run build

# Run tests
npm run test
npm run test:warbler

# Lint code
npm run lint

# Validate Warbler packs
npm run pack:validate

# Simulate Warbler behavior
npm run warbler:simulate

# Publish packages
npm run publish:core
npm run publish:packs
npm run release:all
```

### Unity Commands
```bash
# Open Unity project (from project root)
# Use Unity Hub to open the-seed project

# Unity test runner
# Window > General > Test Runner
# Run all tests or specific STAT7-related tests
```

## Code Style Preferences

### Python
- **Line length**: 100 characters
- **Python version**: 3.9+
- **Formatter**: Black
- **Linter**: flake8, mypy
- **Test framework**: pytest
- **Docstrings**: Google style preferred

### TypeScript/JavaScript
- **Line length**: 100 characters
- **Node version**: 18.0.0+
- **Formatter**: ESLint with TypeScript rules
- **Test framework**: Vitest, Playwright

### C# (Unity)
- **Style**: Microsoft C# conventions
- **Target**: C# 10.0+
- **Namespace**: TWG.TLDA.*
- **Test framework**: Unity Test Framework

## Project Structure

### Core Directories
- `packages/com.twg.the-seed/seed/engine/` - STAT7 core engine
- `web/server/` - STAT7 WebSocket server and visualization
- `Assets/Plugins/TWG/TLDA/` - Unity TLDA integration
- `tests/` - Python test suite
- `docs/` - Project documentation

### STAT7 System
- **STAT7 Coordinates**: 7-dimensional addressing space
- **Realms**: companion, badge, sponsor_ring, achievement, pattern, faculty, void
- **Horizons**: genesis, emergence, peak, decay, crystallization, archived
- **Polarities**: logic, creativity, order, chaos, balance, achievement, etc.

## Testing Strategy

### Test Markers (pytest)
- `exp01-exp10`: STAT7 experiment-specific tests
- `math`: Mathematical validation tests
- `robustness`: Stress and resilience tests
- `integration`: Cross-system integration tests
- `slow`: Long-running tests

### Coverage Requirements
- Target: 85%+ coverage on core STAT7 engine
- Exclude: tests, __pycache__, site-packages
- Report: HTML and terminal output

## STAT7 Visualization

### WebSocket Server
- **Port**: 8765
- **URL**: ws://localhost:8765
- **Visualization**: http://localhost:8000/stat7threejs.html

### Available Experiments
- **Semantic Fidelity Proof**: Tests narrative clustering
- **Resilience Testing**: Tests system under stress
- **EXP-01**: Address uniqueness validation
- **Continuous Generation**: Real-time entity creation

## Development Workflow

### Before Committing
1. Run `python validate_workflows.py`
2. Run `npm run lint` and `python -m black .`
3. Run tests: `python run_tests.py` and `npm run test`
4. Verify STAT7 server starts: `python run_stat7.py`

### STAT7 Entity Creation
1. Extend `STAT7Entity` base class
2. Implement `_compute_stat7_coordinates()`
3. Define `to_collectible_card_data()`
4. Add appropriate test coverage

### File Intent Tagging
When creating new files, include intent comments:
```python
# INTENT: Core STAT7 coordinate computation
# PURPOSE: Provides deterministic address generation
# DEPENDENCIES: stat7_entity.py, hashlib
# STAT7_COORD: realm=system, lineage=0, adjacency=high, horizon=genesis
```

## Environment Setup

### Python Dependencies
- Core: pydantic, numpy, pyyaml
- ML: torch, transformers, sentence-transformers
- Web: fastapi, uvicorn, websockets
- Testing: pytest, pytest-cov, pytest-xdist

### Node.js Dependencies
- Core: TypeScript, ESLint, Vitest
- MCP: @playwright/mcp, js-yaml
- Testing: @playwright/test

## Debugging & Troubleshooting

### STAT7 Server Issues
- Check port 8765 availability
- Verify Python path includes seed/engine
- Run `python diagnose_stat7.py` for diagnostics

### Unity Integration
- Verify TLDA package import in Package Manager
- Check C# version compatibility (C# 10.0+)
- Run Unity Test Runner for TLDA tests

### Test Failures
- Check pytest configuration in pyproject.toml
- Verify test markers are correctly applied
- Run with `-v` flag for detailed output

## Performance Considerations

### STAT7 Scaling
- Batch entity creation for better performance
- Use WebSocket buffering for visualization
- Monitor memory usage during large experiments

### Unity Performance
- Use object pooling for TLDA entities
- Optimize STAT7 coordinate calculations
- Profile with Unity Profiler

## Security Notes

### STAT7 NFT Integration
- User opt-in required for blockchain features
- Verify contract addresses before minting
- Secure IPFS hash handling

### Data Privacy
- Anonymize user data in experiments
- Secure WebSocket connections in production
- Validate all user inputs

## AI Assistant Integration

### Context Files
- `agent-profile.yaml` - AI behavior configuration
- `living-dev-agent.yaml` - Development agent settings
- `TWG-Copilot-Agent.yaml` - Code generation preferences

### Preferred Patterns
- Use absolute paths for file operations
- Include intent comments in complex functions
- Tag files with STAT7 coordinates for metadata
- Update SWEEP.md when adding new commands

---

*Last updated: 2025-10-30*
*Maintained by: Living Dev Agent System*
