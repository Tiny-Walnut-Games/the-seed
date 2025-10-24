# 🎮 TLDA System Documentation

**Unity game engine layer for The Seed multiverse project.**

---

## 🎯 **TLDA Overview**

TLDA (True Living Development Assistant) is the **Unity-based game engine component** of The Seed project. It handles all Unity-specific functionality including game mechanics, Steam integration, and the bridge to the Seed Python backend.

---

## 🏗️ **System Architecture**

### **Core Responsibilities:**
- **Game Mechanics:** Companion battle systems, NPC behavior
- **Unity Integration:** Editor tools, asset management, scene handling
- **Platform Integration:** Steam API, platform-specific features
- **Bridge Communication:** Data exchange with Seed Python backend
- **Visualization:** STAT7 data rendering in Unity environment

### **Directory Structure:**
```
Assets/Plugins/TWG/TLDA/
├── Scripts/
│   ├── GameManager.cs              # Core game management
│   ├── Companion/                  # Companion battle system
│   │   ├── Companion.cs
│   │   ├── CompanionBattleManager.cs
│   │   ├── CompanionBattleUI.cs
│   │   └── CompanionBattleCore.cs
│   ├── Warbler/                   # NPC integration
│   │   ├── WarblerNPCBridge.cs
│   │   ├── WarblerDialogueSystem.cs
│   │   └── WarblerAPI.cs
│   ├── Visualization/              # STAT7 bridges
│   │   ├── SeedMindCastleBridge.cs
│   │   ├── stat7node.cs
│   │   ├── MindCastleVisualizer.cs
│   │   └── MindCastleSceneSetup.cs
│   ├── Platform/                  # Platform integration
│   │   ├── SteamBridge.cs
│   │   ├── ISteamworksAPI.cs
│   │   └── IPlatformBridge.cs
│   ├── Quest/                     # Quest system
│   │   └── QuestManager.cs
│   ├── Chat/                      # Chat interface
│   │   ├── TLDAChatInterface.cs
│   │   └── SeedEnhancedTLDAChat.cs
│   └── Editor/                    # Editor tools
│       ├── WarblerProjectOrchestrator.cs
│       ├── WarblerIntelligentOrchestrator.cs
│       └── WarblerChatWindow.cs
├── Editor/
│   ├── Scribe/                    # Documentation tools
│   │   ├── ScribeCore.cs
│   │   ├── ScribeDataManager.cs
│   │   ├── ScribeMarkdownParser.cs
│   │   ├── ScribeMarkdownGenerator.cs
│   │   ├── ScribeImageManager.cs
│   │   ├── ScribeGitWindow.cs
│   │   ├── ScribeCommitWindow.cs
│   │   ├── ScribeFormBuilder.cs
│   │   ├── ScribeNavigator.cs
│   │   ├── ScribePreviewRenderer.cs
│   │   ├── ScribeFileOperations.cs
│   │   └── ScribeTemplateManager.cs
│   ├── Tools/                      # Unity editor extensions
│   │   ├── School/                 # Experiment tools
│   │   │   ├── SchoolExperimentWorkbench.cs
│   │   │   ├── ExperimentRunner.cs
│   │   │   ├── InventoryCollector.cs
│   │   │   ├── HypothesisExtractor.cs
│   │   │   ├── IntelligenceSynthesizer.cs
│   │   │   ├── ResultValidator.cs
│   │   │   ├── ReportSynthesizer.cs
│   │   │   ├── ManifestConverter.cs
│   │   │   └── WarblerContextBridge.cs
│   │   └── Alchemist/              # Data processing tools
│   │       ├── AlchemistManifestGenerator.cs
│   │       └── ExperimentManifestGenerator.cs
│   ├── TerminusShellConsole.cs     # Debug console
│   ├── SpellsmithCodeWindow.cs     # Code editor
│   ├── ChronasTimerOverlay.cs      # Time tracking
│   ├── TestSuite/                  # Unity test runner
│   │   ├── UnityTestSuiteManager.cs
│   │   └── OneClickValidationRunner.cs
│   └── ForceCSharp10.cs           # C# version enforcement
└── Runtime/                         # Runtime components
    └── CompanionWarblerIntegration.cs
```

---

## 🎮 **Core Systems**

### **Companion Battle System**
**Location:** `Assets/Plugins/TWG/TLDA/Scripts/Companion/`

**Purpose:** Turn-based companion battle mechanics with integration to Seed backend.

**Key Components:**
- `Companion.cs` - Companion entity definition
- `CompanionBattleManager.cs` - Battle state management
- `CompanionBattleUI.cs` - User interface for battles
- `CompanionBattleCore.cs` - Core battle logic

**Integration:** Sends battle events to Seed for STAT7 addressing and narrative tracking.

### **Warbler NPC System**
**Location:** `Assets/Plugins/TWG/TLDA/Scripts/Warbler/`

**Purpose:** AI-powered NPC integration with Living Dev Agent.

**Key Components:**
- `WarblerNPCBridge.cs` - Unity↔AI communication bridge
- `WarblerDialogueSystem.cs` - Dialogue management
- `WarblerAPI.cs` - AI service interface

**Integration:** Connects to Seed's Living Dev Agent for dynamic NPC behavior.

### **STAT7 Visualization**
**Location:** `Assets/Plugins/TWG/TLDA/Scripts/Visualization/`

**Purpose:** Render STAT7 7D coordinate data in Unity environment.

**Key Components:**
- `SeedMindCastleBridge.cs` - Data bridge from Seed backend
- `stat7node.cs` - STAT7 entity representation
- `MindCastleVisualizer.cs` - 3D visualization rendering
- `MindCastleSceneSetup.cs` - Scene configuration

**Integration:** Receives STAT7 data via WebSocket and renders as 3D objects.

---

## 🔗 **Bridge Integration**

### **Unity ↔ Python Communication**

#### **WebSocket Bridge:**
```csharp
// Example: Sending event to Seed
public void SendBattleEvent(BattleEvent battleEvent)
{
    var eventData = new
    {
        event_type = "companion_battle",
        data = battleEvent.ToDictionary(),
        timestamp = DateTime.UtcNow.ToString("o")
    };

    _webSocketClient.SendJson(eventData);
}
```

#### **STAT7 Data Reception:**
```csharp
// Example: Receiving STAT7 entity
public void OnStat7EntityReceived(Stat7Entity entity)
{
    var gameObject = Instantiate(stat7NodePrefab);
    var node = gameObject.GetComponent<stat7node>();
    node.Initialize(entity);

    // Position based on 7D→3D projection
    transform.position = Project7DTo3D(entity.Coordinates);
}
```

---

## 🛠️ **Development Workflow**

### **Setting Up TLDA Development:**

1. **Open Unity Project:**
   ```bash
   # Open in Unity Hub
   # Navigate to E:/Tiny_Walnut_Games/the-seed
   ```

2. **Verify Compilation:**
   - Check Console for compilation errors
   - Ensure all TLDA scripts compile without errors
   - Verify .NET Framework version compatibility

3. **Run Tests:**
   - Window → General → Test Runner
   - Run "TLDA Test Suite"
   - Verify all tests pass

### **Creating New TLDA Components:**

1. **Choose Location:**
   - Game mechanics: `Scripts/`
   - Editor tools: `Editor/`
   - Runtime components: `Runtime/`

2. **Follow Patterns:**
   - Use existing script templates
   - Implement proper bridge integration
   - Add Unity Test Runner tests

3. **Bridge Integration:**
   - Add WebSocket communication if needed
   - Define JSON schemas for data exchange
   - Update bridge documentation

---

## 🧪 **Testing**

### **Unity Test Runner:**
```csharp
[Test]
public void CompanionBattle_CalculatesDamageCorrectly()
{
    // Arrange
    var companion = new Companion();
    var opponent = new Companion();

    // Act
    var damage = companion.CalculateDamage(opponent);

    // Assert
    Assert.IsTrue(damage > 0);
}
```

### **Integration Tests:**
- Test WebSocket communication with Seed backend
- Verify STAT7 data reception and rendering
- Validate bridge protocol compliance

---

## 📊 **Performance Considerations**

### **Unity Optimization:**
- **Object Pooling:** Reuse companion and effect objects
- **LOD Systems:** Level of detail for STAT7 visualization
- **Async Operations:** Non-blocking WebSocket communication
- **Memory Management:** Proper cleanup of bridge connections

### **Bridge Performance:**
- **Batch Updates:** Group multiple STAT7 updates
- **Compression:** Compress JSON data for large transfers
- **Connection Pooling:** Reuse WebSocket connections
- **Error Handling:** Graceful degradation on connection loss

---

## 🔧 **Configuration**

### **Unity Settings:**
- **Scripting Runtime Version:** .NET Standard 2.1
- **API Compatibility Level:** .NET Standard 2.1
- **Script Compilation:** Custom defines for TLDA features

### **Bridge Configuration:**
```csharp
public class TLDAConfig
{
    public string WebSocketUrl = "ws://localhost:8765";
    public string WebServerUrl = "http://localhost:8001";
    public bool EnableSTAT7Visualization = true;
    public bool EnableWarblerIntegration = true;
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **Compilation Errors:**
- Check .NET Framework version
- Verify all required packages are imported
- Check for missing using statements

#### **WebSocket Connection Issues:**
- Verify Seed backend is running
- Check firewall settings for ports 8765/8001
- Validate JSON schema compatibility

#### **STAT7 Visualization Issues:**
- Check 7D→3D projection calculations
- Verify coordinate system alignment
- Validate material and shader assignments

---

## 📚 **Related Documentation**

- **[BRIDGES/README.md](../BRIDGES/README.md)** - Bridge system documentation
- **[API/UNITY_API.md](../API/UNITY_API.md)** - Unity API reference
- **[DEVELOPMENT/CODING_STANDARDS.md](../DEVELOPMENT/CODING_STANDARDS.md)** - Coding guidelines

---

**TLDA provides the Unity foundation for The Seed's multiverse vision, enabling rich game experiences while maintaining clean integration with the STAT7 addressing system.**
