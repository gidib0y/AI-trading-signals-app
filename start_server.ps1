Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    TRADING SIGNALS SERVER STARTUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = py --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not accessible" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow
try {
    py -m pip install -r requirements.txt
    Write-Host "✅ Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error installing packages: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8003" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

try {
    py server.py
} catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
