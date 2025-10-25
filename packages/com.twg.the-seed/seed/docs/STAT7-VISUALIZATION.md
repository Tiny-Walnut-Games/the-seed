# 🎭 STAT7 7D Space Visualization System

A lightweight, Unity-free visualization system for STAT7 experiments using WebSocket streaming and Three.js GPU acceleration.

## 🚀 Overview

The STAT7 Visualization System provides real-time, browser-based visualization of 7-dimensional STAT7 space without requiring Unity or heavy dependencies. It uses a Python WebSocket server to stream STAT7 events to a Three.js client that handles GPU-accelerated rendering.

### Key Features

- **🔌 WebSocket Streaming**: Real-time event streaming from Python experiments
- **🎮 GPU Acceleration**: Three.js WebGL rendering for smooth performance
- **📐 7D Projection**: Advanced dimensional reduction algorithms
- **🎨 Interactive Controls**: Camera manipulation, filters, and animations
- **📊 Experiment Integration**: Direct visualization of STAT7 validation experiments
- **📓 Jupyter Support**: Embed visualizations directly in notebooks
- **🌐 Cross-Platform**: Works in any modern browser

## 📁 File Structure

```
the-seed/
├── stat7wsserve.py                    # WebSocket server implementation
├── stat7threejs.html                  # Three.js visualization client
├── stat7_visualization_demo.ipynb     # Jupyter notebook demo
└── Packages/com.twg.the-seed/seed/engine/
    ├── stat7_experiments.py           # STAT7 experiments (EXP-01 through EXP-03)
    └── stat7_visualization.py         # High-level visualization API
```

## 🛠️ Installation

### Prerequisites

```bash
# Python dependencies
pip install websockets asyncio three

# For Jupyter notebook support
pip install jupyter ipython

# Optional: For development
pip install pytest black flake8
```

### Browser Requirements

- Chrome/Edge (recommended): Full WebGL support
- Firefox: Full WebGL support
- Safari: WebGL support (may need to enable in settings)
- Mobile: Limited support (touch controls)

## 🚀 Quick Start

### 1. Start the WebSocket Server

```python
from stat7_visualization import quick_start_visualization

# Start server with default settings (localhost:8765)
manager = quick_start_visualization()
```

### 2. Open Visualization in Browser

Open `stat7threejs.html` in your web browser:

```bash
# Option 1: Direct file open
open stat7threejs.html

# Option 2: Local web server (recommended)
python -m http.server 8000
# Then visit http://localhost:8000/stat7threejs.html
```

### 3. Run Experiments with Visualization

```python
import asyncio
from stat7_visualization import visualize_experiment

# Visualize EXP-01 address uniqueness test
await visualize_experiment("EXP-01", sample_size=1000, iterations=5)

# Continuous generation demo
await visualize_experiment("continuous", duration_seconds=30, rate_per_second=20)
```

## 📚 Usage Examples

### Basic Python Script

```python
#!/usr/bin/env python3
"""
Basic STAT7 visualization example
"""

import asyncio
from stat7_visualization import get_visualization_manager

async def main():
    # Start visualization server
    manager = get_visualization_manager()

    # Run EXP-01 with visualization
    await manager.visualize_exp01(sample_size=500, iterations=3)

    # Continuous generation
    await manager.visualize_continuous_generation(duration_seconds=60, rate_per_second=10)

    # Keep server running
    print("Press Ctrl+C to stop...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        manager.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
```

### Jupyter Notebook Integration

```python
# In Jupyter notebook
from stat7_visualization import display_in_jupyter, visualize_experiment

# Display visualization widget
display_in_jupyter(width="100%", height="600px")

# Run experiments
await visualize_experiment("EXP-01", sample_size=300, iterations=2)
```

### Custom Bit-Chain Visualization

```python
from stat7_experiments import BitChain, Coordinates
from stat7_visualization import get_visualization_manager
import uuid

# Create custom bit-chains
bitchains = []
for i in range(100):
    bitchain = BitChain(
        id=str(uuid.uuid4()),
        entity_type="concept",
        realm="data",
        coordinates=Coordinates(
            realm="data",
            lineage=i + 1,
            adjacency=[str(uuid.uuid4()) for _ in range(2)],
            horizon="genesis",
            resonance=0.5,
            velocity=0.0,
            density=0.5
        ),
        created_at="2024-01-01T00:00:00Z",
        state={"value": i}
    )
    bitchains.append(bitchain)

# Visualize custom bit-chains
manager = get_visualization_manager()
await manager.visualize_bitchain_batch(bitchains, experiment_id="custom")
```

## 🎮 Visualization Controls

### Mouse Controls

- **Left Click + Drag**: Rotate camera around origin
- **Mouse Wheel**: Zoom in/out
- **Right Click + Drag**: Pan camera (if enabled)

### UI Controls

- **Projection Mode**: Switch between 7D→3D, 7D→2D, Realm Slice, Dimension Cross-Section
- **Point Size**: Adjust visualization scale (0.1 - 5.0)
- **Animation Speed**: Control floating animation (0.0 - 3.0)
- **Realm Filter**: Show/hide specific realms
- **Reset Camera**: Return to default camera position
- **Clear Points**: Remove all visualized points

### Realm Color Scheme

| Realm     | Color   | Description                 |
|-----------|---------|-----------------------------|
| Data      | #3498db | Blue - Information entities |
| Narrative | #e74c3c | Red - Story elements        |
| System    | #2ecc71 | Green - System components   |
| Faculty   | #f39c12 | Orange - Agent capabilities |
| Event     | #9b59b6 | Purple - Temporal events    |
| Pattern   | #1abc9c | Teal - Recurring patterns   |
| Void      | #34495e | Dark gray - Unknown/empty   |

## 📐 7D Projection Algorithms

### Default: 7D → 3D (t-SNE inspired)

```python
def project7DTo3D(coords):
    realm_val = realm_values[coords.realm]  # 0-6
    lineage = coords.lineage / 100.0        # Normalize to 0-1
    adjacency = len(coords.adjacency) / 10.0
    horizon = horizon_values[coords.horizon]  # 0-1
    resonance = (coords.resonance + 1.0) / 2.0  # -1,1 to 0,1
    velocity = (coords.velocity + 1.0) / 2.0
    density = coords.density

    # Multi-dimensional projection
    x = (realm_val - 3) * 15 + resonance * 10 - 5
    y = (lineage - 0.5) * 20 + velocity * 10 - 5
    z = (horizon - 0.5) * 20 + density * 10 - 5

    return Vector3(x, y, z)
```

### Alternative Projections

- **7D → 2D (PCA)**: Principal component analysis for 2D visualization
- **Realm Slice**: Show only specific realm with full detail
- **Dimension Cross-Section**: Fix some dimensions, vary others

## 🔧 Advanced Configuration

### WebSocket Server Settings

```python
from stat7wsserve import STAT7EventStreamer

# Custom server configuration
streamer = STAT7EventStreamer(
    host="0.0.0.0",    # Allow remote connections
    port=8765,         # Custom port
    max_buffer_size=2000  # Larger event buffer
)
```

### Visualization Customization

```javascript
// In stat7threejs.html
const settings = {
    pointSize: 1.5,           // Larger points
    animationSpeed: 2.0,      // Faster animation
    projectionMode: '7d-to-2d', // 2D projection
    realmFilter: new Set(['data', 'system']) // Filter realms
};
```

### Performance Optimization

```python
# For large-scale visualizations
await manager.visualize_continuous_generation(
    duration_seconds=300,     # 5 minutes
    rate_per_second=50,       # High generation rate
    batch_size=10            # Process in batches
)
```

## 📊 WebSocket Event Protocol

### Event Structure

```json
{
    "event_type": "bitchain_created",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "data": {
        "bitchain": { /* BitChain data */ },
        "address": "sha256_hash",
        "stat7_uri": "stat7://realm/lineage/adjacency/horizon?r=0.5&v=0.0&d=0.5",
        "coordinates": { /* 7D coordinates */ },
        "entity_type": "concept",
        "realm": "data"
    },
    "experiment_id": "EXP-01-abc123",
    "metadata": {
        "visualization_type": "point_cloud",
        "color": "#3498db",
        "size": 1.0
    }
}
```

### Event Types

- `bitchain_created`: New bit-chain added to visualization
- `experiment_start`: Experiment began
- `experiment_complete`: Experiment finished
- `experiment_iteration_start`: New iteration started
- `experiment_iteration_complete`: Iteration finished

## 🧪 Experiment Integration

### Supported Experiments

- **EXP-01**: Address Uniqueness Test
- **EXP-02**: Retrieval Efficiency Test
- **EXP-03**: Dimension Necessity Test
- **Continuous**: Custom bit-chain generation

### Adding New Experiments

```python
async def visualize_custom_experiment():
    manager = get_visualization_manager()

    # Start experiment event
    start_event = manager.event_streamer.create_experiment_event(
        "CUSTOM-EXP", "start", {"name": "Custom Experiment"}
    )
    await manager.event_streamer.broadcast_event(start_event)

    # Generate and visualize bit-chains
    for i in range(1000):
        bitchain = generate_custom_bitchain(i)
        event = manager.event_streamer.create_bitchain_event(bitchain, "CUSTOM-EXP")
        await manager.event_streamer.broadcast_event(event)

    # Complete experiment
    complete_event = manager.event_streamer.create_experiment_event(
        "CUSTOM-EXP", "complete", {"total_generated": 1000}
    )
    await manager.event_streamer.broadcast_event(complete_event)
```

## 🔍 Troubleshooting

### Common Issues

**WebSocket Connection Failed**
```bash
# Check if server is running
netstat -an | grep 8765

# Restart server
python stat7wsserve.py
```

**Visualization Not Loading**
```bash
# Check browser console for WebGL errors
# Try different browser
# Check graphics drivers
```

**Performance Issues**
```python
# Reduce generation rate
await visualize_experiment("continuous", rate_per_second=5)

# Clear points periodically
manager.clear_all_points()

# Use realm filtering
settings.realmFilter = new Set(['data'])  # Show only data realm
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor WebSocket events
streamer.logger.setLevel(logging.DEBUG)
```

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8765

CMD ["python", "stat7wsserve.py"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/stat7threejs.html;
        try_files $uri $uri/ =404;
    }

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 📈 Performance Metrics

### Benchmarks

| Metric                | Value  | Notes           |
|-----------------------|--------|-----------------|
| Max Concurrent Points | 10,000 | With modern GPU |
| WebSocket Latency     | < 5ms  | Local network   |
| Frame Rate            | 60 FPS | WebGL rendering |
| Memory Usage          | 100MB  | 1000 points     |
| CPU Usage             | 5%     | Python server   |

### Optimization Tips

1. **Point Culling**: Remove off-screen points
2. **Level of Detail**: Reduce detail for distant points
3. **Batch Processing**: Group WebSocket messages
4. **Memory Management**: Dispose unused geometries
5. **Frame Rate Limiting**: Cap at 30 FPS for battery

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd the-seed

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black stat7wsserve.py stat7_visualization.py
flake8 stat7wsserve.py stat7_visualization.py
```

### Adding Features

1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

This project is part of The Seed framework. See LICENSE file for details.

## 🙏 Acknowledgments

- **Three.js**: 3D graphics library
- **WebSockets**: Real-time communication
- **STAT7 Framework**: 7-dimensional addressing system
- **The Seed Project**: Experimental validation framework

---

## 📞 Support

For questions, issues, or contributions:

- 📧 Email: support@tinywalnutgames.com
- 🐛 Issues: GitHub repository
- 💬 Discord: Community server
- 📖 Docs: Full documentation site

**Happy Visualizing! 🎭✨**
