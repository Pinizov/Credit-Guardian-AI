from datetime import datetime
from typing import Dict, Any, List
from .llm_client import CreditAnalysisAgent
from .pdf_processor import PDFProcessor
from .tracing import trace


class AgentExecutor:
    def __init__(self):
        self.agent = CreditAnalysisAgent()

    @staticmethod
    def calculate_real_apr(principal: float, total_costs: float, days: int) -> float:
        """
        Calculate real Annual Percentage Rate (APR)
        Formula: (total_costs / principal) / days * 365 * 100
        """
        if principal == 0 or days == 0:
            return 0.0
        
        daily_rate = (total_costs / principal) / days
        annual_rate = daily_rate * 365 * 100
        
        return round(annual_rate, 2)
    
    @staticmethod
    def check_legal_violations(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check contract for Bulgarian law violations
        Returns list of violation objects
        """
        violations = []
        principal = analysis.get("principal", 0)
        stated_apr = analysis.get("stated_apr", 0)
        calculated_apr = analysis.get("calculated_real_apr", 0)
        
        # 1. Check for illegal fees (чл. 10а ЗПК)
        illegal_fee_keywords = [
            "бързо разглеждане",
            "fast review",
            "управление на кредита",
            "credit management",
            "усвояване",
            "disbursement",
            "комисион за разглеждане",
            "processing fee",
            "такса за обработка",
        ]
        
        for fee in analysis.get("fees", []):
            fee_type = fee.get("type", "").lower()
            if any(keyword in fee_type for keyword in illegal_fee_keywords):
                violations.append({
                    "type": "illegal_fee",
                    "description": f"Незаконна такса: '{fee['type']}' в размер {fee['amount']} лв. Таксата е забранена и не може да се включва в цената на кредита.",
                    "severity": "critical",
                    "legal_basis": "чл. 10а, ал. 2 ЗПК",
                    "financial_impact": fee.get("amount", 0)
                })
        
        # 2. Check if APR exceeds 50% maximum (чл. 19, ал. 4 ЗПК)
        if calculated_apr > 50:
            excess = calculated_apr - 50
            violations.append({
                "type": "apr_exceeded",
                "description": f"Реалният ГПР от {calculated_apr:.2f}% превишава законовия максимум от 50%. Превишението е {excess:.2f} процентни пункта.",
                "severity": "critical",
                "legal_basis": "чл. 19, ал. 4 ЗПК",
                "financial_impact": round((excess / 100) * principal, 2)
            })
        
        # 3. Check for incorrect APR disclosure (чл. 11, ал. 1, т. 10 ЗПК)
        if stated_apr and calculated_apr and abs(calculated_apr - stated_apr) > 0.5:
            violations.append({
                "type": "incorrect_apr_disclosure",
                "description": f"Посоченият в договора ГПР от {stated_apr:.2f}% не съответства на реалния ГПР от {calculated_apr:.2f}%. Разликата е {abs(calculated_apr - stated_apr):.2f} процентни пункта.",
                "severity": "high",
                "legal_basis": "чл. 11, ал. 1, т. 10 ЗПК",
                "financial_impact": round(abs(calculated_apr - stated_apr) / 100 * principal, 2)
            })
        
        # 4. Check for missing mandatory information
        required_fields = ["principal", "stated_apr", "term_months", "creditor", "contract_date"]
        missing = [field for field in required_fields if not analysis.get(field)]
        
        if missing:
            violations.append({
                "type": "missing_information",
                "description": f"Липсва задължителна информация в договора: {', '.join(missing)}. Договорът не отговаря на минималните изисквания за прозрачност.",
                "severity": "medium",
                "legal_basis": "чл. 11, ал. 1 ЗПК",
                "financial_impact": 0
            })
        
        return violations
    
    @staticmethod
    def enhance_analysis_with_calculations(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance AI analysis with calculated metrics
        """
        principal = analysis.get("principal", 0)
        total_actual_cost = analysis.get("total_actual_cost", 0)
        term_months = analysis.get("term_months", 30)  # default 30 days if not specified
        
        # Calculate real APR if not already calculated by AI
        if not analysis.get("calculated_real_apr") and principal > 0:
            days = term_months * 30  # rough approximation
            real_apr = AgentExecutor.calculate_real_apr(principal, total_actual_cost - principal, days)
            analysis["calculated_real_apr"] = real_apr
        
        # Calculate total illegal fees
        illegal_fees_total = sum(
            fee.get("amount", 0) 
            for fee in analysis.get("fees", []) 
            if fee.get("is_illegal", False)
        )
        analysis["total_illegal_fees"] = round(illegal_fees_total, 2)
        
        # Add violations check
        if not analysis.get("violations"):
            analysis["violations"] = []
        
        additional_violations = AgentExecutor.check_legal_violations(analysis)
        analysis["violations"].extend(additional_violations)
        
        return analysis

    @trace("agent_process")
    def process(self, pdf_path: str, user: Dict[str, str]) -> Dict[str, Any]:
        """
        Complete contract analysis workflow:
        1. Extract text from PDF
        2. Extract structured data (numbers, dates, creditor info)
        3. AI analysis
        4. Calculate metrics
        5. Check violations
        6. Generate complaint
        """
        # Step 1: Extract text
        text = PDFProcessor.extract_text(pdf_path)
        
        if len(text) < 100:
            return {
                "status": "error",
                "message": "Не успяхме да извлечем достатъчно текст от файла. Моля, уверете се че файлът е валиден PDF.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Step 2: Extract structured data
        financial_data = PDFProcessor.extract_numbers(text)
        dates = PDFProcessor.extract_dates(text)
        creditor_info = PDFProcessor.extract_creditor_info(text)
        
        # Step 3: AI analysis
        analysis = self.agent.analyze_contract(text)
        
        # Merge extracted data with AI analysis
        analysis.update(financial_data)
        analysis.update(dates)
        analysis.update(creditor_info)
        
        # Step 4: Enhance with calculations
        analysis = self.enhance_analysis_with_calculations(analysis)
        
        # Step 5: Generate complaint
        complaint = self.agent.generate_complaint(
            analysis, 
            user.get("name", "Потребител"), 
            user.get("address", "")
        )
        
        # Step 6: Prepare final result
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "complaint": complaint,
            "text_excerpt": text[:1000],
            "financial_summary": {
                "principal": analysis.get("principal", 0),
                "stated_apr": analysis.get("stated_apr", 0),
                "calculated_real_apr": analysis.get("calculated_real_apr", 0),
                "total_illegal_fees": analysis.get("total_illegal_fees", 0),
                "violations_count": len(analysis.get("violations", [])),
                "critical_violations": len([v for v in analysis.get("violations", []) if v.get("severity") == "critical"])
            }
        }
