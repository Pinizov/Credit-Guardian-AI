# Credit Guardian API Server Startup Script
Write-Host "Starting Credit Guardian AI API..." -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Start the server
Write-Host "Starting server on http://localhost:8080" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
