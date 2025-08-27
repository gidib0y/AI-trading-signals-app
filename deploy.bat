@echo off
echo 🚀 Deploying AI Trading Signal Generator...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Build and start the application
echo 📦 Building Docker image...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

REM Wait for the application to be ready
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running
echo 🔍 Checking application status...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000' -UseBasicParsing | Out-Null; Write-Host '✅ Application is running successfully!' } catch { Write-Host '❌ Application failed to start. Check logs with: docker-compose logs' }"

echo.
echo 🌐 Access your trading dashboard at: http://localhost:8000
echo 📚 API documentation at: http://localhost:8000/docs
echo.
echo 📋 Useful commands:
echo   View logs: docker-compose logs -f
echo   Stop app: docker-compose down
echo   Restart: docker-compose restart
echo.
pause
