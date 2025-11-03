# MMO Orchestrator - Docker Quick Start Guide

## Problem We Solved
The previous approach had the WebSocket server close whenever you switched activities in the IDE. This is because the server was running as a foreground process in PowerShell. Now with Docker, the server runs as a **persistent background service** that survives IDE activity, terminal switches, and everything else.

## Requirements
- **Docker Desktop** installed and running on Windows
  - Download: https://www.docker.com/products/docker-desktop
  - After installation, ensure Docker daemon is running

## Quick Start (5 minutes)

### Option 1: PowerShell Script (Recommended)
```powershell
# From repository root
.\start_mmo_server.ps1
```

This script will:
1. ✅ Verify Docker is installed
2. ✅ Build the Docker image (first time only)
3. ✅ Start the container in background
4. ✅ Wait for the server to be healthy
5. ✅ Display access points and commands

### Option 2: Manual Docker Commands
```powershell
# Build the image
docker build -f Dockerfile.mmo -t twg-mmo:latest .

# Start with docker-compose (recommended - handles networking/volumes)
docker-compose -f docker-compose.yml up -d mmo-orchestrator

# Or start directly
docker run -d `
  --name twg-mmo-orchestrator `
  -p 8000:8000 `
  -v ${PWD}/web:/app/web `
  twg-mmo:latest
```

## Access the Services

Once running, open these URLs in your browser:

| Service | URL |
|---------|-----|
| **3D Visualization** (main) | http://localhost:8000/stat7threejs.html |
| Admin Panel | http://localhost:8000/phase6c_dashboard.html |
| Entity Viewer | http://localhost:8000/admin-entity-viewer.html |
| REST API Base | http://localhost:8000/api |
| WebSocket | ws://localhost:8000/ws |

### Key Endpoints to Test
```bash
# Health check
curl http://localhost:8000/api/health

# List registered games/realms
curl http://localhost:8000/api/realms

# System statistics
curl http://localhost:8000/api/stats
```

## Development Workflow

### Making Code Changes
1. **Edit server code**: `web/server/mmo_orchestrator.py`
2. **Container auto-mounts** the `./web` volume
3. **Restart the server**:
   ```powershell
   docker restart twg-mmo-orchestrator
   ```
4. Changes take effect immediately

### Debugging & Monitoring

```powershell
# View live logs (Ctrl+C to exit)
docker logs -f twg-mmo-orchestrator

# Get container status
docker ps | Select-String twg-mmo

# Shell access (for debugging)
docker exec -it twg-mmo-orchestrator bash

# Inspect container details
docker inspect twg-mmo-orchestrator
```

### Stopping & Cleaning Up

```powershell
# Stop container
docker-compose -f docker-compose.yml down

# Stop and remove container
docker rm -f twg-mmo-orchestrator

# Remove image (frees space)
docker rmi twg-mmo:latest

# Deep clean (prune everything - careful!)
docker system prune -a
```

## Common Issues

### Container won't start
```powershell
# Check logs for errors
docker logs twg-mmo-orchestrator

# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill process using port 8000 (PowerShell admin)
Get-Process | Where-Object {$_.Handles -match "8000"} | Stop-Process -Force
```

### Connection refused when accessing `http://localhost:8000`
- Wait 10 seconds after starting (server needs time to initialize)
- Verify container is running: `docker ps | Select-String twg-mmo`
- Check health: `docker inspect --format='{{.State.Health.Status}}' twg-mmo-orchestrator`

### WebSocket connection fails
- Ensure JavaScript connects to `ws://localhost:8000/ws` (not `ws://0.0.0.0:...`)
- Check browser console for errors
- Verify container logs: `docker logs -f twg-mmo-orchestrator`

## Architecture Notes

### Why Docker?
- **Persistent**: Server keeps running even when IDE is active
- **Isolated**: No dependency conflicts with system Python
- **Reproducible**: Same environment on all machines
- **Hot-reload friendly**: Volumes allow code changes without rebuild
- **Production-ready**: Can deploy same container to cloud

### Container Details
- **Image**: Python 3.12-slim (minimal size ~150MB)
- **Ports**: 8000 (HTTP + WebSocket)
- **Health Check**: Pings `/api/health` every 30s
- **Restart Policy**: auto-restart unless stopped manually
- **Volumes**: 
  - `./web` → read-write for development
  - `./packages/com.twg.the-seed/seed` → for backend changes

### Network Mode
- Container binds to `0.0.0.0:8000` (all interfaces)
- Host accesses via `localhost:8000`
- Named network `twg-network` allows multi-container communication (future extensibility)

## Next Steps

1. **Start the server**: `.\start_mmo_server.ps1`
2. **Open 3D visualization**: http://localhost:8000/stat7threejs.html
3. **Check admin panel**: http://localhost:8000/phase6c_dashboard.html
4. **View logs**: `docker logs -f twg-mmo-orchestrator`
5. **Make a change** to `web/server/mmo_orchestrator.py`
6. **Restart**: `docker restart twg-mmo-orchestrator`
7. **Verify**: Refresh browser, changes should be live

---

**Status**: Docker containerization complete. Server runs persistently now. ✅