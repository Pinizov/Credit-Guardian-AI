# CI/CD, Testing & Code Quality

## Running Tests

### Local (PowerShell)
```powershell
venv\Scripts\activate
pip install pytest pytest-cov
pytest
pytest --cov --cov-report=html
```

View coverage: `htmlcov/index.html`

### Docker
```powershell
docker compose run --rm api pytest
```

## Code Quality

### Pre-commit Hooks
```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Auto-runs on every commit:
- trailing whitespace removal
- YAML/JSON validation
- Black formatting
- Flake8 linting
- isort import sorting

### Manual Linting
```powershell
black .
flake8 .
isort .
```

## Health Checks

### Endpoints
- `GET /health` - Basic health (200 = OK)
- `GET /readiness` - DB connection check (200 = ready, 503 = not ready)

### Docker Health Monitoring
```powershell
docker compose ps
docker inspect cg_api --format='{{.State.Health.Status}}'
```

Status: `healthy` | `unhealthy` | `starting`

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Test Job**
   - Python 3.11 + Postgres 15
   - Install dependencies
   - Lint (flake8, black)
   - Run pytest with coverage
   - Upload to Codecov

2. **Build Backend**
   - Docker build
   - Test container health

3. **Build Frontend**
   - Node 20 build
   - Docker image

4. **Deploy** (main branch only)
   - Configure your deployment target

### Triggering CI
```powershell
git add .
git commit -m "feat: new feature"
git push origin main
```

CI runs on:
- Push to `main` or `develop`
- Pull requests to `main`

## Monitoring & Alerts

### Docker Compose Health
```powershell
docker compose ps
```

Unhealthy containers restart automatically (if configured).

### Logs
```powershell
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db
```

### Metrics (optional future enhancement)
- Prometheus + Grafana
- Sentry error tracking
- CloudWatch (AWS)

## Deployment Checklist

- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No linting errors
- [ ] Docker images build successfully
- [ ] Health checks return 200
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] S3 credentials (if used)
- [ ] CORS origins set correctly
- [ ] SSL/TLS certificates (production)

## Troubleshooting

### Test failures
```powershell
pytest -v --tb=short
pytest tests/test_api.py::test_specific -vv
```

### Health check fails
```powershell
curl http://localhost:8000/health
curl http://localhost:8000/readiness
docker compose logs api
```

### Database connection issues
```powershell
docker compose ps db
docker compose exec db psql -U cg_user -d credit_guardian -c "SELECT 1;"
```
