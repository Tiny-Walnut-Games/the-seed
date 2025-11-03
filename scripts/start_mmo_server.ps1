# MMO Orchestrator Server Launcher (Docker-based)
# Persistent background service that stays alive across IDE activity

Write-Host "=" * 70
Write-Host "🐳 THE SEED - MMO ORCHESTRATOR (DOCKER)" -ForegroundColor Cyan
Write-Host "=" * 70

# Check if Docker is installed
Write-Host "`n[CHECK] Verifying Docker installation..."
try {
    $docker_version = docker --version
    Write-Host "[OK] Docker found: $docker_version" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop:" -ForegroundColor Red
    Write-Host "  https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if container is already running
Write-Host "`n[CHECK] Checking for existing MMO container..."
$existing = docker ps --filter "name=twg-mmo-orchestrator" --format "{{.Status}}"
if ($existing) {
    Write-Host "[INFO] Container already running: $existing" -ForegroundColor Yellow
    Write-Host "[INFO] To restart: docker restart twg-mmo-orchestrator"
    Write-Host "[INFO] To view logs: docker logs -f twg-mmo-orchestrator"
} else {
    Write-Host "[ACTION] Starting MMO Orchestrator container..."
    
    # Build and start with docker-compose
    docker-compose -f docker-compose.yml up -d mmo-orchestrator
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Container started successfully" -ForegroundColor Green
        Write-Host "`n[WAIT] Waiting for server to be ready..." -ForegroundColor Cyan
        
        # Wait for health check to pass (up to 30 seconds)
        $retry = 0
        while ($retry -lt 30) {
            Start-Sleep -Seconds 1
            $health = docker inspect --format='{{.State.Health.Status}}' twg-mmo-orchestrator 2>$null
            if ($health -eq "healthy") {
                Write-Host "[OK] Server is healthy!" -ForegroundColor Green
                break
            }
            $retry++
            Write-Host "." -NoNewline
        }
    } else {
        Write-Host "[ERROR] Failed to start container" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n" + "=" * 70
Write-Host "✅ MMO ORCHESTRATOR IS RUNNING" -ForegroundColor Green
Write-Host "=" * 70

Write-Host "`n📍 ACCESS POINTS:"
Write-Host "  🌐 HTTP API:              http://localhost:8000/api"
Write-Host "  🔌 WebSocket:             ws://localhost:8000/ws"
Write-Host "  📊 3D Visualization:      http://localhost:8000/stat7threejs.html"
Write-Host "  🎛️  Admin Dashboard:       http://localhost:8000/phase6c_dashboard.html"
Write-Host "  👁️  Entity Viewer:         http://localhost:8000/admin-entity-viewer.html"

Write-Host "`n⚙️  DOCKER COMMANDS:"
Write-Host "  View live logs:           docker logs -f twg-mmo-orchestrator"
Write-Host "  Restart server:           docker restart twg-mmo-orchestrator"
Write-Host "  Stop server:              docker-compose -f docker-compose.yml down"
Write-Host "  Rebuild image:            docker-compose -f docker-compose.yml build --no-cache"
Write-Host "  Shell access:             docker exec -it twg-mmo-orchestrator bash"

Write-Host "`n💡 WORKFLOW:"
Write-Host "  1. Edit code in ./web/server/mmo_orchestrator.py"
Write-Host "  2. Container auto-mounts the volume"
Write-Host "  3. Restart with: docker restart twg-mmo-orchestrator"
Write-Host "  4. Changes take effect immediately"

Write-Host "`n" + "=" * 70