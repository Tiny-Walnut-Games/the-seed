# 🔗 Bridge Components Documentation

**Communication layer connecting TLDA and Seed systems.**

---

## 🎯 **Bridge Overview**

Bridge components enable **seamless communication** between the Unity-based TLDA system and the Python-based Seed system. They handle data translation, protocol management, and real-time event streaming.

---

## 🌐 **Key Bridge Components**

### **WebSocket Bridge**
- **Documentation:** [WEBSOCKET_PROTOCOL.md](WEBSOCKET_PROTOCOL.md)
- **Purpose:** Real-time event streaming between systems
- **Location:** `web/js/stat7-websocket.js`, `web/server/stat7wsserve.py`

### **7D→3D Projection**
- **Purpose:** Convert STAT7 7D coordinates to 3D visualization
- **Location:** `web/js/stat7-core.js`, Unity visualization components

### **Unity↔Python Data Bridge**
- **Purpose:** Data serialization and translation
- **Location:** `Assets/Plugins/TWG/TLDA/Scripts/Visualization/`

---

## 📚 **Related Documentation**

- **[TLDA/README.md](../TLDA/README.md)** - Unity system documentation
- **[SEED/README.md](../SEED/README.md)** - Python backend documentation
- **[API/JAVASCRIPT_API.md](../API/JAVASCRIPT_API.md)** - JavaScript API reference

---

**Bridge components enable the multiverse vision by keeping systems separate but tightly integrated.**
