@echo off
echo ========================================
echo    QUICK START - TRADING SIGNALS
echo ========================================
echo.

echo Step 1: Setting PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
echo ✅ Execution policy updated

echo.
echo Step 2: Installing Python packages...
py -m pip install -r requirements.txt
echo ✅ Packages installed

echo.
echo Step 3: Starting the server...
echo Server will be available at: http://localhost:8002
echo Press Ctrl+C to stop the server
echo.
py server.py

echo.
echo Server stopped.
pause
