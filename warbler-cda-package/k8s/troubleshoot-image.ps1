# Quick troubleshooting for Docker-K8s image issues

Write-Host "🔍 Troubleshooting Docker Image in Kubernetes..." -ForegroundColor Cyan
Write-Host ""

# Check if image exists
Write-Host "1. Checking if Docker image exists..." -ForegroundColor Yellow
$images = & docker images --format "{{.Repository}}:{{.Tag}}"
if ($images -contains "warbler-cda:latest") {
    Write-Host "   ✅ Image warbler-cda:latest exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ Image warbler-cda:latest NOT found" -ForegroundColor Red
}

# Try creating a simple test pod
Write-Host ""
Write-Host "2. Testing if Kubernetes can pull the image..." -ForegroundColor Yellow
try {
    $testPod = & kubectl run test-image --image=warbler-cda:latest --restart=Never --namespace=warbler-cda echo "Image works!" 2>$null
    Start-Sleep -Seconds 5

    $status = & kubectl get pod test-image -n warbler-cda -o jsonpath='{.status.phase}' 2>$null
    if ($status -eq "Succeeded") {
        Write-Host "   ✅ Kubernetes can access the image" -ForegroundColor Green
        & kubectl logs test-image -n warbler-cda 2>$null | Write-Host "   Logs: $_" -ForegroundColor Gray
    } elseif ($status -eq "Pending") {
        Write-Host "   ⏳ Still pulling image..." -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ Image pull failed - check pod status" -ForegroundColor Red
        & kubectl describe pod test-image -n warbler-cda 2>$null | Select-Object -Last 10
    }

    # Clean up test pod
    & kubectl delete pod test-image -n warbler-cda --ignore-not-found=true 2>$null | Out-Null
} catch {
    Write-Host "   ❌ Could not create test pod" -ForegroundColor Red
}

# Check the actual deployment pod
Write-Host ""
Write-Host "3. Checking current deployment pod..." -ForegroundColor Yellow
$podStatus = & kubectl get pods -n warbler-cda -l app=warbler-cda 2>$null
Write-Host $podStatus

$podName = (& kubectl get pods -n warbler-cda -l app=warbler-cda -o jsonpath='{.items[0].metadata.name}' 2>$null)
if ($podName) {
    Write-Host ""
    Write-Host "   Pod details for $podName:" -ForegroundColor Gray
    & kubectl describe pod $podName -n warbler-cda 2>$null | Select-Object -Last 15
}

# Alternative: Force reload image
Write-Host ""
Write-Host "4. Force reload suggestion:" -ForegroundColor Yellow
Write-Host "   If image exists but K8s can't pull it, try:" -ForegroundColor Gray
Write-Host "   kubectl rollout restart deployment warbler-cda -n warbler-cda" -ForegroundColor Cyan

Write-Host ""
Write-Host "5. Or rebuild and redeploy:" -ForegroundColor Yellow
Write-Host "   .\quick-build-run.ps1" -ForegroundColor Cyan
