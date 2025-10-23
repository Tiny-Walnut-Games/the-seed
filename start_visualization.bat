@echo off
echo 🚀 Starting STAT7 Visualization System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "stat7wsserve.py" (
    echo ❌ stat7wsserve.py not found in current directory
    echo Please make sure you're running this from the-seed directory
    pause
    exit /b 1
)

if not exist "stat7threejs.html" (
    echo ❌ stat7threejs.html not found in current directory
    echo Please make sure you're running this from the-seed directory
    pause
    exit /b 1
)

REM Install required packages if not already installed
echo 📦 Checking dependencies...
python -c "import websockets" 2>nul
if errorlevel 1 (
    echo Installing websockets...
    pip install websockets
)

REM Start the visualization launcher
echo 🌐 Starting STAT7 Visualization...
python start_stat7_visualization.py

pause
