# Credit Guardian Docker Deployment Script
# =========================================

param(
    [switch]$GPU,
    [switch]$Build,
    [switch]$Down,
    [switch]$Logs,
    [switch]$Status,
    [string]$Service
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Text)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Text)
    Write-Host "➡️  $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

# Check Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Error "Docker is not running! Please start Docker Desktop first."
    exit 1
}

Write-Header "Credit Guardian Docker Deployment"

# Determine compose file
if ($GPU) {
    $ComposeFile = "docker-compose.yml"
    Write-Host "Mode: GPU-accelerated" -ForegroundColor Magenta
} else {
    $ComposeFile = "docker-compose.cpu.yml"
    Write-Host "Mode: CPU-only" -ForegroundColor Magenta
}

# Handle commands
if ($Down) {
    Write-Step "Stopping all containers..."
    docker-compose -f $ComposeFile down
    Write-Success "All containers stopped"
    exit 0
}

if ($Logs) {
    if ($Service) {
        docker-compose -f $ComposeFile logs -f $Service
    } else {
        docker-compose -f $ComposeFile logs -f
    }
    exit 0
}

if ($Status) {
    Write-Header "Container Status"
    docker-compose -f $ComposeFile ps
    
    Write-Host "`n📊 Resource Usage:" -ForegroundColor Yellow
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    exit 0
}

# Main deployment
Write-Step "Using compose file: $ComposeFile"

if ($Build) {
    Write-Step "Building images..."
    docker-compose -f $ComposeFile build --no-cache
}

Write-Step "Starting services..."
docker-compose -f $ComposeFile up -d

Write-Step "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check service health
$services = @("cg_postgres", "cg_ollama", "cg_api", "cg_frontend")
foreach ($svc in $services) {
    $status = docker inspect --format='{{.State.Status}}' $svc 2>$null
    if ($status -eq "running") {
        Write-Success "$svc is running"
    } else {
        Write-Error "$svc is not running (status: $status)"
    }
}

# Wait for Ollama model to be pulled
Write-Step "Checking Ollama model (this may take a few minutes on first run)..."
$attempts = 0
$maxAttempts = 30
while ($attempts -lt $maxAttempts) {
    $models = docker exec cg_ollama ollama list 2>$null
    if ($models -match "llama3.2") {
        Write-Success "Ollama model llama3.2 is ready!"
        break
    }
    $attempts++
    Write-Host "  Waiting for model... ($attempts/$maxAttempts)" -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

if ($attempts -eq $maxAttempts) {
    Write-Host "⚠️  Model still pulling. Check with: docker logs cg_ollama_pull" -ForegroundColor Yellow
}

Write-Header "Deployment Complete!"

Write-Host @"
🌐 Access Points:
   Frontend:  http://localhost:3000
   API:       http://localhost:8080
   API Docs:  http://localhost:8080/docs
   Ollama:    http://localhost:11434

📋 Useful Commands:
   View logs:     .\deploy.ps1 -Logs
   View API logs: .\deploy.ps1 -Logs -Service api
   Status:        .\deploy.ps1 -Status
   Stop all:      .\deploy.ps1 -Down
   Rebuild:       .\deploy.ps1 -Build

🧪 Test Ollama:
   docker exec cg_ollama ollama list
   docker exec cg_ollama ollama run llama3.2 "Здравей!"

"@ -ForegroundColor Cyan

