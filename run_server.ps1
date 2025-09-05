Write-Host "Starting Trading Signals API Server..." -ForegroundColor Green
Write-Host "Server will run until manually stopped with Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "API will be available at: http://localhost:8002" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:8002/api/health" -ForegroundColor Cyan
Write-Host "Dashboard: http://localhost:8002/" -ForegroundColor Cyan
Write-Host "Live Dashboard: http://localhost:8002/live" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

try {
    py app/main.py
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
