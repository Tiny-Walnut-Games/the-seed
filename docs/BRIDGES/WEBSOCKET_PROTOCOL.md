# 🎭 STAT7 7D Space Visualization System

Real-time visualization of STAT7 experiments using WebSocket streaming and Three.js rendering for academic publication and peer review.

## ⚡ Quick Start

### Option 1: Complete Launcher (Recommended)
```bash
python launch_stat7_complete.py
```

### Option 2: Windows Batch File
```bash
start_visualization.bat
```

### Option 3: Manual Launch
```bash
# Terminal 1: Start web server
python simple_web_server.py

# Terminal 2: Start WebSocket server
python stat7wsserve.py
```

## 🔧 System Requirements

- **Python 3.8+**
- **Required packages:** `websockets`
- **Browser:** Chrome, Firefox, or Edge with WebGL support
- **Ports:** 8000 (web server), 8765 (WebSocket server)

## 📦 Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements-visualization.txt
   ```

2. **Run diagnostics (optional but recommended):**
   ```bash
   python diagnose_stat7.py
   ```

3. **Launch the system:**
   ```bash
   python launch_stat7_complete.py
   ```

## 🎮 Available Commands

Once the WebSocket server is running, you can use these commands:

- `exp01` - Run EXP-01 Address Uniqueness Test (300 entities, 3 iterations)
- `continuous` - Continuous bit-chain generation (30 seconds)
- `semantic` - Semantic fidelity proof (clustering test)
- `resilience` - System resilience testing (stress test)
- `quit` - Stop the visualization system

## 🏗️ System Architecture

### Components

1. **Python WebSocket Server** (`stat7wsserve.py`)
   - Streams STAT7 events in real-time
   - Handles experiment orchestration
   - Provides semantic fidelity and resilience proofs

2. **Three.js Visualization** (`stat7threejs.html`)
   - GPU-accelerated 7D→3D projection
   - Interactive controls and filtering
   - Real-time entity rendering

3. **Modular JavaScript Architecture:**
   - `stat7-core.js` - Three.js engine and 7D projection
   - `stat7-websocket.js` - WebSocket client management
   - `stat7-ui.js` - User interface and controls
   - `stat7-main.js` - Main orchestration class

4. **Web Server** (`simple_web_server.py`)
   - Serves HTML/JS files with CORS support
   - Automatic port detection and browser launch

### Data Flow

```
STAT7 Experiments → WebSocket Server → Browser Client → Three.js Renderer
```

## 🧪 Experiment Visualizations

### EXP-01: Address Uniqueness
- Visualizes bit-chain generation and uniqueness testing
- Real-time streaming of entity creation
- Statistical validation of address collision rates

### Semantic Fidelity Proof
- Tests if clustering reflects narrative similarity
- Creates themed entity groups
- Validates 7D coordinate semantic meaning

### Resilience Testing
- Tests system behavior under stress
- Simulates corrupted/adversarial entities
- Validates system stability and error handling

### Continuous Generation
- Sustained bit-chain creation for performance testing
- Configurable generation rate and duration
- Real-time visualization stress testing

## 🎨 Visualization Features

### 7D Coordinate Projection
- **Realm** → Color coding (7 realms)
- **Lineage** → X-axis positioning
- **Resonance** → Y-axis positioning  
- **Velocity** → Z-axis positioning
- **Density** → Entity size/opacity
- **Horizon** → Animation phase
- **Adjacency** → Connection lines (planned)

### Interactive Controls
- **Camera:** Mouse drag (rotate), wheel (zoom), right-click (pan)
- **Filtering:** Show/hide specific realms
- **Search:** Find entities by ID, type, or realm
- **Animation:** Adjustable speed and effects
- **Entity Details:** Click entities for detailed information

### Real-time Statistics
- Total/visible entity count
- Frame rate monitoring
- WebSocket events received
- Active experiment tracking

## 🔍 Troubleshooting

### Common Issues

1. **"WebSocket connection failed"**
   - Ensure WebSocket server is running (`python stat7wsserve.py`)
   - Check port 8765 is not blocked

2. **"Web page not loading"**
   - Ensure web server is running (`python simple_web_server.py`)
   - Check ports 8000-8020 range

3. **"No entities appearing"**
   - Type commands in WebSocket server terminal (`exp01`, `continuous`)
   - Check browser console for JavaScript errors

4. **"JavaScript syntax errors"**
   - Run `python diagnose_stat7.py` to check file integrity
   - Verify all .js files are complete and properly formatted

### Diagnostic Tool
```bash
python diagnose_stat7.py
```

This tool checks:
- Python version compatibility
- Required package availability  
- File presence and integrity
- JavaScript syntax validation
- Port availability
- Basic functionality tests

## 📊 Academic Usage

This visualization system is designed for:

- **Research Papers:** Real-time demonstration of STAT7 experiments
- **Peer Review:** Interactive validation of theoretical claims
- **Conference Presentations:** Live experiment execution
- **Educational Purposes:** Understanding 7D coordinate systems

### Publication Features

- **Reproducible Results:** Seeded random generation
- **Performance Metrics:** Built-in FPS and throughput monitoring
- **Export Capabilities:** Screenshots and data extraction
- **Statistical Validation:** Automated proof generation

## 🚀 Development

### Adding New Experiments

1. **WebSocket Server Side** (`stat7wsserve.py`):
   ```python
   async def visualize_your_experiment(self, params):
       experiment_id = f"YOUR-EXP-{uuid.uuid4().hex[:8]}"
       # Create and stream bitchains
       # Send completion event
   ```

2. **Client Side** (`stat7-ui.js`):
   ```javascript
   // Add UI controls and event handlers
   ```

### Customizing Visualization

- **Colors:** Modify `getRealmColor()` in `stat7-core.js`
- **Projections:** Update `project7DTo3D()` for different mappings
- **Animations:** Adjust animation loops in `animate()` method
- **UI:** Modify HTML/CSS for different layouts

## 📋 File Reference

### Core Files
- `stat7wsserve.py` - WebSocket server and experiment engine
- `stat7threejs.html` - Main visualization page
- `stat7-*.js` - Modular JavaScript components
- `simple_web_server.py` - Static file server

### Launcher Files  
- `launch_stat7_complete.py` - Complete system launcher
- `start_visualization.bat` - Windows batch launcher
- `start_stat7_visualization.py` - Alternative launcher

### Utility Files
- `diagnose_stat7.py` - System diagnostics
- `requirements-visualization.txt` - Python dependencies
- `test_*.py` - Various test scripts

### Documentation
- `stat7_visualization_demo.ipynb` - Jupyter notebook demo
- `README-STAT7-Visualization.md` - This file

## 🎉 Success Indicators

When everything is working correctly, you should see:

1. ✅ Web server starts and opens browser automatically
2. ✅ WebSocket server connects (green indicator in browser)
3. ✅ Commands like `exp01` generate visible entities
4. ✅ Entities appear as colored spheres in 3D space
5. ✅ Interactive controls (camera, filtering) work smoothly
6. ✅ Real-time statistics update correctly

---

**Ready to visualize your STAT7 experiments!** 🚀

Start with `python launch_stat7_complete.py` and type `exp01` to see your first visualization.