#!/bin/bash
# Script to start frontend with Live Server + Docker backend

echo "🚀 Starting Credit Guardian Frontend with Live Server"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Docker backend services
echo "📦 Starting Docker backend services..."
docker-compose up -d db ollama api

# Wait for services to start
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check API health
echo "🔍 Checking API health..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API not ready yet, but continuing..."
fi

echo ""
echo "📋 Next Steps:"
echo "1. Open VS Code"
echo "2. Open file: frontend/index.html"
echo "3. Right-click -> 'Open with Live Server' OR click 'Go Live' in status bar"
echo "4. Frontend will open on http://localhost:5500"
echo "5. Frontend will automatically connect to Docker API on http://localhost:8080"
echo ""
echo "💡 Tip: Check browser console (F12) to see detected API URL"
echo ""
echo "📊 Docker Services Status:"
docker-compose ps

