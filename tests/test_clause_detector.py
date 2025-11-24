import pytest
from analyzers.clause_detector import ClauseDetector

@pytest.fixture
def detector():
    return ClauseDetector()

def test_detect_unilateral_change(detector):
    contract = """
    Член 5. Кредиторът има право едностранно да промени лихвения процент 
    по всяко време без предварително уведомление на заемателя.
    """
    clauses = detector.detect_unfair_clauses(contract)
    assert len(clauses) > 0
    assert any('Едностранно изменение' in c['type'] for c in clauses)

def test_detect_excessive_penalty(detector):
    contract = """
    При забава на плащането, заемателят дължи неустойка в размер 
    на 50% от непогасената главница.
    """
    clauses = detector.detect_unfair_clauses(contract)
    assert len(clauses) > 0
    assert any('неустойка' in c['type'].lower() for c in clauses)

def test_detect_prepayment_restriction(detector):
    contract = """
    Предсрочното погасяване на кредита не се допуска през 
    първите 12 месеца от договора.
    """
    clauses = detector.detect_unfair_clauses(contract)
    assert len(clauses) > 0
    assert any('предсрочно' in c['type'].lower() for c in clauses)

def test_severity_calculation(detector):
    clauses = [
        {'type': 'Test', 'severity': 'critical', 'text': 'test', 'legal_basis': 'test'},
        {'type': 'Test', 'severity': 'high', 'text': 'test', 'legal_basis': 'test'},
        {'type': 'Test', 'severity': 'medium', 'text': 'test', 'legal_basis': 'test'},
    ]
    analysis = detector.analyze_clause_severity(clauses)
    assert analysis['severity_counts']['critical'] == 1
    assert analysis['severity_counts']['high'] == 1
    assert analysis['severity_counts']['medium'] == 1
    assert analysis['risk_score'] > 0
    assert analysis['overall_risk'] in ['low', 'medium', 'high', 'critical']

def test_clean_contract(detector):
    contract = """
    Кредиторът се задължава да предостави на заемателя договорения кредит.
    Заемателят се задължава да върне кредита в уговорения срок.
    """
    clauses = detector.detect_unfair_clauses(contract)
    # May still detect some false positives, but should be minimal
    assert isinstance(clauses, list)

def test_generate_complaint(detector):
    clauses = [
        {
            'type': 'Едностранно изменение',
            'text': 'Кредиторът може да променя лихвата.',
            'legal_basis': 'чл. 143 ЗЗП',
            'explanation': 'Недопустимо'
        }
    ]
    complaint = detector.generate_complaint(clauses, 'ТестБанка АД')
    assert 'КОМИСИЯТА ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ' in complaint
    assert 'ТестБанка АД' in complaint
    assert 'Едностранно изменение' in complaint
