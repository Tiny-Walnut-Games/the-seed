@echo off
echo 🚀 STAT7 Visualization System Launcher
echo ===================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if required files exist
if not exist "stat7wsserve.py" (
    echo ❌ stat7wsserve.py not found
    pause
    exit /b 1
)

if not exist "stat7threejs.html" (
    echo ❌ stat7threejs.html not found
    pause
    exit /b 1
)

echo ✅ Required files found

REM Start web server in background
echo 🌐 Starting web server...
start "STAT7 Web Server" cmd /c "python simple_web_server.py"

REM Wait a moment for web server to start
timeout /t 3 /nobreak >nul

REM Start WebSocket server (this will be interactive)
echo 🔌 Starting WebSocket server...
echo.
echo 📋 Instructions:
echo    1. Web server is running in background window
echo    2. WebSocket server starting below (interactive)
echo    3. Type 'exp01' to run EXP-01 visualization
echo    4. Type 'continuous' for continuous generation
echo    5. Type 'quit' to stop
echo.

python stat7wsserve.py

echo.
echo 👋 STAT7 Visualization System stopped
pause