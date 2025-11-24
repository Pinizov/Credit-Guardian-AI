"""Seed script to insert sample creditors and violations.

Works with SQLite or Postgres transparently; just ensure `DATABASE_URL` env var points
to your target database before running.
Example (PowerShell):
```
$env:DATABASE_URL="postgresql+psycopg2://cg_user:cg_pass@localhost:5432/credit_guardian"
python database/seed_db.py
```
"""
from datetime import datetime
from database.models import get_session, Creditor, Violation, UnfairClause

SAMPLE_CREDITORS = [
    {"name": "ФинКредит ООД", "type": "non-bank", "bulstat": "123456789", "address": "София",},
    {"name": "БързЗаем ЕАД", "type": "non-bank", "bulstat": "987654321", "address": "Пловдив",},
]

SAMPLE_VIOLATIONS = [
    {"violation_type": "незаконна такса", "law_reference": "чл. 10а ЗПК", "authority": "KZP", "severity": "high", "penalty_amount": 5000},
    {"violation_type": "некоректен ГПР", "law_reference": "чл. 10 ЗПК", "authority": "KZP", "severity": "critical", "penalty_amount": 12000},
]

SAMPLE_CLAUSES = [
    {"clause_type": "Едностранно изменение", "legal_basis": "чл. 143 ЗЗП", "is_confirmed_illegal": True,
     "clause_text": "Кредиторът може едностранно да променя лихвата без уведомление."},
]

def seed():
    session = get_session()
    try:
        creditors = []
        for c in SAMPLE_CREDITORS:
            creditor = Creditor(**c)
            session.add(creditor)
            creditors.append(creditor)
        session.flush()

        for idx, v in enumerate(SAMPLE_VIOLATIONS):
            violation = Violation(creditor_id=creditors[idx % len(creditors)].id,
                                  decision_date=datetime.utcnow(), **v)
            session.add(violation)

        for c in SAMPLE_CLAUSES:
            clause = UnfairClause(creditor_id=creditors[0].id, **c)
            session.add(clause)

        for cred in creditors:
            cred.recalc_risk_score()

        session.commit()
        print("Seed data inserted.")
    except Exception as e:
        session.rollback()
        print("Seed failed:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed()
