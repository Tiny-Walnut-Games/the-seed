# 🚀 MMO Orchestrator - Quick Reference

## Status Now
```
✅ Server Running:    twg-mmo-orchestrator
✅ Health Status:     healthy
✅ API:               responding
✅ Games:             2 registered
✅ Persistence:       guaranteed
```

## Open in Browser
| What | Link |
|------|------|
| 3D Visualization | http://localhost:8000/stat7threejs.html |
| Admin Panel | http://localhost:8000/phase6c_dashboard.html |
| Entity Viewer | http://localhost:8000/admin-entity-viewer.html |

## Docker Commands

### Monitor
```powershell
docker logs -f twg-mmo-orchestrator      # Watch logs live
docker ps | Select-String twg-mmo        # Check container status
docker inspect --format='{{.State.Health.Status}}' twg-mmo-orchestrator
```

### Restart
```powershell
docker restart twg-mmo-orchestrator      # Fast restart (2-5s)
```

### Stop
```powershell
docker-compose -f docker-compose.yml down
```

### Rebuild
```powershell
docker-compose -f docker-compose.yml build --no-cache mmo-orchestrator
docker-compose -f docker-compose.yml up -d mmo-orchestrator
```

## Code Changes Workflow
```
1. Edit: web/server/mmo_orchestrator.py
2. Run:  docker restart twg-mmo-orchestrator
3. Done: Changes live in 2-5 seconds
```

## API Endpoints

### Health
```
GET http://localhost:8000/api/health
```

### Realms (Games)
```
GET http://localhost:8000/api/realms
```

### Stats
```
GET http://localhost:8000/api/stats
```

### WebSocket
```
ws://localhost:8000/ws
```

## Key Facts

- 🐳 **Running in Docker** - Persistent background service
- 🔌 **Port 8000** - HTTP + WebSocket
- 📊 **2 Games** - The Golden Dragon Tavern, Whisperwood Forest
- ⚡ **Control Ticks** - Executing ~100ms intervals
- 🔄 **Auto Restart** - Survives crashes
- 📁 **Volume Mounts** - Live code changes reflected

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port in use | `taskkill /PID <PID> /F` |
| Container won't start | `docker logs twg-mmo-orchestrator` |
| Health check failing | `Start-Sleep -Seconds 5; docker restart twg-mmo-orchestrator` |
| WebSocket not connecting | Verify health check passing, check browser console |

## Documentation Files

- `DOCKER_QUICK_START.md` - Setup guide
- `MMO_SERVER_RUNNING.md` - Current status
- `DOCKER_DEPLOYMENT_COMPLETE.md` - Full deployment report
- `IMPLEMENTATION_COMPLETE.md` - What was fixed and why

---

**TL;DR**: Server is running in Docker on port 8000. Open http://localhost:8000/stat7threejs.html to see it. It won't close no matter what you do. ✅