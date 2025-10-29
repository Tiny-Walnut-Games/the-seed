# 📚 API Documentation

**API references for all three systems.**

---

## 🔗 **System APIs**

### **Unity API (TLDA)**
- **Documentation:** [UNITY_API.md](UNITY_API.md)
- **Components:** Companion system, Warbler NPC, STAT7 integration
- **Location:** `Assets/Plugins/TWG/TLDA/Scripts/`

### **Python API (Seed)**
- **Documentation:** [PYTHON_API.md](PYTHON_API.md)
- **Components:** STAT7 experiments, Living Dev Agent, WebSocket server
- **Location:** `Packages/com.twg.the-seed/seed/engine/`

### **JavaScript API (Bridges)**
- **Documentation:** [JAVASCRIPT_API.md](JAVASCRIPT_API.md)
- **Components:** WebSocket client, 7D→3D projection, UI controls
- **Location:** `web/js/`

---

## 🔄 **Cross-System Communication**

### **WebSocket Protocol**
- **Port:** 8765 (WebSocket), 8001 (HTTP)
- **Format:** JSON event streaming
- **Documentation:** [../BRIDGES/WEBSOCKET_PROTOCOL.md](../BRIDGES/WEBSOCKET_PROTOCOL.md)

### **Data Schemas**
- **Location:** `Packages/com.twg.the-seed/schemas/`
- **Format:** JSON Schema validation
- **Purpose:** Ensure data contract compatibility

---

## 📋 **API Usage Examples**

### **Unity to Python:**
```csharp
// Send event to Seed backend
var eventData = new { event_type = "battle_complete", data = battleData };
webSocketClient.SendJson(eventData);
```

### **Python to Unity:**
```python
# Broadcast STAT7 entity to Unity
event = VisualizationEvent(event_type="bitchain_created", data=entity_data)
await streamer.broadcast_event(event)
```

### **JavaScript Bridge:**
```javascript
// Handle WebSocket events
websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    stat7Core.addEntity(data);
};
```

---

## 📚 **Related Documentation**

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture
- **[BRIDGES/README.md](../BRIDGES/README.md)** - Bridge components

---

**APIs enable clean integration between the three systems while maintaining proper separation of concerns.**
