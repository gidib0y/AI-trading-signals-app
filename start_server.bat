@echo off
echo ========================================
echo    TRADING SIGNALS SERVER STARTUP
echo ========================================
echo.
echo Checking Python installation...

py --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Starting server...
py server.py

echo.
echo Server stopped.
pause
