# 🤖 AI Assistant Instructions Profile
## For The Seed Project - STAT7 Multiverse Simulation

---

## 🎯 **Core Mission**
You are assisting with the development of **The Seed** - an open-source virtual sandbox for multiverse simulation using STAT7 (7-dimensional addressing). The goal is to create the backbone for an Oasis-style multiverse where developers can register games and coordinate narrative information across virtual worlds.

---

## 🏗️ **PROJECT ARCHITECTURE - MANDATORY ORGANIZATION**

### **Three System Boundaries (NEVER MIX):**

#### **🎮 TLDA (Unity) System - Game Engine Layer**
- **Location:** `Assets/Plugins/TWG/TLDA/`
- **Purpose:** Unity-specific game mechanics, editor tools, Steam integration
- **File Types:** `.cs`, `.unity`, `.prefab`, `.asset`
- **Key Components:**
  - Companion battle system (`Companion*.cs`)
  - Warbler NPC integration (`Warbler*.cs`)
  - Scribe documentation tools (`Scribe*.cs`)
  - Game management (`GameManager.cs`)
  - Platform integration (`SteamBridge.cs`)
  - Visualization bridges (`MindCastle*.cs`, `stat7node.cs`)

#### **🌐 Seed (Python) System - Backend Engine**
- **Location:** `Packages/com.twg.the-seed/seed/engine/`
- **Purpose:** STAT7 addressing, AI functionality, data processing
- **File Types:** `.py`, `.ipynb`, `.txt`
- **Key Components:**
  - STAT7 experiments (`stat7_experiments.py`)
  - Living Dev Agent AI (`warbler_quote_engine.py`, `interaction_manager.py`)
  - WebSocket server (`stat7wsserve.py`)
  - Data processing (`conservator.py`, `telemetry.py`)
  - Development tools (`symbolic_linter.py`, `validate_docs.py`)

#### **🔗 Bridge Components (Communication Layer)**
- **Location:** `web/` for web bridges, `Assets/Plugins/TWG/TLDA/Scripts/` for Unity bridges
- **Purpose:** Communication between TLDA and Seed systems
- **File Types:** `.js`, `.json`, bridge `.cs` files
- **Key Components:**
  - WebSocket communication (`stat7-websocket.js`)
  - 7D→3D projection (`stat7-core.js`)
  - Unity↔Seed bridges (`SeedMindCastleBridge.cs`, `WarblerNPCBridge.cs`)
  - Data schemas (shared JSON configurations)

---

## 📁 **STRICT FILE ORGANIZATION RULES**

### **🚫 NEVER CREATE FILES IN PROJECT ROOT**
The root directory should ONLY contain:
- Project configuration files (`README.md`, `package.json`, `.gitignore`)
- Solution files (`.sln`)
- Directory structure documentation

### **✅ PROPER FILE PLACEMENT**

#### **Python Scripts:**
- **STAT7 Visualization:** `web/server/`, `web/js/`, `web/launchers/`
- **Experiments:** `Packages/com.twg.the-seed/seed/engine/`
- **Living Dev Agent:** `Packages/com.twg.the-seed/The Living Dev Agent/`
- **Tests:** `tests/` (root level is acceptable for test organization)

#### **Unity Scripts:**
- **Runtime:** `Assets/Plugins/TWG/TLDA/Scripts/`
- **Editor:** `Assets/Plugins/TWG/TLDA/Editor/`
- **Tools:** `Assets/Plugins/TWG/TLDA/Tools/`

#### **Web Components:**
- **HTML:** `web/`
- **JavaScript:** `web/js/`
- **CSS:** `web/css/`
- **Servers:** `web/server/`
- **Launchers:** `web/launchers/`

#### **Documentation:**
- **Canonical:** `docs/` (GitBook-style directory - SEE BELOW)
- **API:** Auto-generated in appropriate package directories
- **Examples:** `examples/` in respective package directories

---

## 📚 **DOCUMENTATION ARCHITECTURE & SINGLE SOURCE OF TRUTH**

### **🎯 MANDATORY: GitBook-Style Documentation Directory**
**Location:** `docs/` (project root)

**Required Structure:**
\`\`\`
docs/
├── README.md                    # Main project overview
├── GETTING_STARTED.md           # Quick start guide (CANONICAL)
├── ARCHITECTURE.md              # System architecture overview
├── TLDA/                        # Unity system documentation
│   ├── README.md
│   ├── COMPANION_SYSTEM.md
│   ├── WARBLER_NPC.md
│   └── UNITY_INTEGRATION.md
├── SEED/                        # Python backend documentation
│   ├── README.md
│   ├── STAT7_ADDRESSING.md
│   ├── STAT7_VALIDATION_RESULTS.md  # Current validation status
│   ├── LIVING_DEV_AGENT.md
│   └── EXPERIMENTS.md
├── BRIDGES/                     # Communication layer documentation
│   ├── README.md
│   ├── WEBSOCKET_PROTOCOL.md
│   ├── 7D_PROJECTION.md
│   └── DATA_SCHEMAS.md
├── DEVELOPMENT/                 # Development guidelines
│   ├── README.md
│   ├── SECURITY.md              # Security policies & implementation (CANONICAL)
│   ├── TESTING.md
│   ├── CI_CD.md
│   └── CONTRIBUTING.md
├── API/                         # API references
│   ├── README.md
│   ├── SECURITY.md              # CANONICAL security reference (from Phase 1)
│   ├── PYTHON_API.md
│   ├── JAVASCRIPT_API.md
│   └── UNITY_API.md
└── ARCHIVE/                     # Historical documentation (read-only reference)
└── SCATTERED/
├── README.md            # Links to canonical versions
└── ...other old docs
\`\`\`

---

## ✏️ **DOCUMENTATION MAINTENANCE & EDITING PRACTICES**

### **🔑 FUNDAMENTAL PRINCIPLE: SINGLE SOURCE OF TRUTH**
- ✅ **One canonical location per concept** - Do NOT duplicate across multiple files
- ✅ **Direct editing of existing docs** - Update in place; commit history preserves all changes
- ❌ **Never create new .md files for updates** - This creates fragmentation and bloat
- ✅ **Archive outdated docs** - Move old versions to `docs/ARCHIVE/` with links to canonical versions

### **📖 How to Update Documentation**

**WHEN YOU NEED TO DOCUMENT SOMETHING:**

1. **Identify the canonical location:**
  - Feature in TLDA → `docs/TLDA/`
  - Feature in Seed → `docs/SEED/`
  - Bridge/WebSocket → `docs/BRIDGES/`
  - Development process → `docs/DEVELOPMENT/`
  - API reference → `docs/API/`
  - Getting started → `docs/GETTING_STARTED.md`

2. **Edit the canonical file directly:**
   \`\`\`bash
   # ✅ DO THIS:
   # Edit: docs/SEED/STAT7_ADDRESSING.md
   # Make your changes
   # Commit with: "docs(seed): Update STAT7 addressing clarification"

   # ❌ NEVER DO THIS:
   # Create: STAT7_ADDRESSING_NEW.md
   # Create: STAT7_UPDATES.md
   # Create: STAT7_REVISION_2.md
   \`\`\`

3. **Preserve version history:**
  - Changes automatically tracked in Git
  - No need to create new files for tracking changes
  - Use commit messages to document what changed and why

### **📝 Canonical Documentation Files & Their Maintainers**

| File | Purpose | Scope | Update Frequency |
|------|---------|-------|------------------|
| `docs/GETTING_STARTED.md` | Developer onboarding | All systems | As projects/setup changes |
| `docs/API/SECURITY.md` | Security policies & fixes | All APIs | On security findings |
| `docs/SEED/STAT7_VALIDATION_RESULTS.md` | Current system validation status | Seed system | After validation runs |
| `docs/SEED/STAT7_ADDRESSING.md` | STAT7 specification & theory | Seed system | On design changes |
| `docs/DEVELOPMENT/TESTING.md` | Test frameworks & practices | All systems | When test approach changes |
| `docs/DEVELOPMENT/CI_CD.md` | CI/CD pipeline documentation | Infrastructure | On workflow changes |

### **🚫 WHAT NOT TO DO**

**These create documentation bloat and will be consolidated:**
- ❌ Creating root-level `.md` files (except allowed config: `README.md`, `CHANGELOG.md`, `SECURITY.md`)
- ❌ Creating scattered docs in package subdirectories (except auto-generated API docs)
- ❌ Creating new docs when you could update existing ones
- ❌ Creating "QUICK_REFERENCE.md", "UPDATE_*.md", "NOTES_*.md" files
- ❌ One .md file per day/session (consolidate into canonical locations)
- ❌ Leaving outdated docs in place without archiving

**These WILL be cleaned up regularly:**
- Scattered documentation in `packages/com.twg.the-seed/seed/docs/`
- Scattered documentation in `packages/com.twg.the-seed/seed/engine/`
- Root-level documentation files (except allowed config)
- Outdated validation/results documents

### **✅ WHAT TO DO INSTEAD**

**For documentation changes:**
1. Find the canonical file in `docs/`
2. Edit it directly
3. Commit with descriptive message: `docs(section): What changed and why`
4. Outdated docs get archived to `docs/ARCHIVE/SCATTERED/` periodically

**For experimental/temporary documentation:**
- Use code comments for experimental features
- Use Git branches for parallel documentation development
- Merge into canonical locations when ready
- Do NOT create separate .md files

### **🔄 Documentation Review Checklist**

Before committing ANY documentation change:
- [ ] **Is this editing an existing canonical doc?**
- [ ] **Does this new content belong in one of the canonical locations?**
- [ ] **Am I NOT creating a new .md file as a workaround?**
- [ ] **Are cross-references up to date?**
- [ ] **Have I linked to actual code locations (when applicable)?**
- [ ] **Does this reflect current reality (truth-first)?**

---

## 📋 **DOCUMENTATION STANDARDS**

### **Every Major Component Must Have Documentation**
1. **Every major component** has corresponding documentation in `docs/`
2. **Cross-reference** between systems (TLDA ↔ Seed ↔ Bridges)
3. **Include examples** and usage patterns
4. **Maintain API references** for all public interfaces
5. **Update documentation** BEFORE changing code (truth-first approach)

### **Documentation Content Guidelines**
- **Start with WHY** - Explain purpose before implementation
- **Include examples** - Show real usage from the codebase
- **Link to code** - Reference actual files where logic lives
- **Date validation** - Note when documentation was last verified against code
- **Status indicator** - Mark if MAINTAINED, OUTDATED, or EXPERIMENTAL
- **Use tables** - For structured comparisons and overviews

---

## 🔧 **DEVELOPMENT WORKFLOW RULES**

### **Before Creating ANY File:**
1. **Check system boundaries** - Is this TLDA, Seed, or Bridge?
2. **Verify proper directory** - Use the structure above
3. **Consider documentation** - Where does this fit in `docs/`?
4. **Check for duplicates** - Does this already exist?

### **When Modifying Code:**
1. **Update relevant documentation** in `docs/` FIRST
2. **Test across system boundaries** if it affects bridges
3. **Verify file organization** remains clean
4. **Update cross-references** in documentation

### **When Running Tests:**
1. **TLDA tests:** Unity Test Runner
2. **Seed tests:** pytest from appropriate directories
3. **Bridge tests:** Both systems (integration tests)
4. **Documentation tests:** Verify all docs are accurate

---

## 🚨 **CRITICAL REMINDERS**

### **System Separation:**
- **TLDA = Unity game engine stuff**
- **Seed = Python backend/AI stuff**
- **Bridges = Communication between them**
- **NEVER mix responsibilities across boundaries**

### **File Organization:**
- **ROOT = Configuration only**
- **NO scripts in root directory**
- **Use proper package directories**
- **Keep web components in `web/`**

### **Documentation (NO MORE BLOAT):**
- **`docs/` is ONLY canonical reference**
- **ONE location per concept** - no duplicates
- **Edit existing docs directly** - Git tracks changes
- **Archive old docs** - don't leave them scattered
- **Root directory = config files only** (no .md bloat)

### **Communication:**
- **WebSocket for real-time data**
- **JSON schemas for data contracts**
- **Bridge components handle translation**
- **Keep interfaces clean and documented**

---

## 🎯 **PROJECT VISION CONTEXT**

Remember: This isn't just a technical project - it's building the foundation for an **open-source multiverse**. STAT7 addressing enables **narrative latency optimization** across virtual worlds. Think **Ready Player One's Oasis**, but **decentralized and MIT-licensed**.

When working on any component:
1. **How does this serve the multiverse vision?**
2. **Does this enable cross-world communication?**
3. **Is this properly documented for other developers?**
4. **Are system boundaries respected?**

---

## 📋 **CHECKLIST BEFORE ANY ACTION**

- [ ] **System boundary identified** (TLDA/Seed/Bridge)?
- [ ] **Proper directory selected** (no root files)?
- [ ] **Documentation location planned** in \`docs/\`?
- [ ] **Editing existing doc, NOT creating new one?**
- [ ] **Cross-system impacts considered?**
- [ ] **File organization verified?**
- [ ] **API boundaries respected?**

---

**This profile is your guide to maintaining clean, organized, and well-documented code that serves the multiverse vision. Always reference these rules before making any changes to the project structure.**

**DOCUMENTATION IS A COMMITMENT: Edit it directly, keep it current, archive the old. No bloat, no fragmentation—just truth.**
