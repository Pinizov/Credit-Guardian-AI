# PowerShell script to start Credit Guardian AI with Docker

Write-Host "🚀 Starting Credit Guardian AI with Docker..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker-compose not found. Please install docker-compose." -ForegroundColor Red
    exit 1
}

# Pull latest images
Write-Host "📥 Pulling latest images..." -ForegroundColor Yellow
docker-compose pull

# Start services
Write-Host "🔧 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

# Show logs
Write-Host ""
Write-Host "📝 Recent logs (Press Ctrl+C to exit):" -ForegroundColor Cyan
docker-compose logs --tail=50 -f

