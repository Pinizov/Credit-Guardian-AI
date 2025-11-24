import pytest
from analyzers.gpr_calculator import GPRCalculator

@pytest.fixture
def calculator():
    return GPRCalculator()

def test_gpr_basic_calculation(calculator):
    result = calculator.calculate_gpr(
        loan_amount=1000,
        total_repayment=1200,
        fees=[],
        term_months=12
    )
    assert result['gpr_exact'] > 0
    assert result['total_cost'] == 1200
    assert result['overpayment'] == 200

def test_gpr_with_fees(calculator):
    result = calculator.calculate_gpr(
        loan_amount=5000,
        total_repayment=6000,
        fees=[
            {'name': 'такса обработка', 'amount': 200, 'when': 'upfront'},
            {'name': 'месечна такса', 'amount': 10, 'when': 'monthly'}
        ],
        term_months=24
    )
    assert result['total_fees'] == 210
    assert result['effective_amount'] == 4800  # 5000 - 200 upfront
    assert result['gpr_exact'] > 0

def test_gpr_verification_correct(calculator):
    result = calculator.verify_gpr_declaration(
        25.0,
        {
            'amount': 2000,
            'total_repayment': 2500,
            'fees': [],
            'term_months': 12
        }
    )
    assert 'is_correct' in result
    assert 'calculated_gpr' in result
    assert 'difference' in result

def test_gpr_verification_mismatch(calculator):
    result = calculator.verify_gpr_declaration(
        10.0,  # Unrealistically low
        {
            'amount': 2000,
            'total_repayment': 3000,
            'fees': [],
            'term_months': 12
        }
    )
    assert result['is_correct'] == False
    assert result['difference'] > 0.1

def test_early_repayment_compensation(calculator):
    result = calculator.calculate_early_repayment_compensation(
        remaining_principal=10000,
        remaining_months=18,
        interest_rate=15.0
    )
    assert result['max_compensation_rate'] == 1.0  # >12 months
    assert result['calculated_compensation'] > 0
    assert result['calculated_compensation'] <= result['legal_limit']

def test_early_repayment_under_12_months(calculator):
    result = calculator.calculate_early_repayment_compensation(
        remaining_principal=10000,
        remaining_months=6,
        interest_rate=15.0
    )
    assert result['max_compensation_rate'] == 0.5  # <=12 months
