import os
import re
from typing import Dict, List, Any

class ContractAnalyzer:
    """Анализ на кредитни договори (PDF/DOCX/TXT)"""
    
    def __init__(self):
        from analyzers.gpr_calculator import GPRCalculator
        from analyzers.clause_detector import ClauseDetector
        
        self.gpr_calc = GPRCalculator()
        self.clause_detector = ClauseDetector()
    
    def analyze_file(self, path: str) -> Dict[str, Any]:
        """Analyze contract file and return results"""
        raw_text = self._read_file(path)
        text = self._normalize_text(raw_text)
        
        creditor = self._extract_creditor(text)
        amount = self._extract_loan_amount(text)
        declared_gpr = self._extract_declared_gpr(text)
        total_repayment = self._estimate_total_repayment(text, amount)
        term_months = self._extract_term(text)
        fees = self._extract_fees(text)
        illegal_fees = self._find_illegal_fees(fees)
        
        gpr_verification = None
        if declared_gpr and amount and total_repayment and term_months:
            gpr_verification = self.gpr_calc.verify_gpr_declaration(
                declared_gpr,
                {
                    'amount': amount,
                    'total_repayment': total_repayment,
                    'fees': fees,
                    'term_months': term_months
                }
            )
        
        unfair_clauses = self.clause_detector.detect_unfair_clauses(text)
        clause_risk = self.clause_detector.analyze_clause_severity(unfair_clauses)
        
        risk_level = self._aggregate_risk(gpr_verification, clause_risk, illegal_fees)
        
        return {
            'creditor': creditor,
            'amount': amount or 0.0,
            'declared_gpr': declared_gpr or 0.0,
            'estimated_total_repayment': total_repayment,
            'term_months': term_months,
            'fees': fees,
            'illegal_fees': illegal_fees,
            'gpr_verification': gpr_verification,
            'unfair_clauses': unfair_clauses,
            'clause_risk': clause_risk,
            'risk_level': risk_level,
            'source_path': path
        }
    
    def _read_file(self, path: str) -> str:
        """Read file content"""
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text"""
        return re.sub(r'\s+', ' ', text).strip()
    
    def _extract_creditor(self, text: str) -> str:
        """Extract creditor name"""
        match = re.search(r'(?:Кредитор|Банка|Фирма)\s*[:\-]\s*([A-ZА-Я0-9"„][^,\n]+)', text)
        if match:
            return match.group(1).strip()
        
        comp = re.search(r'([A-ZА-Я][A-Za-zА-Яа-я0-9\s]+(?:ООД|ЕООД|АД|ЕАД))', text)
        return comp.group(1).strip() if comp else "Неразпознат"
    
    def _extract_loan_amount(self, text: str) -> float:
        """Extract loan amount"""
        from utils.helpers import extract_amounts
        amounts = extract_amounts(text)
        if not amounts:
            return 0.0
        candidates = [a for a in amounts if a <= 200000]
        return max(candidates) if candidates else max(amounts)
    
    def _extract_declared_gpr(self, text: str) -> float:
        """Extract declared GPR"""
        from utils.helpers import extract_percentages
        percents = extract_percentages(text)
        gpr_match = re.search(r'ГПР[^0-9]{0,20}(\d{1,3}[.,]\d{1,2})\s*%', text)
        if gpr_match:
            return float(gpr_match.group(1).replace(',', '.'))
        if percents:
            plausible = [p for p in percents if p < 200]
            return max(plausible) if plausible else max(percents)
        return 0.0
    
    def _extract_term(self, text: str) -> int:
        """Extract loan term in months"""
        m = re.search(r'срок.*?(\d{1,3})\s*мес', text.lower())
        if m:
            return int(m.group(1))
        y = re.search(r'срок.*?(\d{1,2})\s*год', text.lower())
        if y:
            return int(y.group(1)) * 12
        return 0
    
    def _estimate_total_repayment(self, text: str, amount: float) -> float:
        """Estimate total repayment"""
        m = re.search(r'(общо.*?дължима|общ размер).*?(\d{3,9}[.,]\d{2})', text.lower())
        if m:
            return float(m.group(2).replace(',', '.'))
        return amount * 1.25 if amount else 0.0
    
    def _extract_fees(self, text: str) -> List[Dict]:
        """Extract fees"""
        fees = []
        fee_patterns = [
            r'(такса [A-Za-zА-Яа-я\s]+)\s*[:\-]?\s*(\d{1,6}[.,]\d{2})\s*лв',
            r'(комисиона [A-Za-zА-Яа-я\s]+)\s*[:\-]?\s*(\d{1,6}[.,]\d{2})\s*лв'
        ]
        for pattern in fee_patterns:
            for m in re.finditer(pattern, text.lower()):
                name = m.group(1).strip()
                amt = float(m.group(2).replace(',', '.'))
                fees.append({'name': name, 'amount': amt, 'when': 'unknown'})
        return fees
    
    def _find_illegal_fees(self, fees: List[Dict]) -> List[Dict]:
        """Find illegal fees"""
        from utils.legal_texts import ILLEGAL_FEES_KEYWORDS
        illegal = []
        for f in fees:
            if any(k in f['name'] for k in ILLEGAL_FEES_KEYWORDS):
                illegal.append({
                    'name': f['name'],
                    'amount': f['amount'],
                    'legal_basis': 'ЗПК / практика КЗП (недопустима такса)'
                })
        return illegal
    
    def _aggregate_risk(self, gpr_ver: Dict, clause_risk: Dict, illegal_fees: List[Dict]) -> str:
        """Aggregate risk level"""
        score = 0
        if gpr_ver and not gpr_ver['is_correct']:
            score += 5
        if illegal_fees:
            score += 5
        if clause_risk:
            mapping = {'low': 1, 'medium': 3, 'high': 6, 'critical': 10}
            score += mapping.get(clause_risk['overall_risk'], 0)
        if score >= 15:
            return 'critical'
        if score >= 10:
            return 'high'
        if score >= 5:
            return 'medium'
        return 'low'
