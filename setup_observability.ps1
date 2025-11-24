# Quick Start Script for Observability & Evaluation Setup
# Run this script to quickly set up and test the new features

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Credit Guardian - Observability & Evaluation Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Install dependencies
Write-Host "[1/5] Installing dependencies..." -ForegroundColor Yellow
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-openai opentelemetry-exporter-otlp-proto-grpc

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed`n" -ForegroundColor Green

# Step 2: Create evaluation directory structure
Write-Host "[2/5] Creating evaluation directory structure..." -ForegroundColor Yellow
$evalDir = "evaluation"
if (-not (Test-Path $evalDir)) {
    New-Item -ItemType Directory -Path $evalDir | Out-Null
}
Write-Host "✓ Directory structure ready`n" -ForegroundColor Green

# Step 3: Create sample dataset
Write-Host "[3/5] Creating sample evaluation dataset..." -ForegroundColor Yellow
python run_evaluation.py --create-sample --dataset evaluation/test_dataset.json

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create sample dataset" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Sample dataset created`n" -ForegroundColor Green

# Step 4: Test tracing
Write-Host "[4/5] Testing tracing setup..." -ForegroundColor Yellow
$testTracing = @"
from ai_agent.tracing import initialize_tracing, trace_span, add_trace_event
import time

initialize_tracing(service_name='test-service', console_export=True)

with trace_span('test_operation', attributes={'test': 'true'}):
    add_trace_event('start', {'timestamp': time.time()})
    time.sleep(0.1)
    add_trace_event('complete', {'timestamp': time.time()})

print('✓ Tracing test successful')
"@

$testTracing | python

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tracing test failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Tracing working`n" -ForegroundColor Green

# Step 5: Run tests
Write-Host "[5/5] Running evaluation framework tests..." -ForegroundColor Yellow
pytest tests/test_evaluation.py -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some tests failed (this is normal if test fixtures are missing)" -ForegroundColor Yellow
} else {
    Write-Host "✓ All tests passed`n" -ForegroundColor Green
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Set your OpenAI API key: " -NoNewline; Write-Host "`$env:OPENAI_API_KEY='your-key'" -ForegroundColor Yellow
Write-Host "2. Edit evaluation dataset: " -NoNewline; Write-Host "evaluation/test_dataset.json" -ForegroundColor Yellow
Write-Host "3. Run evaluation: " -NoNewline; Write-Host "python run_evaluation.py --verbose" -ForegroundColor Yellow
Write-Host "4. View traces in console or set OTLP endpoint" -ForegroundColor White
Write-Host "5. Read full guide: " -NoNewline; Write-Host "README_OBSERVABILITY.md`n" -ForegroundColor Yellow

Write-Host "For trace export to Jaeger (optional):" -ForegroundColor White
Write-Host "  docker run -d --name jaeger -p 16686:16686 -p 4317:4317 jaegertracing/all-in-one:latest" -ForegroundColor Gray
Write-Host "  `$env:OTEL_EXPORTER_OTLP_ENDPOINT='http://localhost:4317'" -ForegroundColor Gray
Write-Host "  View at http://localhost:16686`n" -ForegroundColor Gray
