# Windows PowerShell script to deploy directly to Docker Desktop K8s

Write-Host "🔧 Deploying Warbler CDA to Docker Desktop Kubernetes (Windows)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Check Docker
try {
    & docker info 2>&1 | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check kubectl connectivity
try {
    & kubectl cluster-info 2>&1 | Out-Null
    Write-Host "✅ Kubernetes is accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to Kubernetes cluster." -ForegroundColor Red
    Write-Host "   Enable Kubernetes in Docker Desktop Settings → Kubernetes" -ForegroundColor Yellow
    exit 1
}

# Build Docker image
Write-Host ""
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan
$currentDir = Get-Location
$projectDir = Split-Path $currentDir -Parent

Write-Host "   Building from: $projectDir" -ForegroundColor Gray
Set-Location $projectDir

try {
    & docker build -t warbler-cda:latest .
    Write-Host "✅ Image built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

Set-Location $currentDir

# Apply Kubernetes manifests
Write-Host ""
Write-Host "🚀 Deploying to Kubernetes..." -ForegroundColor Cyan

# Create namespace first
Write-Host "   Creating namespace..." -ForegroundColor Gray
try {
    & kubectl apply -f namespace.yaml
    Write-Host "   ✅ Namespace created" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to create namespace" -ForegroundColor Red
    exit 1
}

# Apply configs
Write-Host "   Applying ConfigMap..." -ForegroundColor Gray
& kubectl apply -f configmap.yaml

Write-Host "   Creating PVC..." -ForegroundColor Gray
& kubectl apply -f pvc.yaml

Write-Host "   Deploying application..." -ForegroundColor Gray
& kubectl apply -f deployment.yaml

Write-Host "   Creating service..." -ForegroundColor Gray
& kubectl apply -f service.yaml

Write-Host "   Creating ingress..." -ForegroundColor Gray
& kubectl apply -f ingress.yaml

# Wait for pod to be ready
Write-Host ""
Write-Host "⏳ Waiting for pod to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
Write-Host ""
Write-Host "📊 Deployment Status:" -ForegroundColor Cyan
& kubectl get pods -n warbler-cda
Write-Host ""
& kubectl get svc -n warbler-cda

Write-Host ""
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Access your application:" -ForegroundColor Cyan
Write-Host "   Run this in a new terminal:"
Write-Host "   kubectl port-forward svc/warbler-cda-service 8001:80 -n warbler-cda" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Then visit: http://localhost:8001/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 Monitor:"
Write-Host "   kubectl logs -f deployment/warbler-cda -n warbler-cda"
