---
title: Testing Framework & Guidelines
order: 3
---

# Testing Framework & Guidelines

## Test Framework Setup

**Framework**: pytest (Python 3.9+)  
**Configuration**: pytest.ini in repository root  
**Test Location**: tests/ directory  
**Test Naming**: test_*.py or *_test.py

## Test File Organization

\\\
tests/
├── test_stat7.py                    # Core STAT7 tests
├── test_stat7_e2e.py               # End-to-end scenarios
├── test_websocket_load_stress.py    # Performance (1000+ entities)
├── test_complete_system.py          # Full integration
├── test_event_store.py              # Persistence
├── test_tick_engine.py              # Game loop
├── test_api_contract.py             # REST API contracts
├── test_governance_integration.py    # Security/access control
├── test_phase2_warbler_integration.py
├── test_phase3_semantic_search.py
├── test_phase4_multi_turn_dialogue.py
├── test_phase5_bridge_integration.py
├── test_phase6b_rest_api.py
├── test_phase6c_web_dashboard.py
├── test_phase6c_narrative_audit.py
├── test_phase6d_reproducibility.py
├── websocket/                       # WebSocket-specific tests
└── __init__.py
\\\

## Writing Tests

### Test Function Template

\\\python
def test_stat7_dimension_validation():
    \"\"\"Test that all 7 STAT7 dimensions initialize correctly.\"\"\"
    entity = STAT7Entity(
        realm="prime",
        lineage=1,
        adjacency=0.8,
        horizon="emergence",
        luminosity=0.95,
        polarity="positive",
        dimensionality=3
    )
    assert entity.realm == "prime"
    assert entity.validate()
\\\

### Async Test Pattern

\\\python
import pytest

@pytest.mark.asyncio
async def test_websocket_event_broadcast():
    \"\"\"Test WebSocket event broadcasting.\"\"\"
    server = WebSocketServer()
    await server.initialize()
    event = {"event_type": "test", "data": {}}
    await server.broadcast_event(event)
    # Assertions...
\\\

## Running Tests

### Basic Commands

\\\ash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific file
pytest tests/test_stat7.py -v

# Run specific test
pytest tests/test_stat7.py::test_stat7_dimension_validation -v

# Run tests matching pattern
pytest tests/ -k "stat7" -v

# Run with coverage report
pytest tests/ --cov=packages/com.twg.the-seed/seed --cov-report=html
\\\

### Performance & Load Tests

\\\ash
# Run load stress tests (takes 5-10 minutes)
pytest tests/test_websocket_load_stress.py -v -s

# Run specific load scenario
pytest tests/test_websocket_load_stress.py::test_1000_concurrent_entities -v
\\\

## Test Dependencies

From pyproject.toml and requirements.txt:

\\\
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-timeout>=2.1.0
pytest-mock>=3.10.0
\\\

## Pytest Configuration

From pytest.ini:

\\\ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = --tb=short --strict-markers
markers =
    asyncio: marks tests as async (deselect with '-m "not asyncio"')
    slow: marks tests as slow (deselect with '-m "not slow"')
    load: marks tests as load/stress tests
\\\

## Test Categories

### 🔴 Critical Tests (Must Pass)
- test_stat7.py - Core functionality
- test_complete_system.py - Integration
- test_websocket_load_stress.py - Performance

### 🟡 Feature Tests (Should Pass)
- test_phase*.py - Feature-specific validation
- test_api_contract.py - API contracts

### 🟢 Optional Tests (Nice to Have)
- test_enhanced_visualization.py
- test_governance_integration.py

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Async test not running | Add @pytest.mark.asyncio |
| Import error in test | Check PYTHONPATH includes tests/ |
| WebSocket tests timeout | Increase timeout with @pytest.mark.timeout(30) |
| Port in use during tests | Tests use dynamic port allocation |

## Development Best Practices

1. **Test First**: Write tests before feature implementation
2. **Descriptive Names**: test_stat7_dimension_validation() not test_1()
3. **Single Responsibility**: One test = one behavior
4. **Async Pattern**: Use @pytest.mark.asyncio for async functions
5. **Mock External**: Mock LLM endpoints, external APIs
6. **Isolation**: Each test independent, no shared state

## Continuous Integration

GitHub Actions workflow (.github/workflows/):
- Runs on: push to main, pull_request
- Tests: All 46+ scenarios
- Coverage: Reports to PR
- Performance: Tracks metrics over time

---

**Truth Status**: Reflects actual pytest implementation. See tests/ directory for live examples.
