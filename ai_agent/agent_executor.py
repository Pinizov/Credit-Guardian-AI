from datetime import datetime
from typing import Dict, Any
from .llm_client import CreditAnalysisAgent
from .pdf_processor import PDFProcessor

class AgentExecutor:
    def __init__(self):
        self.agent = CreditAnalysisAgent()

    def process(self, pdf_path: str, user: Dict[str, str]) -> Dict[str, Any]:
        text = PDFProcessor.extract_text(pdf_path)
        analysis = self.agent.analyze_contract(text)
        complaint = self.agent.generate_complaint(analysis, user.get("name", "Потребител"), user.get("address", ""))
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "complaint": complaint,
            "text_excerpt": text[:1000],
        }
