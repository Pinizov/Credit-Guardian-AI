# ai_agent/llm_client.py
"""
Unified LLM Client for Credit Guardian AI agent.

Supports multiple providers:
  - ollama: Local LLM via Ollama (FREE, no API key required)
  - perplexity: Cloud LLM via Perplexity API (requires PERPLEXITY_API_KEY)

Usage:
    from ai_agent import LLMClient
    
    client = LLMClient(provider="ollama")  # or "perplexity"
    analysis = client.analyze_contract(contract_text)
    complaint = client.generate_complaint(analysis, "Иван Иванов", "ул. Примерна 1")
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .tracing import trace_span, add_trace_event

# Import provider clients
try:
    from .ollama_client import OllamaClient
except ImportError:
    OllamaClient = None

try:
    from .perplexity_client import PerplexityClient
except ImportError:
    PerplexityClient = None

# Import RAG utilities
try:
    from .rag_utils import get_credit_analysis_context, get_complaint_context
except ImportError:
    def get_credit_analysis_context(top_k=7):
        return ""
    def get_complaint_context(top_k=5):
        return ""


def load_system_prompt() -> str:
    """Load system prompt from file or return default."""
    prompt_path = Path(__file__).parent / "legal_prompt.txt"
    
    if prompt_path.exists():
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to load legal_prompt.txt: {e}")
    
    # Fallback default prompt
    return """Вие сте експерт по защита на потребителските права при кредити в България.
Анализирайте договори и идентифицирайте нарушения на ЗПК, ЗЗП и ЗЗД.
ВИНАГИ отговаряйте на български език и връщайте валиден JSON."""


# Global system prompt (loaded once)
SYSTEM_PROMPT = load_system_prompt()


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Automatically selects provider based on AI_PROVIDER env var or constructor argument.
    Uses RAG context from embeddings database for improved accuracy.
    
    Environment Variables:
        AI_PROVIDER: "ollama" or "perplexity" (default: "ollama")
        OLLAMA_URL: Ollama server URL (default: http://localhost:11434)
        OLLAMA_MODEL: Model name for Ollama (default: llama3.2)
        PERPLEXITY_API_KEY: API key for Perplexity
        PERPLEXITY_MODEL: Model name for Perplexity
    """
    
    def __init__(self, provider: str = None, model: str = None):
        """
        Initialize LLM client with specified provider.
        
        Args:
            provider: "ollama" or "perplexity". Defaults to AI_PROVIDER env var or "ollama"
            model: Model name. Defaults to provider-specific env var
        """
        self.provider = (provider or os.getenv("AI_PROVIDER", "ollama")).lower()
        self.model = model
        self.client = None
        
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the appropriate provider client."""
        
        if self.provider == "ollama":
            if OllamaClient is None:
                raise ImportError("OllamaClient not available. Check ai_agent/ollama_client.py")
            
            self.model = self.model or os.getenv("OLLAMA_MODEL", "llama3.2")
            self.client = OllamaClient(model=self.model)
            
        elif self.provider == "perplexity":
            if PerplexityClient is None:
                raise ImportError("PerplexityClient not available. Check ai_agent/perplexity_client.py")
            
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                raise ValueError("PERPLEXITY_API_KEY environment variable is required")
            
            self.model = self.model or os.getenv("PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online")
            self.client = PerplexityClient(api_key=api_key, model=self.model)
            
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}. Use 'ollama' or 'perplexity'")
    
    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """
        Analyze a credit contract for violations.
        
        Uses RAG context from embeddings database for improved accuracy.
        
        Args:
            contract_text: Full text of the credit contract
        
        Returns:
            Dict with analysis results including violations, fees, APR calculations
        """
        with trace_span("llm.analyze_contract", attributes={
            "model": self.model,
            "provider": self.provider,
            "text_length": len(contract_text),
            "operation": "contract_analysis"
        }, trace_llm=True):
            
            if not self.client:
                add_trace_event("llm.unavailable", {"reason": "no_client_configured"})
                return self._error_response("AI анализ недостъпен (провайдър не е конфигуриран)")
            
            # Get RAG context from embeddings
            rag_context = get_credit_analysis_context(top_k=7)
            add_trace_event("rag.context_retrieved", {"context_length": len(rag_context)})
            
            # Truncate contract text once (leave room for instructions)
            max_contract_chars = 7500  # Leave ~500 chars for instructions
            truncated_contract = contract_text[:max_contract_chars]
            
            # Build analysis prompt - used consistently for all providers
            user_prompt = (
                "Анализирай следния кредитен договор и върни валиден JSON със следните полета: "
                "contract_number, creditor, principal, stated_apr, fees (списък), violations (списък), "
                "calculated_real_apr, summary.\n\n"
                f"ДОГОВОР:\n{truncated_contract}"
            )
            
            # Provider-specific calls - all receive the same formatted prompt
            if self.provider == "ollama":
                return self._analyze_with_ollama(user_prompt, rag_context)
            elif self.provider == "perplexity":
                return self._analyze_with_perplexity(user_prompt, rag_context)
            
            return self._error_response(f"Unsupported provider: {self.provider}")
    
    def _analyze_with_ollama(self, prompt: str, rag_context: str) -> Dict[str, Any]:
        """Analyze using Ollama client."""
        try:
            result = self.client.analyze_contract(
                contract_text=prompt,
                system_prompt=SYSTEM_PROMPT,
                extra_context=rag_context
            )
            add_trace_event("llm.response_received", {
                "provider": "ollama",
                "has_error": "error" in result
            })
            return result
        except Exception as e:
            add_trace_event("ollama.error", {"error": str(e)})
            return self._error_response(f"Ollama грешка: {e}")
    
    def _analyze_with_perplexity(self, user_prompt: str, rag_context: str) -> Dict[str, Any]:
        """Analyze using Perplexity client."""
        try:
            # Build system prompt with RAG context
            full_system_prompt = SYSTEM_PROMPT
            if rag_context:
                full_system_prompt += f"\n\nРЕЛЕВАНТНИ ЗАКОНОВИ ТЕКСТОВЕ:\n{rag_context}"
            
            # Use chat_completion directly for consistent prompt handling
            messages = [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat_completion(messages, temperature=0.2)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse JSON response
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                result = json.loads(content.strip())
            except json.JSONDecodeError:
                result = {"summary": content[:500], "raw": content, "error": "JSON decode failed"}
            
            add_trace_event("llm.response_received", {
                "provider": "perplexity",
                "has_error": "error" in result
            })
            return result
        except Exception as e:
            add_trace_event("perplexity.error", {"error": str(e)})
            return self._error_response(f"Perplexity грешка: {e}")
    
    def generate_complaint(self, analysis: Dict[str, Any], user_name: str, user_address: str) -> str:
        """
        Generate an official complaint to KZP (Consumer Protection Commission).
        
        Args:
            analysis: Analysis dict from analyze_contract()
            user_name: Consumer's full name
            user_address: Consumer's address
        
        Returns:
            Formatted complaint text in Bulgarian
        """
        with trace_span("llm.generate_complaint", attributes={
            "model": self.model,
            "provider": self.provider,
            "user_name_length": len(user_name),
            "operation": "complaint_generation"
        }, trace_llm=True):
            
            if not self.client:
                add_trace_event("llm.unavailable", {"reason": "no_client_configured"})
                return f"Жалба не може да бъде генерирана (провайдър {self.provider} не е конфигуриран)."
            
            # Get complaint-specific RAG context
            rag_context = get_complaint_context(top_k=5)
            
            if self.provider == "ollama":
                return self._generate_complaint_ollama(analysis, user_name, user_address, rag_context)
            elif self.provider == "perplexity":
                return self._generate_complaint_perplexity(analysis, user_name, user_address, rag_context)
            
            return "Неподдържан провайдър"
    
    def _generate_complaint_ollama(self, analysis: Dict[str, Any], user_name: str, 
                                    user_address: str, rag_context: str) -> str:
        """Generate complaint using Ollama."""
        try:
            full_prompt = SYSTEM_PROMPT
            if rag_context:
                full_prompt += f"\n\nРЕЛЕВАНТНИ ЗАКОНОВИ ТЕКСТОВЕ:\n{rag_context}"
            
            result = self.client.generate_complaint(
                analysis=analysis,
                system_prompt=full_prompt,
                user_name=user_name,
                user_address=user_address,
                temperature=0.3
            )
            add_trace_event("llm.complaint_generated", {"provider": "ollama", "length": len(result)})
            return result
        except Exception as e:
            add_trace_event("ollama.error", {"error": str(e)})
            return f"Грешка при генериране на жалба: {e}"
    
    def _generate_complaint_perplexity(self, analysis: Dict[str, Any], user_name: str,
                                        user_address: str, rag_context: str) -> str:
        """Generate complaint using Perplexity."""
        try:
            full_prompt = SYSTEM_PROMPT
            if rag_context:
                full_prompt += f"\n\nРЕЛЕВАНТНИ ЗАКОНОВИ ТЕКСТОВЕ:\n{rag_context}"
            
            body = json.dumps(analysis, ensure_ascii=False, indent=2)
            prompt = (
                f"Генерирай официална жалба до Комисията за защита на потребителите (КЗП) "
                f"на базата на следния анализ:\n{body}\n\nИМЕ: {user_name}\nАДРЕС: {user_address}"
            )
            
            messages = [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat_completion(messages, temperature=0.3)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            add_trace_event("llm.complaint_generated", {"provider": "perplexity", "length": len(result)})
            return result
        except Exception as e:
            add_trace_event("perplexity.error", {"error": str(e)})
            return f"Грешка при генериране на жалба: {e}"
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Build standard error response."""
        return {
            "contract_number": "UNKNOWN",
            "creditor": "Неразпознат",
            "principal": 0,
            "stated_apr": 0,
            "fees": [],
            "violations": [],
            "summary": message,
            "error": message
        }


# Backward compatibility alias
CreditAnalysisAgent = LLMClient


# Quick test function
def test_llm_client():
    """Test LLM client configuration."""
    provider = os.getenv("AI_PROVIDER", "ollama")
    print(f"Testing LLM client with provider: {provider}")
    
    try:
        client = LLMClient(provider=provider)
        print(f"✓ Client initialized: {client.provider} / {client.model}")
        
        # Test with sample text
        sample = "ДОГОВОР ЗА ПОТРЕБИТЕЛСКИ КРЕДИТ №12345. Главница: 1000 лв. ГПР: 48%. Такса бързо разглеждане: 50 лв."
        print(f"\nAnalyzing sample contract...")
        
        result = client.analyze_contract(sample)
        print(f"✓ Analysis complete. Keys: {list(result.keys())}")
        
        if "summary" in result:
            print(f"  Summary: {result['summary'][:100]}...")
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_llm_client()
