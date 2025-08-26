#!/bin/bash

echo "🚀 Starting Trading Signals Frontend..."
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error installing dependencies."
        exit 1
    fi
fi

echo "🔥 Starting React development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo

# Start the development server
npm start

