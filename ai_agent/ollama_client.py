# ai_agent/ollama_client.py
"""Ollama HTTP API client for Credit Guardian AI agent."""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from .tracing import trace_span, add_trace_event


class OllamaClient:
    """
    Проста обвивка за Ollama HTTP API.
    Поддържа:
      • chat completion (с `response_format={"type":"json_object"}` ако моделът го поддържа)
      • fallback към чист текст → обрязване на markdown‑блокове → json.loads
    """

    def __init__(self,
                 model: str = None,
                 base_url: str = None):
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.headers = {"Content-Type": "application/json"}

    # ------------------------------------------------------------------
    # HTTP POST helper
    # ------------------------------------------------------------------
    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        resp = requests.post(url, headers=self.headers, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Chat completion – може да върне чист JSON
    # ------------------------------------------------------------------
    def chat_completion(self,
                       messages: List[Dict[str, str]],
                       temperature: float = 0.2,
                       response_format: Optional[dict] = None) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if response_format:
            payload["format"] = "json"  # Ollama uses "format" not "response_format"
        return self._post("/api/chat", payload)

    # ------------------------------------------------------------------
    # Специализирана функция – анализ на договор
    # ------------------------------------------------------------------
    def analyze_contract(self,
                         contract_text: str,
                         system_prompt: str,
                         extra_context: str = "") -> Dict[str, Any]:
        """
        Връща JSON (ако моделът не поддържа json_object, прави опит
        да извлече JSON от markdown‑блок).
        
        Note: contract_text should already be truncated by the caller (LLMClient).
        We don't truncate here to avoid cutting off instruction text.
        """
        with trace_span("ollama.analyze_contract", attributes={
                "model": self.model,
                "text_len": len(contract_text)
            }, trace_llm=True):
            # Build system prompt with RAG context (same approach as Perplexity)
            full_system_prompt = system_prompt
            if extra_context:
                full_system_prompt += f"\n\nРЕЛЕВАНТНИ ЗАКОНОВИ ТЕКСТОВЕ:\n{extra_context}"
            
            # Standard message ordering: system → user
            messages = [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": contract_text}
            ]

            # Опитваме json‑output
            raw = self.chat_completion(messages,
                                       temperature=0.2,
                                       response_format={"type": "json_object"})
            
            try:
                content = raw.get("message", {}).get("content", "")
                if isinstance(content, dict):
                    return content
                return json.loads(content)
            except Exception:
                # fallback: получаваме markdown‑blob → изрязваме JSON‑блока
                raw_text = raw.get("message", {}).get("content", "")
                add_trace_event("ollama.fallback", {"raw_len": len(raw_text)})
                for delimiter in ["```json", "```"]:
                    if delimiter in raw_text:
                        raw_text = raw_text.split(delimiter)[1].split("```")[0]
                try:
                    return json.loads(raw_text.strip())
                except json.JSONDecodeError as e:
                    add_trace_event("ollama.parse_error", {"error": str(e)})
                    return {"summary": raw_text[:500], "raw": raw_text, "error": "JSON decode failed"}

    # ------------------------------------------------------------------
    # Генериране на жалба
    # ------------------------------------------------------------------
    def generate_complaint(self,
                           analysis: Dict[str, Any],
                           system_prompt: str,
                           user_name: str,
                           user_address: str,
                           temperature: float = 0.3) -> str:
        body = json.dumps(analysis, ensure_ascii=False, indent=2)
        prompt = (
            f"Генерирай официална жалба към КЗП въз основа на следния анализ:\n{body}\n"
            f"ИМЕ: {user_name}\nАДРЕС: {user_address}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        raw = self.chat_completion(messages, temperature=temperature)
        return raw.get("message", {}).get("content", "")

