from database.models import Session, Creditor, Violation, CourtCase, UnfairClause, CreditProduct
from datetime import datetime

class ReportGenerator:
    """Generate reports for creditors and system statistics."""
    
    def generate_creditor_report(self, creditor_name: str) -> str:
        """Generate detailed report for a specific creditor."""
        s = Session()
        c = s.query(Creditor).filter(Creditor.name.ilike(f'%{creditor_name}%')).first()
        if not c:
            s.close()
            return f"Няма данни за кредитор: {creditor_name}"
        
        violations = s.query(Violation).filter_by(creditor_id=c.id).all()
        clauses = s.query(UnfairClause).filter_by(creditor_id=c.id).all()
        cases = s.query(CourtCase).filter_by(creditor_id=c.id).all()
        
        report = []
        report.append(f"ДОКЛАД ЗА КРЕДИТОР: {c.name}")
        report.append(f"Дата: {datetime.now():%d.%m.%Y}")
        report.append(f"Тип: {c.type}")
        report.append(f"Нарушения: {c.violations_count}")
        report.append(f"Риск скор: {c.risk_score:.1f}")
        
        if c.is_blacklisted:
            report.append("СТАТУС: ЧЕРЕН СПИСЪК")
        
        report.append("\n=== НАРУШЕНИЯ ===")
        for v in violations:
            report.append(f"- {v.violation_type} ({v.severity}) | {v.decision_date} | {v.authority}")
        
        report.append("\n=== НЕРАВНОПРАВНИ КЛАУЗИ ===")
        for cl in clauses:
            report.append(f"- {cl.clause_type} | {cl.legal_basis} | {'потвърдена' if cl.is_confirmed_illegal else 'непотвърдена'}")
        
        report.append("\n=== СЪДЕБНИ ДЕЛА ===")
        for case in cases[:20]:
            report.append(f"- {case.case_number} | {case.court_name} | {case.decision_date} | финално:{case.is_final}")
        
        s.close()
        return "\n".join(report)
    
    def generate_summary_report(self) -> str:
        """Generate summary statistics report."""
        s = Session()
        creditors = s.query(Creditor).count()
        violations = s.query(Violation).count()
        cases = s.query(CourtCase).count()
        clauses = s.query(UnfairClause).count()
        critical = s.query(Violation).filter_by(severity='critical').count()
        
        report = [
            "ОБЩ СВОДЕН ДОКЛАД",
            f"Дата: {datetime.now():%d.%m.%Y}",
            f"Кредитори: {creditors}",
            f"Нарушения: {violations} (критични: {critical})",
            f"Съдебни дела: {cases}",
            f"Неравноправни клаузи: {clauses}"
        ]
        
        s.close()
        return "\n".join(report)
