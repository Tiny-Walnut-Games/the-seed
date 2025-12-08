# Direct Python API Runner (Windows)
# Bypasses Docker networking issues

Write-Host "🚀 Starting Warbler CDA FractalStat API (Direct Python)" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment is activated (optional)
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment active: $($env:VIRTUAL_ENV)" -ForegroundColor Green
} else {
    Write-Host "[Info]  Consider activating virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

# Set environment variables
$env:FRACTALSTAT_TESTING = "true"
$env:PYTHONPATH = "$PWD"

Write-Host ""
Write-Host "📦 Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "   Access at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   Health check: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host "   API docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Run the API service directly with detailed error capture
Write-Host "🔧 Starting API service with debug output..." -ForegroundColor Cyan
Write-Host "   This will show import progress and any startup issues" -ForegroundColor Gray
Write-Host ""

try {
    python start_server.py 2>&1
} catch {
    Write-Host "❌ Error running API service:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
