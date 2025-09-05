@echo off
echo Starting Trading Signals API Server...
echo Server will run until manually stopped with Ctrl+C
echo.
echo API will be available at: http://localhost:8002
echo Health check: http://localhost:8002/api/health
echo Dashboard: http://localhost:8002/
echo Live Dashboard: http://localhost:8002/live
echo.
py app/main.py
pause
