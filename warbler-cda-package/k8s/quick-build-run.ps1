# Build and deploy script - all in one

Write-Host "🔨 Building Warbler CDA image with full API dependencies..." -ForegroundColor Cyan

$currentDir = Get-Location
$projectDir = $currentDir

# Navigate to project root if in k8s directory
if ($currentDir.Path -match '\\k8s$') {
    $projectDir = Split-Path $currentDir -Parent
    Set-Location $projectDir
    Write-Host "   Changed to project directory: $projectDir" -ForegroundColor Gray
}

# Build the image
Write-Host "   Building Docker image..." -ForegroundColor Gray
& docker build -t warbler-cda:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built successfully" -ForegroundColor Green

# Deploy to Kubernetes
Set-Location "$currentDir"
Write-Host ""
Write-Host "🚀 Deploying to Kubernetes..." -ForegroundColor Cyan

# Apply manifests
& kubectl apply -f namespace.yaml
& kubectl apply -f configmap.yaml
& kubectl apply -f deployment.yaml
& kubectl apply -f service.yaml
& kubectl apply -f ingress.yaml

Write-Host "⏳ Waiting for pod to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check status
Write-Host ""
Write-Host "📊 Status:" -ForegroundColor Cyan
$podStatus = & kubectl get pods -n warbler-cda 2>$null
if ($podStatus) {
    Write-Host $podStatus
} else {
    Write-Host "❌ No pods found - check for errors" -ForegroundColor Red
    & kubectl get events -n warbler-cda --sort-by=.metadata.creationTimestamp | Select-Object -Last 5
}

# Check if pod is running
$podRunning = & kubectl get pods -n warbler-cda -o jsonpath='{.items[0].status.phase}' 2>$null
if ($podRunning -eq "Running") {
    Write-Host ""
    Write-Host "🎉 SUCCESS! Your API service is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📖 Access your application:" -ForegroundColor Cyan
    Write-Host "   kubectl port-forward svc/warbler-cda-service 8001:80 -n warbler-cda" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Then visit: http://localhost:8001/health" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔍 Debug commands:" -ForegroundColor Gray
Write-Host "   kubectl logs deployment/warbler-cda -n warbler-cda" -ForegroundColor Gray
Write-Host "   kubectl describe pod -n warbler-cda" -ForegroundColor Gray
