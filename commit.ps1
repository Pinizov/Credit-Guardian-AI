# Auto-commit script for Credit Guardian

Write-Host "=== Credit Guardian Auto Commit ===" -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
}

# Stage all changes
Write-Host "`nStaging all changes..." -ForegroundColor Yellow
git add -A

# Create commit with AI-generated message
Write-Host "`nCreating commit..." -ForegroundColor Yellow
$commitMessage = @"
feat: complete credit guardian platform implementation

- Add comprehensive database models with SQLAlchemy ORM (Creditor, Violation, UnfairClause, CourtCase, CreditProduct)
- Implement Alembic migrations for database schema management
- Build GPR (Annual Percentage Rate) calculator with exact and simplified algorithms
- Create clause detector for identifying unfair contract terms using pattern matching
- Develop contract analyzer supporting PDF/DOCX/TXT with automatic extraction
- Build FastAPI REST API with health checks, GPR calculation, and contract analysis endpoints
- Implement React + Vite frontend with dashboard, creditor search, GPR calculator, and contract analyzer
- Add Docker Compose orchestration for PostgreSQL, API, and frontend services
- Configure GitHub Actions CI/CD pipeline with testing, linting, and build stages
- Implement pre-commit hooks for code quality (Black, Flake8, isort, mypy)
- Add comprehensive test suite covering API, database, GPR calculations, and clause detection
- Include S3 storage integration for contract document management
- Create utility modules for text extraction, legal pattern matching, and report generation
- Add environment configuration with .env.example template
- Document database setup, CI/CD workflow, and deployment procedures
"@

git commit -m $commitMessage

# Show result
Write-Host "`n=== Commit Summary ===" -ForegroundColor Green
git log --oneline -1
Write-Host "`n=== Current Status ===" -ForegroundColor Green
git status --short

Write-Host "`nCommit completed successfully!" -ForegroundColor Green
