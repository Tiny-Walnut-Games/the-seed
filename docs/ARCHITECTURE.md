# 🏗️ System Architecture

**Technical architecture of The Seed's three-system design for multiverse simulation.**

---

## 🎯 **Three-System Design**

The Seed implements a **clean separation of concerns** across three interconnected systems:

```
┌─────────────────┐    🔗 WebSocket/JSON    ┌─────────────────┐
│   🎮 TLDA     │◄──────────────────────►│   🌐 Seed      │
│  (Unity Game)   │                     │ (Python Backend) │
└─────────────────┘                     └─────────────────┘
         │                                      │
         │ 7D→3D Projection                    │ STAT7 Addressing
         ▼                                      ▼
┌─────────────────┐    🎮 Unity Bridge     ┌─────────────────┐
│  👁 Browser    │◄──────────────────────►│  📊 Visualization│
│   (Three.js)   │                     │   (Web Client)  │
└─────────────────┘                     └─────────────────┘
```

---

## 🎮 **TLDA System (Unity)**

### **Purpose:**
Game engine layer for Unity-specific functionality and Steam integration.

### **Responsibilities:**
- **Game Mechanics:** Companion battle systems, NPC behavior
- **Unity Integration:** Editor tools, asset management
- **Platform Integration:** Steam API, platform-specific features
- **Rendering:** Unity scene management, visual effects
- **Input/Output:** Player controls, UI systems

### **Key Components:**
```
Assets/Plugins/TWG/TLDA/
├── Scripts/
│   ├── GameManager.cs              # Core game loop
│   ├── Companion/                  # Battle system
│   ├── Warbler/                   # NPC integration
│   ├── Visualization/              # STAT7 bridges
│   └── Platform/                  # Steam integration
├── Editor/
│   ├── Scribe/                    # Documentation tools
│   ├── Tools/                      # Unity editor extensions
│   └── TestSuite/                 # Unity test runner
└── Runtime/                         # Runtime components
```

### **Data Flow:**
- **Input:** Player actions, Steam events, Unity lifecycle
- **Processing:** Game logic, companion battles, NPC AI
- **Output:** Unity scene updates, Steam achievements, bridge events

---

## 🌐 **Seed System (Python)**

### **Purpose:**
Backend engine for STAT7 addressing, AI functionality, and data processing.

### **Responsibilities:**
- **STAT7 Addressing:** 7D coordinate generation and management
- **Living Dev Agent:** AI assistant and development tools
- **Data Processing:** Experiment execution, analysis, storage
- **WebSocket Server:** Real-time event streaming
- **Development Tools:** Code quality, validation, build management

### **Key Components:**
```
Packages/com.twg.the-seed/
├── seed/engine/
│   ├── stat7_experiments.py       # Core STAT7 validation
│   ├── stat7wsserve.py           # WebSocket server
│   ├── conservator.py             # Data management
│   ├── telemetry.py               # System monitoring
│   └── plugins/                  # Plugin architecture
├── The Living Dev Agent/
│   ├── src/                      # AI components
│   ├── scripts/                   # Development tools
│   └── tests/                     # AI system tests
└── seed/docs/                      # Technical documentation
```

### **Data Flow:**
- **Input:** WebSocket events, experiment parameters, AI queries
- **Processing:** STAT7 calculations, AI responses, data analysis
- **Output:** WebSocket streams, experiment results, AI responses

---

## 🔗 **Bridge Components**

### **Purpose:**
Communication layer enabling TLDA and Seed systems to work together seamlessly.

### **Types of Bridges:**

#### **🌐 Web Bridge (JavaScript)**
```
web/
├── js/
│   ├── stat7-websocket.js        # WebSocket client
│   ├── stat7-core.js            # 7D→3D projection
│   ├── stat7-ui.js              # User interface
│   └── stat7-main.js            # Main orchestration
├── server/
│   ├── stat7wsserve.py           # WebSocket server
│   └── simple_web_server.py     # Static file server
└── *.html                        # Visualization interfaces
```

#### **🎮 Unity Bridge (C#)**
```
Assets/Plugins/TWG/TLDA/Scripts/Visualization/
├── SeedMindCastleBridge.cs      # Unity↔Seed data
├── stat7node.cs                # STAT7 Unity integration
└── MindCastleVisualizer.cs     # 3D rendering
```

#### **🤖 AI Bridge (Python↔Unity)**
```
Assets/Plugins/TWG/TLDA/Scripts/NPCControl/
├── WarblerNPCBridge.cs          # Unity↔AI communication
├── WarblerDialogueSystem.cs     # Dialogue management
└── WarblerAPI.cs               # AI interface
```

---

## 📊 **Communication Protocols**

### **WebSocket Protocol:**
- **Port:** 8765 (WebSocket server)
- **Port:** 8001 (HTTP server)
- **Format:** JSON event streaming
- **Events:** `bitchain_created`, `experiment_start`, `experiment_complete`

### **Data Schemas:**
```json
{
  "event_type": "bitchain_created",
  "timestamp": "2025-01-01T00:00:00Z",
  "data": {
    "bitchain": {...},
    "address": "stat7://...",
    "coordinates": {
      "realm": "narrative",
      "lineage": 123,
      "adjacency": [...],
      "horizon": "crystallization",
      "resonance": 0.85,
      "velocity": 1.2,
      "density": 0.7
    }
  },
  "experiment_id": "EXP-01-abc123",
  "metadata": {
    "visualization_type": "point_cloud",
    "color": "#e74c3c",
    "size": 1.0
  }
}
```

---

## 🎯 **STAT7 7D Addressing System**

### **Coordinate Dimensions:**

1. **Realm** - Virtual world/universe identifier
2. **Lineage** - Entity hierarchy and inheritance
3. **Adjacency** - Connection relationships between entities
4. **Horizon** - Temporal context and lifecycle stage
5. **Resonance** - Semantic similarity and thematic grouping
6. **Velocity** - Rate of change and dynamic properties
7. **Density** - Information concentration and complexity

### **Address Format:**
```
stat7://realm:lineage/adjacency1,adjacency2/horizon?resonance=X&velocity=Y&density=Z
```

### **Use Cases:**
- **Cross-world references:** NPCs can mention events from other games
- **Narrative coordination:** Stories can span multiple virtual worlds
- **Semantic optimization:** Related content groups efficiently
- **Temporal tracking:** Events maintain chronological context

---

## 🔄 **System Interactions**

### **Typical Workflow:**

1. **Game Event (TLDA):**
   - Player completes companion battle
   - Unity generates event data
   - Bridge sends to Seed system

2. **STAT7 Processing (Seed):**
   - Generate 7D address for event
   - Calculate semantic relationships
   - Store in coordinate system

3. **Visualization (Bridge):**
   - WebSocket streams event to browser
   - JavaScript projects 7D→3D
   - Three.js renders visualization

4. **AI Response (Seed):**
   - Living Dev Agent analyzes event
   - Generates contextual response
   - Sends back to Unity via bridge

### **Data Flow Diagram:**
```
Unity Game → C# Bridge → WebSocket → Python Engine → AI Processing
     ↓              ↓           ↓              ↓
Scene Update ← JSON Data ← 7D Address ← Narrative Context
```

---

## 🛡️ **Security & Isolation**

### **System Boundaries:**
- **TLDA:** Unity sandbox, no direct Python access
- **Seed:** Python environment, no Unity dependencies
- **Bridges:** Controlled communication via defined protocols

### **Data Validation:**
- **Input validation** on all bridge interfaces
- **Schema validation** for JSON communication
- **Type safety** in C# and Python components
- **Error handling** with graceful degradation

---

## 🚀 **Scalability Considerations**

### **Performance:**
- **WebSocket streaming** for real-time updates
- **GPU acceleration** via Three.js for visualization
- **Async processing** in Python for concurrent operations
- **Unity optimization** for game performance

### **Extensibility:**
- **Plugin architecture** for custom components
- **Modular bridges** for new integrations
- **Schema evolution** for protocol updates
- **API versioning** for backward compatibility

---

## 📋 **Development Guidelines**

### **When Adding Features:**
1. **Identify system boundary** (TLDA/Seed/Bridge)
2. **Follow existing patterns** in that system
3. **Update bridge protocols** if cross-system communication needed
4. **Document in appropriate section** of this architecture
5. **Test integration** across system boundaries

### **When Modifying Bridges:**
1. **Maintain protocol compatibility**
2. **Update both endpoints** (Unity and Python)
3. **Test with all supported systems**
4. **Update documentation** and examples

---

This architecture enables **clean development** while supporting the complex interactions needed for a multiverse simulation platform.
