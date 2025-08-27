#!/bin/bash

echo "🚀 Deploying AI Trading Signal Generator..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start the application
echo "📦 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for the application to be ready
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your trading dashboard at: http://localhost:8000"
    echo "📚 API documentation at: http://localhost:8000/docs"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop app: docker-compose down"
    echo "  Restart: docker-compose restart"
else
    echo "❌ Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi
