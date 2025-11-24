import os
import json
from typing import Dict, Any
from .tracing import trace_span, add_trace_event

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # fallback when lib missing

SYSTEM_PROMPT = (
    "Вие сте експерт по защита на потребителите при кредити в България. "
    "Идентифицирате незаконни такси, неправилен ГПР, неравноправни клаузи. "
    "Винаги отговаряте на български език и връщате коректен JSON."
)


class CreditAnalysisAgent:
    def __init__(self, model: str = "gpt-4"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        with trace_span("llm.analyze_contract", attributes={
            "model": self.model,
            "text_length": len(contract_text),
            "operation": "contract_analysis"
        }, trace_llm=True):
            if not self.client:
                add_trace_event("llm.unavailable", {"reason": "missing_api_key"})
                return {
                    "contract_number": "UNKNOWN",
                    "creditor": "Неразпознат",
                    "principal": 0,
                    "stated_apr": 0,
                    "fees": [],
                    "violations": [],
                    "summary": "AI анализ недостъпен (липсва OPENAI_API_KEY)",
                }
            
            prompt = (
                "Анализирай договора и върни JSON със следните ключове: "
                "contract_number, creditor, principal, stated_apr, fees(list), violations(list), summary.\n" + contract_text[:8000]
            )
            
            add_trace_event("llm.request_prepared", {
                "prompt_length": len(prompt),
                "temperature": 0.2
            })
            
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            
            raw = resp.choices[0].message.content
            add_trace_event("llm.response_received", {
                "response_length": len(raw),
                "tokens_used": resp.usage.total_tokens if resp.usage else 0
            })
            
            try:
                result = json.loads(raw)
                add_trace_event("llm.parse_success", {"keys": list(result.keys())})
                return result
            except json.JSONDecodeError as e:
                add_trace_event("llm.parse_error", {"error": str(e)})
                return {"summary": "Неуспешен JSON парс", "raw": raw}

    def generate_complaint(self, analysis: Dict[str, Any], user_name: str, user_address: str) -> str:
        with trace_span("llm.generate_complaint", attributes={
            "model": self.model,
            "user_name_length": len(user_name),
            "operation": "complaint_generation"
        }, trace_llm=True):
            if not self.client:
                add_trace_event("llm.unavailable", {"reason": "missing_api_key"})
                return "Жалба не може да бъде генерирана (липсва OPENAI_API_KEY)."
            
            body = json.dumps(analysis, ensure_ascii=False)
            prompt = f"Генерирай официална жалба на български до КЗП въз основа на анализа: {body}\nИме: {user_name}\nАдрес: {user_address}"
            
            add_trace_event("llm.request_prepared", {
                "prompt_length": len(prompt),
                "temperature": 0.3
            })
            
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            result = resp.choices[0].message.content
            add_trace_event("llm.response_received", {
                "response_length": len(result),
                "tokens_used": resp.usage.total_tokens if resp.usage else 0
            })
            
            return result
