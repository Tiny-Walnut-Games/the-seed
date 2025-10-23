@echo off
REM STAT7 Test Runner - Windows Batch Version
REM This avoids PowerShell quoting issues in IDEs

echo.
echo ========================================
echo   STAT7 Visualization Test Suite
echo ========================================
echo.

cd /d "E:\Tiny_Walnut_Games\the-seed"

echo Running Python test runner...
python run_stat7_tests.py

echo.
echo Tests completed. Press any key to close...
pause > nul