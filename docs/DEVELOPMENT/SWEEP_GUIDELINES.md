# SWEEP.md - Development Guidelines & Commands

> **Truth First, Hype Last** - This document prioritizes what actually works over what sounds impressive

## 🚨 CRITICAL RULE: NO FALSE CELEBRATIONS

**ABSOLUTE MANDATE**: Never claim completion or success when documentation doesn't match reality.

- ✅ **DO**: Report actual progress with specific evidence
- ❌ **DON'T**: Say "EVERYTHING IS AWESOME" when docs are outdated
- ✅ **DO**: Acknowledge gaps between vision and implementation
- ❌ **DON'T**: Celebrate features that don't exist yet
- ✅ **DO**: Use precise language about what's working vs. what's planned
- ❌ **DON'T**: Let premature celebrations confuse yourself or others

**If you catch yourself writing celebratory language, stop and verify:**
1. Does the code actually work?
2. Is the documentation up to date?
3. Are there known issues not mentioned?
4. Is this feature complete or just started?

---

## 📋 PROJECT OVERVIEW

### What This Project Actually Is (Today)
- **The Seed**: STAT7 (7-dimensional addressing) validation experiments in Python
- **Unity Integration**: TLDA template with Seed-specific bridges under Assets/TWG/
- **Living Dev Agent**: Development workflow tools and documentation systems
- **Multi-language**: Python experiments, C# Unity code, TypeScript/JavaScript tooling

### What This Project Is NOT (Yet)
- A complete fractal-chain addressing system (still experimental)
- A production-ready storage solution (validation phase)
- A finished C# project (Unity integration layer only)

### Project Structure
```
/seed/                    # Core Seed experiments and documentation
/src/                     # Source code for various tools
/scripts/                 # Build, validation, and utility scripts
/Assets/                  # Unity project files and TLDA integration
/docs/                    # Documentation (may contain outdated celebratory content)
/packages/                # Node.js packages and warbler-core
/TLDL/                    # True Living Development Log entries
```

---

## 🛠️ DEVELOPMENT COMMANDS

### Environment Setup
```bash
# Clone and initialize
git clone <repository-url>
cd the-seed

# Install Python dependencies (timeout acceptable)
pip install -r scripts/requirements.txt

# Initialize development context
./scripts/init_agent_context.sh

# Or on Windows
powershell scripts/init_agent_context.ps1
```

### Python/Seed Commands
```bash
# Run STAT7 validation experiments
python3 scripts/run_exp_phase1.py --mode quick    # Fast validation
python3 scripts/run_exp_phase1.py --mode full     # Complete validation

# Validate documentation
python3 src/SymbolicLinter/validate_docs.py --tldl-path TLDL/entries/

# Symbolic code linting
python3 src/SymbolicLinter/symbolic_linter.py --path src/

# Debug overlay validation
python3 src/DebugOverlayValidation/debug_overlay_validator.py --path src/DebugOverlayValidation/
```

### Node.js/TypeScript Commands
```bash
# Install dependencies
npm install

# Build all workspaces
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Validate warbler packs
npm run pack:validate

# Simulate warble
npm run warbler:simulate
```

### Unity Commands
```bash
# Open Unity project (use Unity Hub or command line)
Unity -projectPath . -batchmode -quit -executeMethod BuildScript.Build

# Run Unity tests (via Unity Test Runner)
# Unity Menu: Window > General > Test Runner

# Generate School experiment inventory
# Unity Menu: Tools > School > Generate Inventory

# Extract School hypotheses
# Unity Menu: Tools > School > Extract Hypotheses
```

### Validation Commands
```bash
# Complete validation suite (sub-200ms total)
python3 src/SymbolicLinter/validate_docs.py --tldl-path TLDL/entries/ && \
python3 src/SymbolicLinter/symbolic_linter.py --path src/ && \
python3 src/DebugOverlayValidation/debug_overlay_validator.py --path src/DebugOverlayValidation/

# Quick health check
./scripts/validate_setup.sh
```

---

## 🎯 STORY TEST PHILOSOPHY (NON-C# GUIDANCE)

### Core Principle: Quality Beyond Language
The Story Test system validates C# code, but its philosophy applies to ALL components:

**Every component must:**
1. **Have Clear Purpose** - What problem does this solve?
2. **Demonstrate Quality** - Is this implementation robust?
3. **Show Evidence** - Can we prove it works?
4. **Maintain Standards** - Does it meet project quality bar?

### Applying Story Test Standards to Non-C# Code

#### Python/Seed Components
```python
# ✅ GOOD: Clear purpose with validation
def validate_stat7_addressing():
    """
    Validates STAT7 addressing uniqueness.
    Returns: (success: bool, details: dict)
    """
    # Implementation with measurable results
    pass

# ❌ AVOID: Unclear purpose without validation
def some_function():
    # Does something with STAT7
    pass
```

#### TypeScript/JavaScript Components
```typescript
// ✅ GOOD: Clear interface with validation
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

function validateWarblerPack(pack: PackConfig): ValidationResult {
  // Return structured, testable results
}

// ❌ AVOID: Vague return types
function processPack(pack: any): any {
  // What does this return? How do we know it worked?
}
```

#### Documentation Components
```markdown
<!-- ✅ GOOD: Specific, verifiable claims -->
## STAT7 Validation Results
- **EXP-01 Address Uniqueness**: 99.8% collision-free at 1M scale
- **EXP-02 Retrieval Speed**: 0.3ms average query time
- **Test Environment**: Python 3.11, 16GB RAM, M1 Pro

<!-- ❌ AVOID: Unverifiable claims -->
## STAT7 is Amazing!
- Everything works perfectly!
- Revolutionary addressing system!
- Complete success achieved!
```

### Quality Checklist for All Components
- [ ] **Purpose**: Can I explain what this does in one sentence?
- [ ] **Evidence**: How do I know it works? (tests, metrics, logs)
- [ ] **Standards**: Does this meet our quality criteria?
- [ ] **Documentation**: Is the current state accurately reflected?
- [ ] **Integration**: How does this connect to other components?

---

## 📝 DOCUMENTATION STANDARDS

### Truth-First Documentation Rules

#### 1. Status Accuracy
```markdown
<!-- ✅ ACCURATE -->
## Current Status
- **STAT7 Validation**: Phase 1 complete (EXP-01, EXP-02, EXP-03)
- **Unity Integration**: Basic bridges implemented, testing required
- **Documentation**: Some sections outdated, see IMPLEMENTATION_STATUS.md

<!-- ❌ PREMATURE CELEBRATION -->
## Current Status
- **STAT7**: Revolutionary success! Everything works!
- **Unity**: Complete integration achieved!
- **Documentation**: Comprehensive and up-to-date!
```

#### 2. Evidence-Based Claims
```markdown
<!-- ✅ EVIDENCE-BASED -->
## Performance Results
- **Address Generation**: 10,000 addresses/sec (Python 3.11, M1 Pro)
- **Memory Usage**: 150MB for 1M addresses
- **Test Coverage**: 85% of core functions

<!-- ❌ UNSUPPORTED CLAIMS -->
## Performance Results
- **Blazing Fast**: Unmatched performance!
- **Memory Efficient**: Minimal footprint!
- **Well Tested**: Comprehensive coverage!
```

#### 3. Gap Acknowledgment
```markdown
<!-- ✅ HONEST ABOUT GAPS -->
## Known Limitations
- **Scale Testing**: Only tested up to 1M addresses
- **Unity Integration**: Basic functionality, error handling incomplete
- **Documentation**: Some lore documents contain aspirational content

<!-- ❌ HIDING PROBLEMS -->
## Current Status
- **Scale**: Handles unlimited addresses!
- **Integration**: Production-ready!
- **Documentation**: Complete and accurate!
```

### Documentation Update Workflow
1. **Code Change**: Update relevant documentation immediately
2. **Status Check**: Verify all claims match reality
3. **Evidence Review**: Ensure all metrics are current
4. **Gap Audit**: Acknowledge what's not working
5. **Peer Review**: Have someone check for false celebrations

---

## 🏗️ CODE CLASSIFICATION SYSTEM

### Sacred Code Categories (from Sacred Code Classification Protocol)

#### ??? PROTECTED CORE (Don't Touch Without Review)
- Core mathematical algorithms
- Performance-critical systems
- Burst-compiled components
- Coordinate transform logic

#### ?? INTENDED EXPANSION (Modify Freely)
- Game-specific validation logic
- Art placement strategies
- Test harness examples
- Project-specific configurations

#### ?? ENHANCEMENT READY (Improve Thoughtfully)
- Simplified implementations
- Basic material systems
- Stub implementations
- Placeholder validations

#### ?? COORDINATE-AWARE (Spatial Intelligence)
- Systems using nodeId.Coordinates
- Distance-based calculations
- Pattern recognition algorithms
- Spatial coherence analysis

### Comment Patterns
```csharp
// ??? CORE ALGORITHM - Modification requires architectural review
// ?Intended use!? [Purpose] - Expand as needed for your project
// ?? ENHANCEMENT READY - Simplified for compilation success
// ?? COORDINATE-AWARE - Uses nodeId.Coordinates for spatial intelligence
```

---

## 🧪 TESTING & VALIDATION

### STAT7 Validation Experiments
```bash
# Phase 1 Experiments (Core validation)
python3 scripts/run_exp_phase1.py --mode quick    # Basic validation
python3 scripts/run_exp_phase1.py --mode default  # Standard validation
python3 scripts/run_exp_phase1.py --mode full     # Complete validation

# Individual experiments
python3 seed/engine/stat7_experiments.py --exp EXP-01  # Address uniqueness
python3 seed/engine/stat7_experiments.py --exp EXP-02  # Retrieval efficiency
python3 seed/engine/stat7_experiments.py --exp EXP-03  # Dimension necessity
```

### Unity Testing
```csharp
// Run Unity tests via Test Runner
// Window > General > Test Runner
// Run All tests or specific categories

// School Experiment Workflow
// Tools > School > Generate Inventory
// Tools > School > Extract Hypotheses
```

### Documentation Validation
```bash
# Validate TLDL entries
python3 src/SymbolicLinter/validate_docs.py --tldl-path TLDL/entries/

# Check for broken links and outdated content
python3 src/SymbolicLinter/symbolic_linter.py --path docs/

# Validate project structure
python3 src/DebugOverlayValidation/debug_overlay_validator.py --path src/DebugOverlayValidation/
```

---

## 🚀 BUILD & DEPLOYMENT

### Local Development
```bash
# Python environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r scripts/requirements.txt

# Node.js environment
npm install
npm run build

# Unity (requires Unity Editor)
# Open project in Unity Hub
# Assets > Open C# Project (for Rider/VSCode)
```

### CI/CD Pipeline
```yaml
# .github/workflows/validate.yml
name: Validate Project
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r scripts/requirements.txt
      - name: Run validation
        run: |
          python3 src/SymbolicLinter/validate_docs.py --tldl-path TLDL/entries/
          python3 src/SymbolicLinter/symbolic_linter.py --path src/
          npm run lint
```

---

## 📊 PROJECT STATUS (TRUTHFUL)

### What's Working (Verified)
- ✅ **STAT7 Phase 1 Validation**: EXP-01, EXP-02, EXP-03 implemented
- ✅ **Python Experiment Framework**: Basic validation runner works
- ✅ **Unity TLDA Integration**: Core bridges and editors functional
- ✅ **Documentation Validation**: Sub-200ms validation suite
- ✅ **TLDL System**: Chronicle generation and indexing

### What's Partial (Needs Work)
- 🔄 **Unity Testing**: Story Test only validates C#, not full system
- 🔄 **STAT7 Scaling**: Tested to 1M addresses, higher scales unverified
- 🔄 **Documentation Accuracy**: Some lore docs contain aspirational content
- 🔄 **Error Handling**: Incomplete in several components

### What's Not Working (Known Issues)
- ❌ **Complete Fractal Implementation**: Still conceptual/experimental
- ❌ **Production Storage**: Not production-ready
- ❌ **Cross-language Integration**: Limited between Python/C#/TypeScript
- ❌ **Performance at Scale**: Not tested beyond experimental limits

---

## 🎯 DEVELOPMENT PRIORITIES

### Immediate (This Week)
1. **Fix Documentation Gaps**: Update all celebratory claims to reality
2. **Complete Unity Testing**: Extend Story Test philosophy to non-C# parts
3. **Improve Error Handling**: Add robust error handling to all components
4. **Scale Testing**: Test STAT7 beyond 1M addresses

### Short Term (Next Month)
1. **Cross-language Integration**: Better Python/C#/TypeScript communication
2. **Enhanced Validation**: More comprehensive test coverage
3. **Performance Optimization**: Improve experiment execution speed
4. **Documentation Sync**: Ensure all docs match implementation

### Long Term (Future)
1. **Production Storage**: Move from experimental to production-ready
2. **Complete Fractal Implementation**: Full hierarchical addressing
3. **Advanced Visualization**: Better tools for understanding STAT7 space
4. **Community Integration**: Make system usable by other projects

---

## 📞 GETTING HELP

### When You're Stuck
1. **Check IMPLEMENTATION_STATUS.md**: Current verified state
2. **Run Validation**: `python3 scripts/run_exp_phase1.py --mode quick`
3. **Read Code First**: Prefer working code over documentation
4. **Ask Specific Questions**: "What's the current status of X?" not "Is X done?"

### Reporting Issues
1. **Provide Evidence**: Logs, error messages, validation results
2. **Be Specific**: "Component Y fails when Z happens" not "Everything is broken"
3. **Include Environment**: OS, Python/Node/Unity versions
4. **Avoid Celebratory Language**: Just state facts

---

## 🔗 USEFUL REFERENCES

### Current & Accurate
- [seed/docs/index.md](seed/docs/index.md) - Seed project overview
- [IMPLEMENTATION_STATUS.md](seed/docs/lore/TheSeedConcept/IMPLEMENTATION_STATUS.md) - Current status
- [scripts/requirements.txt](scripts/requirements.txt) - Python dependencies
- [package.json](package.json) - Node.js configuration

### Historical (May Contain Aspirational Content)
- [README.md](README.md) - Project overview (some sections outdated)
- [docs/index.md](docs/index.md) - TLDL documentation
- [seed/docs/lore/TheSeedConcept/](seed/docs/lore/TheSeedConcept/) - Conceptual documents

### Code References
- [seed/engine/stat7_experiments.py](seed/engine/stat7_experiments.py) - Core experiments
- [Assets/TWG/](Assets/TWG/) - Unity integration code
- [src/SymbolicLinter/](src/SymbolicLinter/) - Validation tools

---

## 📜 LAST UPDATED

**Date**: 2025-01-18
**Status**: Active development, validation phase
**Accuracy**: This document prioritizes verified facts over aspirational goals
**Philosophy**: Truth first, documentation accuracy always, no false celebrations

---

**Remember**: The goal is to build something that actually works, not to document something we wish worked. Stay grounded in reality, acknowledge gaps honestly, and celebrate only what's truly achieved. 🚀
