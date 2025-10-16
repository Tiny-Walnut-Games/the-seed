---
description: Repository Information Overview
alwaysApply: true
---

# The Seed Information

## Summary
The Seed is a conceptual fractal creation engine, currently in early development. It's built upon the Living Dev Agent (TLDA) template, which provides professional debugging and development workflow tools with an adventure-driven development experience. The Seed aims to create an infinitely extensible framework where realms, lineages, adjacencies, and horizons form the addressing scheme of both data and narrative.

## Structure
- **src/**: Core Python modules for various tools and services
- **engine/**: Python backend for the framework's core functionality
- **docs/**: Extensive documentation and guides
- **tests/**: Test files for various components
- **Assets/**: Unity-related assets and scripts
- **data/**: JSON and YAML data files
- **packs/**: Warbler packs for content distribution
- **schema/**: JSON schema definitions

## Language & Runtime
**Languages**: Python, JavaScript/TypeScript, C#
**Python Version**: 3.12 (specified in Dockerfile)
**Node Version**: >=18.0.0 (specified in package.json)
**Build Systems**: npm, Unity
**Package Managers**: npm, pip

## Dependencies
**Main Dependencies**:
- JavaScript: @playwright/mcp, js-yaml
- Python: PyYAML, argparse, markdown, jsonschema
- Unity: High Definition Render Pipeline

**Development Dependencies**:
- @playwright/test, typescript, vitest, eslint
- colorama, ruamel.yaml (Python)

## Build & Installation
```bash
# JavaScript/TypeScript components
npm run build

# Python components
pip install -r scripts/requirements.txt

# Validation tools
python3 src/SymbolicLinter/validate_docs.py --tldl-path TLDL/entries/
python3 src/SymbolicLinter/symbolic_linter.py --path src/
python3 src/DebugOverlayValidation/debug_overlay_validator.py --path src/DebugOverlayValidation/
```

## Docker
**Dockerfile**: Located at repository root
**Image**: twg-tlda-ai
**Configuration**: Python 3.12-slim with LLM integration capabilities
**Run Command**:
```bash
docker build -t twg-tlda-ai .
docker run --rm -p 8080:8080 twg-tlda-ai
```

## Testing
**Frameworks**: Python unittest, Vitest (JavaScript)
**Test Location**: /tests directory
**Naming Convention**: test_*.py for Python, *-tests.js for JavaScript
**Run Command**:
```bash
# JavaScript tests
npm run test

# Warbler-specific tests
npm run test:warbler
```

## Unity Integration
**Project Type**: Unity game/tool
**Configuration**: High Definition Render Pipeline
**Components**: 
- TLDA (Living Dev Agent) integration
- School Experiment Workflow
- Debug overlay validation

## Key Components
**Warbler System**: Content management and distribution system
**ScrollQuoteEngine**: Quote management and display system
**SymbolicLinter**: Documentation validation tool
**ConsoleCommentary**: Debugging and documentation tool
**SelfCare Engine**: Developer cognitive resource management