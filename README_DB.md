# Database Layer (Credit Guardian)

## Models
- `Creditor` (name, type, bulstat, risk metrics)
- `Violation` (authority, law_reference, severity, penalty)
- `UnfairClause` (clause_text, legal_basis, confirmed flag)
- `CourtCase` (case_number unique, court_name, final flag)
- `CreditProduct` (interest_rate, gpr, fees, mismatch)

All tables include timestamps; relationships enforce cascading deletes where appropriate.

## Setup
```powershell
python database/init_db.py  # creates tables
python database/seed_db.py  # inserts sample data
python utils/export_all.py  # exports JSON snapshot
```

Override database URL:
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:pass@localhost/credit_guardian"
python database/init_db.py
```

## Risk Score
`Creditor.recalc_risk_score()` aggregates violation severities and confirmed unfair clauses.

## Next Steps
- Integrate Alembic for migrations
- Add indexing for performance on large datasets
- Implement pagination APIs

## Postgres + Alembic

### Run Postgres (Docker Compose)
```powershell
docker compose up -d db
```

### Environment Variables
Use `.env.example` and set:
```
POSTGRES_DB=credit_guardian
POSTGRES_USER=cg_user
POSTGRES_PASSWORD=cg_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://cg_user:cg_pass@localhost:5432/credit_guardian
```

### Create Migration (if schema changes)
```powershell
alembic revision --autogenerate -m "schema update"
alembic upgrade head
```

### Apply Existing Migrations
```powershell
alembic upgrade head
```

### Downgrade (rollback last migration)
```powershell
alembic downgrade -1
```

### Regenerating Initial Migration
If you alter models drastically, delete old files in `alembic/versions/` (except keep backups), then:
```powershell
alembic revision --autogenerate -m "recreate base"
alembic upgrade head
```

### Seeding (works for SQLite or Postgres)
```powershell
python database/seed_db.py
```

### Export Snapshot
```powershell
python utils/export_all.py
```
