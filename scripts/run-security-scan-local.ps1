# PowerShell script to run security scans locally using Docker
# Supports Windows, Mac, and Linux
# Usage: ./scripts/run-security-scan-local.ps1

param(
    [string]$ScanType = "full",  # full, bandit, pip-audit, semgrep, trufflehog
    [string]$ScanPath = "."
)

$ErrorActionPreference = "Stop"

Write-Host "🛡️  Security Scan Runner (Local Docker)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
$dockerCheck = docker --version 2>$null
if (-not $dockerCheck) {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Install Docker from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker found: $dockerCheck" -ForegroundColor Green

# Build security Docker image
Write-Host ""
Write-Host "🔨 Building security scanning image..." -ForegroundColor Cyan
$imageTag = "twg-security-scanner:latest"

docker build -f Dockerfile.security -t $imageTag . 2>&1 | Write-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built successfully" -ForegroundColor Green
Write-Host ""

# Prepare scan commands
$scanCommands = @{
    "bandit" = "bandit -r scripts/ src/ packages/ -f json -o /results/bandit-results.json"
    "pip-audit" = "pip-audit --format json --output /results/pip-audit-results.json"
    "safety" = "safety check --json --output /results/safety-results.json"
    "trufflehog" = "trufflehog filesystem /code --json > /results/trufflehog-results.json"
    "semgrep" = "semgrep --config=auto --json --output=/results/semgrep-results.json /code/scripts /code/packages"
    "full" = "bash -c 'echo Running full security scan... && (bandit -r scripts/ src/ packages/ -f json -o /results/bandit.json 2>/dev/null || true) && (pip-audit --format json --output /results/pip-audit.json 2>/dev/null || true) && (safety check --json --output /results/safety.json 2>/dev/null || true) && (trufflehog filesystem /code --json > /results/trufflehog.json 2>/dev/null || true) && (semgrep --config=auto --json --output=/results/semgrep.json /code 2>/dev/null || true) && echo ✅ Full scan complete'"
}

$command = $scanCommands[$ScanType]
if (-not $command) {
    Write-Host "❌ Unknown scan type: $ScanType" -ForegroundColor Red
    Write-Host "Available options: $(($scanCommands.Keys -join ', '))" -ForegroundColor Yellow
    exit 1
}

# Create results directory if it doesn't exist
$resultsDir = Join-Path (Get-Location) "security-results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
}

Write-Host "🔍 Running $ScanType scan..." -ForegroundColor Cyan
Write-Host ""

# Run container
docker run --rm `
    -v "${PWD}:/code" `
    -v "${resultsDir}:/results" `
    $imageTag `
    bash -c $command

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Scan completed successfully" -ForegroundColor Green
    Write-Host "📁 Results saved to: $resultsDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Result files:"
    Get-ChildItem $resultsDir | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "⚠️  Scan completed with warnings or non-critical issues" -ForegroundColor Yellow
    Write-Host "📁 Results saved to: $resultsDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "🛡️  Security scan runner finished" -ForegroundColor Cyan