# PowerShell script to start frontend with Live Server + Docker backend

Write-Host "🚀 Starting Credit Guardian Frontend with Live Server" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Start Docker backend services
Write-Host "📦 Starting Docker backend services..." -ForegroundColor Yellow
docker-compose up -d db ollama api

# Wait for services to start
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check API health
Write-Host "🔍 Checking API health..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is healthy!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  API not ready yet, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open VS Code" -ForegroundColor White
Write-Host "2. Open file: frontend/index.html" -ForegroundColor White
Write-Host "3. Right-click -> 'Open with Live Server' OR click 'Go Live' in status bar" -ForegroundColor White
Write-Host "4. Frontend will open on http://localhost:5500" -ForegroundColor White
Write-Host "5. Frontend will automatically connect to Docker API on http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Check browser console (F12) to see detected API URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Docker Services Status:" -ForegroundColor Cyan
docker-compose ps

