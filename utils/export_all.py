"""Export all database tables to JSON."""
import json
from datetime import datetime
from database.models import get_session, Creditor, Violation, CourtCase, UnfairClause, CreditProduct

EXPORT_PATH = "backup_export.json"

def export_all(path: str = EXPORT_PATH):
    session = get_session()
    data = {}
    try:
        data["creditors"] = [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "bulstat": c.bulstat,
                "license_number": c.license_number,
                "violations_count": c.violations_count,
                "risk_score": c.risk_score,
                "is_blacklisted": c.is_blacklisted,
                "created_at": c.created_at.isoformat(),
            }
            for c in session.query(Creditor).all()
        ]
        data["violations"] = [
            {
                "id": v.id,
                "creditor_id": v.creditor_id,
                "violation_type": v.violation_type,
                "law_reference": v.law_reference,
                "authority": v.authority,
                "penalty_amount": v.penalty_amount,
                "decision_date": v.decision_date.isoformat() if v.decision_date else None,
                "severity": v.severity,
            }
            for v in session.query(Violation).all()
        ]
        data["unfair_clauses"] = [
            {
                "id": uc.id,
                "creditor_id": uc.creditor_id,
                "clause_type": uc.clause_type,
                "legal_basis": uc.legal_basis,
                "is_confirmed_illegal": uc.is_confirmed_illegal,
            }
            for uc in session.query(UnfairClause).all()
        ]
        data["court_cases"] = [
            {
                "id": cc.id,
                "creditor_id": cc.creditor_id,
                "case_number": cc.case_number,
                "court_name": cc.court_name,
                "decision_date": cc.decision_date.isoformat() if cc.decision_date else None,
                "is_final": cc.is_final,
            }
            for cc in session.query(CourtCase).all()
        ]
        data["credit_products"] = [
            {
                "id": p.id,
                "creditor_id": p.creditor_id,
                "product_name": p.product_name,
                "interest_rate": p.interest_rate,
                "gpr": p.gpr,
                "gpr_calculated": p.gpr_calculated,
                "gpr_mismatch": p.gpr_mismatch,
                "term_months": p.term_months,
            }
            for p in session.query(CreditProduct).all()
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"generated_at": datetime.utcnow().isoformat(), **data}, f, ensure_ascii=False, indent=2)
        print(f"Export written to {path}")
    finally:
        session.close()

if __name__ == "__main__":
    export_all()
