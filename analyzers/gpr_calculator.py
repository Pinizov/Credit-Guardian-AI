from typing import List, Dict
import math

class GPRCalculator:
    """
    Калкулатор за Годишен процент на разходите (ГПР)
    Съгласно Приложение 1 към ЗПК
    """
    
    def calculate_gpr(self, 
                      loan_amount: float,
                      total_repayment: float,
                      fees: List[Dict],
                      term_months: int,
                      payment_schedule: List[Dict] = None) -> Dict:
        """
        Изчислява ГПР по формулата от ЗПК
        """
        
        total_fees = sum(fee['amount'] for fee in fees)
        total_cost = total_repayment + total_fees
        
        effective_amount = loan_amount - sum(
            fee['amount'] for fee in fees if fee.get('when') == 'upfront'
        )
        
        simple_gpr = self._calculate_simple_gpr(
            effective_amount,
            total_cost,
            term_months
        )
        
        exact_gpr = self._calculate_exact_gpr(
            effective_amount,
            payment_schedule or self._generate_payment_schedule(
                total_cost, term_months
            )
        )
        
        return {
            'gpr_simple': round(simple_gpr, 2),
            'gpr_exact': round(exact_gpr, 2),
            'total_cost': total_cost,
            'total_fees': total_fees,
            'effective_amount': effective_amount,
            'overpayment': total_cost - loan_amount,
            'overpayment_percent': round((total_cost - loan_amount) / loan_amount * 100, 2),
            'breakdown': self._generate_breakdown(loan_amount, total_cost, fees, term_months)
        }
    
    def _calculate_simple_gpr(self, amount: float, total: float, months: int) -> float:
        """Опростена формула за ГПР"""
        if amount <= 0 or months <= 0:
            return 0.0
        
        gpr = (math.pow(total / amount, 12 / months) - 1) * 100
        return max(0, gpr)
    
    def _calculate_exact_gpr(self, amount: float, schedule: List[Dict]) -> float:
        """
        Точно изчисляване на ГПР по формулата от ЗПК
        Използва метод на Нютон-Рафсън
        """
        
        def npv(rate: float) -> float:
            """Net Present Value при дадена лихва"""
            pv = -amount
            
            for payment in schedule:
                months = payment['month']
                pmt = payment['amount']
                pv += pmt / math.pow(1 + rate/12, months)
            
            return pv
        
        def npv_derivative(rate: float) -> float:
            """Производна на NPV"""
            deriv = 0
            for payment in schedule:
                months = payment['month']
                pmt = payment['amount']
                deriv -= (months * pmt) / (12 * math.pow(1 + rate/12, months + 1))
            
            return deriv
        
        rate = 0.10
        
        for _ in range(100):
            npv_val = npv(rate)
            
            if abs(npv_val) < 0.01:
                break
            
            deriv = npv_derivative(rate)
            if abs(deriv) < 1e-10:
                break
            
            rate = rate - npv_val / deriv
            
            if rate < 0:
                rate = 0.001
        
        return rate * 100
    
    def _generate_payment_schedule(self, total: float, months: int) -> List[Dict]:
        """Генерира график на плащанията (равни месечни вноски)"""
        monthly_payment = total / months
        
        schedule = []
        for month in range(1, months + 1):
            schedule.append({
                'month': month,
                'amount': monthly_payment
            })
        
        return schedule
    
    def _generate_breakdown(self, loan: float, total: float, fees: List[Dict], months: int) -> Dict:
        """Генерира детайлна разбивка на разходите"""
        return {
            'principal': loan,
            'interest': total - loan - sum(f['amount'] for f in fees),
            'fees_breakdown': fees,
            'monthly_payment': total / months,
            'term_months': months
        }
    
    def verify_gpr_declaration(self, 
                               declared_gpr: float,
                               loan_details: Dict) -> Dict:
        """
        Проверява дали деклариран ГПР съответства на реалния
        """
        calculated = self.calculate_gpr(
            loan_amount=loan_details['amount'],
            total_repayment=loan_details['total_repayment'],
            fees=loan_details.get('fees', []),
            term_months=loan_details['term_months'],
            payment_schedule=loan_details.get('schedule')
        )
        
        difference = abs(calculated['gpr_exact'] - declared_gpr)
        is_correct = difference <= 0.1
        
        return {
            'is_correct': is_correct,
            'declared_gpr': declared_gpr,
            'calculated_gpr': calculated['gpr_exact'],
            'difference': round(difference, 3),
            'tolerance': 0.1,
            'verdict': 'Съответства' if is_correct else 'НЕСЪОТВЕТСТВИЕ - Възможно нарушение на чл. 10а ЗПК',
            'details': calculated
        }
    
    def calculate_early_repayment_compensation(self,
                                               remaining_principal: float,
                                               remaining_months: int,
                                               interest_rate: float) -> Dict:
        """
        Изчислява обезщетение при предсрочно погасяване
        Съгласно чл. 29, ал. 3 ЗПК
        """
        
        max_compensation_rate = 0.01 if remaining_months > 12 else 0.005
        
        monthly_rate = interest_rate / 100 / 12
        lost_interest = remaining_principal * monthly_rate * remaining_months
        
        max_compensation_amount = remaining_principal * max_compensation_rate
        compensation = min(lost_interest, max_compensation_amount)
        
        return {
            'remaining_principal': remaining_principal,
            'remaining_months': remaining_months,
            'max_compensation_rate': max_compensation_rate * 100,
            'calculated_compensation': round(compensation, 2),
            'lost_interest': round(lost_interest, 2),
            'legal_limit': round(max_compensation_amount, 2),
            'legal_reference': 'чл. 29, ал. 3 ЗПК'
        }
