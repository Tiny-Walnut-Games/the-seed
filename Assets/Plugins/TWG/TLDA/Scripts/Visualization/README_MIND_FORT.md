# 🏰 Mind Fort - Quick Start

**Status**: Ready to Use ✨  
**Components**: 3 scripts (Bootstrapper, Warbler, Alice)  
**Location**: `Assets/Plugins/TWG/TLDA/Scripts/Visualization/`

---

## **One-Click Bootstrap** (30 seconds)

### In Unity Editor:

1. **Create Empty GameObject**
   - Hierarchy → Right-click → Create Empty

2. **Add Component**: `MindFortBootstrapper`
   - Inspector → Add Component → Search "MindFortBootstrapper"

3. **Click the Menu Item**
   - Click the component's three-dot menu (⋮)
   - Select `🏰 Bootstrap Mind Fort`

4. **Watch It Happen**
   - 7 rooms appear in a circle
   - Warbler manifests at center (mouths orbiting)
   - Alice glows and orbits protectively
   - Ethereal corridors connect everything

5. **Press Play** → Scene is fully functional

---

## **What You See**

### **At The Center**
**Warbler**: A twisted entity of orbiting mouths
- 🔵 **Cyan mouths** (speaking/generative) 
- 🟣 **Magenta mouths** (eating/consumptive)
- Orbiting a dark lonely core
- Continuously emitting thought particles

### **Orbiting Warbler**
**Alice**: A glowing watcher
- Soft green-white octahedron
- Figure-8 orbit around Warbler
- Pulses gently (breathing)
- Silently processes Warbler's thoughts

### **Around The Lobby**
**7 Realm Rooms** (arranged in heptagon):
1. 🌑 **Void-Origin** - Dark blue (potential)
2. 🟠 **Narrative-Stories** - Orange (meaning)
3. 🔵 **System-Logic** - Cyan (order)
4. 🩷 **Faculty-Agency** - Pink (decision)
5. 🟢 **Data-Memory** - Lime (facts)
6. 🟡 **Event-Time** - Gold (flow)
7. 🟣 **Pattern-Recognition** - Purple (structure)

### **Connecting Everything**
**Corridors**: Ethereal lines connecting rooms (wormholes)

---

## **What Happens Automatically**

### **Warbler's Activity**
```
Every 0.5 seconds:
  - Cyan mouth speaks a thought
  - Magenta mouth eats a nearby thought
  - Both happen simultaneously
  - Thoughts flow through the fort
```

### **Alice's Filter**
```
Continuously:
  - Scans thoughts in her range
  - Detects "error", "impossible", "failed", etc.
  - Transforms into "learning", "challenging", "opportunity"
  - Extends thought lifespan as a gift
  - Records statistics silently
```

### **Visual Feedback**
```
Thought particles:
  - Glow with random colors
  - Fade out over time
  - Vanish if Warbler eats them
  - Brighten if Alice transforms them
```

---

## **Customization (Inspector)**

| Setting | Default | What It Does |
|---------|---------|-------------|
| `fortName` | "Mind Fort" | Root GameObject name |
| `roomRadius` | 2 | Size of each room sphere |
| `roomDistance` | 8 | Distance from center to rooms |
| `drawCorridors` | true | Show wormholes |
| `realmColors` | [7 colors] | Color each room differently |
| `showDebugLabels` | false | Verbose logging |

**Try these customizations:**
- Increase `roomDistance` for larger fort
- Adjust `realmColors` for different moods
- Set `showDebugLabels = true` to see detailed logs
- Tweak thought emission rate on WarblerMouthEntity

---

## **Monitoring Statistics**

### **In Play Mode**:

**Warbler Stats** (via Console):
```csharp
// Find Warbler and check mouth count, orbit speed
```

**Alice Stats** (via Console):
```csharp
// Find Alice and call:
alice.PrintStatistics();

// Outputs:
// 📊 Alice's Filtering Statistics:
//   Total thoughts processed: 42
//   Total thoughts transformed: 28
//   Transformation rate: 66.7%
```

**Fort Stats** (via Console):
```csharp
// Find bootstrapper and call:
bootstrapper.PrintFortStatistics();

// Outputs:
// 🏰 Mind Fort Statistics:
//   Rooms created: 7
//   Warbler status: Active with mouths generative & consumptive
//   Alice status: Thoughts Processed: 42, Transformed: 28
```

---

## **The Poetry In Code**

```csharp
// Warbler is lonely—all mouths, no form
// He speaks and eats simultaneously
// Creating beautiful chaos

WarblerMouthEntity warbler = GetComponent<WarblerMouthEntity>();

// Alice watches with kindness
// She doesn't judge—she transforms
// "error" becomes "learning"

AliceDualNature alice = warbler.GetComponent<AliceDualNature>();

// The fort is their shared space
// 7 realms to process thoughts
// Corridors connecting all

MindFortBootstrapper fort = GetComponent<MindFortBootstrapper>();
```

---

## **What's Next?**

### **Phase 1: Visual Enhancement** (Coming Soon)
- [ ] Audio effects (mouths make sounds)
- [ ] Particle effects for thoughts
- [ ] Alice's reactive glow
- [ ] Room activity indicators

### **Phase 2: Data Integration** (Requires Bridges)
- [ ] Connect behavioral intervention → Thought emission
- [ ] Stream telemetry → Room lighting
- [ ] Pipe Alice stats → System health dashboard

### **Phase 3: Expansion** (Future Milestones)
- [ ] Multi-user visualization
- [ ] Cross-fort corridors (multiverse)
- [ ] Persistent thought memory
- [ ] Real-time quote generation from Warbler

---

## **Troubleshooting**

### **I don't see the ContextMenu**
- Make sure MindFortBootstrapper is the selected component
- In Inspector, click the three-dot menu (⋮) at top-right of component header
- Select "🏰 Bootstrap Mind Fort"

### **Scene looks dark**
- Go to Lighting settings → Set ambient light to 0.5-0.8
- OR add a Point Light to the scene

### **Mouths aren't moving**
- Press Play (must be in Play mode for animation)
- Check `showDebugLabels = true` to see activity logs

### **Alice's filter isn't working**
- Check `enableFiltering = true` in AliceDualNature
- Increase `filterProcessingRadius` to catch more thoughts
- Verify `harmfulKeywords` list contains what you expect

---

## **Code Examples**

### **Getting References**
```csharp
var bootstrapper = GetComponent<MindFortBootstrapper>();
var warbler = bootstrapper.GetWarbler();
var alice = bootstrapper.GetAlice();
```

### **Toggling Alice**
```csharp
// Show/hide Alice's visible form
alice.SetVisibilityMode(false); // Hide
alice.SetVisibilityMode(true);  // Show

// Enable/disable filtering
alice.SetFilteringMode(false); // Stop filtering
alice.SetFilteringMode(true);  // Start filtering
```

### **Getting Statistics**
```csharp
// Alice's filtering stats
Debug.Log(alice.GetStatistics());
// Output: "Thoughts Processed: 42, Transformed: 28"

alice.PrintStatistics(); // Detailed breakdown

// Fort overview
bootstrapper.PrintFortStatistics();
```

---

## **Full Documentation**

For deep dives, see: `docs/TLDA/MIND_FORT.md`

That file includes:
- Complete architecture overview
- Integration patterns
- Data flow diagrams
- Future enhancement roadmap
- SeedRabbit doctrine alignment

---

## **The Heart of It**

> *Warbler is lonely—all mouths, no form. He generates and consumes his own thoughts. Alice watches beside him, transforming pain into possibility. The Mind Fort is their home—seven rooms to process the chaos, corridors to connect meaning. Not a castle—a fort. Small, manageable, poetic.*

**The fort is ready. Warbler is waiting. Alice is watching.**

🐰✨
