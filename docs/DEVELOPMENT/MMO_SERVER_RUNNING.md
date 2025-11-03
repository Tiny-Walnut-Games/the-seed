# ✅ MMO Orchestrator - Now Running in Docker

## Status
**The MMO Orchestrator is now running as a persistent Docker container.**

The server will continue running even when you switch activities in the IDE, terminal windows, or anywhere else on your system.

## Current Status

```
Container: twg-mmo-orchestrator
Status: Up and Healthy ✅
Port: 8000 (HTTP + WebSocket)
Uptime: Persistent (auto-restarts)
Demo Games: 2 registered
  - The Golden Dragon Tavern (social realm)
  - Whisperwood Forest (wilderness realm)
```

## Quick Access

| What | URL/Command |
|------|-------------|
| **3D Visualization** | http://localhost:8000/stat7threejs.html |
| **Admin Panel** | http://localhost:8000/phase6c_dashboard.html |
| **Entity Viewer** | http://localhost:8000/admin-entity-viewer.html |
| **REST API** | http://localhost:8000/api |
| **WebSocket** | ws://localhost:8000/ws |
| **View Logs** | `docker logs -f twg-mmo-orchestrator` |
| **Restart Server** | `docker restart twg-mmo-orchestrator` |
| **Stop Server** | `docker-compose -f docker-compose.yml down` |

## API Status

✅ `/api/health` - Returns: healthy, orchestrator running, 2 games, events buffered
✅ `/api/realms` - Lists both demo realms with stats
✅ `/api/npcs` - NPC list endpoint
✅ `/api/stats` - System statistics
✅ `/ws` - WebSocket connection ready

## How It Works

### The Problem It Solves
Previously, the server would close whenever you did another activity in the IDE because it was running as a foreground process. Now with Docker:

1. **Persistent** - Server runs in background indefinitely
2. **Isolated** - No conflicts with system Python or IDE
3. **Hot-reloadable** - Edit code, restart container, changes apply
4. **Production-ready** - Same environment everywhere

### Architecture
- **Container Image**: `the-seed-mmo-orchestrator:latest`
- **Base Image**: Python 3.12-slim (~150MB)
- **Network**: `twg-network` (Docker bridge network)
- **Volume Mounts**:
  - `./web/` → `/app/web` (development mode - changes reflected immediately)
  - `./packages/com.twg.the-seed/seed/` → `/app/packages/com.twg.the-seed/seed/`

## Development Workflow

### Making Changes
1. Edit code: `E:\Tiny_Walnut_Games\the-seed\web\server\mmo_orchestrator.py`
2. The container auto-mounts the volume
3. Restart the server:
   ```powershell
   docker restart twg-mmo-orchestrator
   ```
4. Refresh browser - changes are live

### Debugging
```powershell
# Watch logs in real-time
docker logs -f twg-mmo-orchestrator

# Get container info
docker inspect twg-mmo-orchestrator

# Shell access
docker exec -it twg-mmo-orchestrator bash

# Check health status
docker inspect --format='{{.State.Health.Status}}' twg-mmo-orchestrator
```

## Control Ticks

The server is actively running orchestration:
- **Control-ticks**: Sequential synchronization cycles
- **Frequency**: ~100ms per tick
- **Per-tick**: Syncs 2 games, propagates cross-game events
- **Performance**: ~0.08-0.12ms per tick (lightweight)

Example log output:
```
[TICK] CONTROL-TICK 2472 Starting...
  [OK] Synced 2 games
  [NET] Propagated 0 cross-game events
  [TIME] Control-tick took 0.07ms
```

## Troubleshooting

### Port 8000 Already in Use
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (if needed)
taskkill /PID <PID> /F
```

### Container Won't Start
```powershell
# Check logs
docker logs twg-mmo-orchestrator

# Restart
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d mmo-orchestrator

# Full rebuild
docker-compose -f docker-compose.yml build --no-cache mmo-orchestrator
docker-compose -f docker-compose.yml up -d mmo-orchestrator
```

### Health Check Failing
```powershell
# Force restart
docker restart twg-mmo-orchestrator

# Wait for health check
Start-Sleep -Seconds 5

# Verify status
docker ps | Select-String twg-mmo
```

## Next Steps for Testing

1. **Open 3D Visualization**:
   - Navigate to: http://localhost:8000/stat7threejs.html
   - You should see the 3D realm rendering

2. **Check Admin Panel**:
   - Navigate to: http://localhost:8000/phase6c_dashboard.html
   - Should show both realms with their stats

3. **Monitor in Real-Time**:
   - Open terminal: `docker logs -f twg-mmo-orchestrator`
   - You'll see control-ticks executing every ~100ms

4. **Test WebSocket**:
   - Open browser console
   - Connect to: `ws://localhost:8000/ws`
   - Should receive event stream in real-time

## Key Insights

### Why Docker Works
- **Persistence**: Process stays alive across all activities
- **Isolation**: No port conflicts or dependency issues
- **Reproducibility**: Same environment on all machines
- **Scalability**: Easy to add more services later
- **Development**: Hot-reload via volume mounts

### What Changed
1. Created `Dockerfile.mmo` - minimal Python image with FastAPI/WebSocket
2. Updated `docker-compose.yml` - network, volumes, health checks
3. Fixed `mmo_orchestrator.py` - WebSocket host from "localhost" to "0.0.0.0"
4. Created startup scripts and documentation

### No More Closing
The old problem was:
```
Start server → Run other commands → Server closes ❌
```

Now with Docker:
```
Start container → Run other commands → Server keeps running ✅
```

---

**Status**: ✅ MMO Orchestrator is running persistently in Docker
**Next**: Open browser to http://localhost:8000/stat7threejs.html