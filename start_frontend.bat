@echo off
echo 🚀 Starting Trading Signals Frontend...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Error installing dependencies.
        pause
        exit /b 1
    )
)

echo 🔥 Starting React development server...
echo 🌐 Frontend will be available at: http://localhost:3000
echo.

REM Start the development server
npm start

pause

