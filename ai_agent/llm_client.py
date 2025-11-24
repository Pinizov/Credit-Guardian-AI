import os
import json
from typing import Dict, Any

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
        if not self.client:
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
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"summary": "Неуспешен JSON парс", "raw": raw}

    def generate_complaint(self, analysis: Dict[str, Any], user_name: str, user_address: str) -> str:
        if not self.client:
            return "Жалба не може да бъде генерирана (липсва OPENAI_API_KEY)."
        body = json.dumps(analysis, ensure_ascii=False)
        prompt = f"Генерирай официална жалба на български до КЗП въз основа на анализа: {body}\nИме: {user_name}\nАдрес: {user_address}"
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
