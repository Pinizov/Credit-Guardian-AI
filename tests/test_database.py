import pytest
from database.models import Base, Creditor, Violation, engine, get_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope='function')
def test_db():
    """Create test database"""
    test_engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()

def test_creditor_creation(test_db):
    creditor = Creditor(
        name="Тест Банка",
        type="bank",
        bulstat="123456789"
    )
    test_db.add(creditor)
    test_db.commit()
    
    result = test_db.query(Creditor).filter_by(name="Тест Банка").first()
    assert result is not None
    assert result.bulstat == "123456789"

def test_violation_relationship(test_db):
    creditor = Creditor(name="Тест ООД", type="non-bank")
    test_db.add(creditor)
    test_db.flush()
    
    violation = Violation(
        creditor_id=creditor.id,
        violation_type="незаконна такса",
        severity="high",
        penalty_amount=5000
    )
    test_db.add(violation)
    test_db.commit()
    
    assert len(creditor.violations) == 1
    assert creditor.violations[0].violation_type == "незаконна такса"

def test_risk_score_calculation(test_db):
    creditor = Creditor(name="Рискова фирма", type="non-bank")
    test_db.add(creditor)
    test_db.flush()
    
    v1 = Violation(creditor_id=creditor.id, severity="critical")
    v2 = Violation(creditor_id=creditor.id, severity="high")
    test_db.add_all([v1, v2])
    test_db.flush()
    
    creditor.recalc_risk_score()
    test_db.commit()
    
    assert creditor.risk_score > 0
    assert creditor.violations_count == 2
