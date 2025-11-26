"""Perplexity API client for Credit Guardian AI agent.
Provides contract analysis using Perplexity's Sonar models.
"""
import os
import json
from typing import Dict, Any, Optional
import requests


class PerplexityClient:
    """Client for Perplexity API integration."""
    
    BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-small-128k-chat"):
        """Initialize Perplexity client.
        
        Args:
            api_key: Perplexity API key (or set PERPLEXITY_API_KEY env var)
            model: Model to use (default: llama-3.1-sonar-small-128k-chat)
                   Options: llama-3.1-sonar-small-128k-chat, llama-3.1-sonar-large-128k-chat,
                           llama-3.1-sonar-huge-128k-chat
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def chat_completion(
        self, 
        messages: list[dict[str, str]], 
        temperature: float = 0.2,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request to Perplexity API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            **kwargs: Additional API parameters
        
        Returns:
            API response dict with 'choices', 'usage', etc.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_detail = e.response.text
            except:
                pass
            return {
                "error": error_detail,
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "error": "API request failed",
                            "details": error_detail
                        })
                    }
                }]
            }
    
    def analyze_contract(self, contract_text: str, system_prompt: str) -> Dict[str, Any]:
        """Analyze a credit contract using Perplexity.
        
        Args:
            contract_text: Full text of the contract to analyze
            system_prompt: System instructions for the AI
        
        Returns:
            Parsed analysis result as dict
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Анализирай договора и върни JSON:\n\n{contract_text[:8000]}"}
        ]
        
        response = self.chat_completion(messages, temperature=0.1)
        
        if "error" in response:
            return {
                "error": response["error"],
                "contract_number": "UNKNOWN",
                "creditor": "Неразпознат",
                "summary": f"Грешка при анализ: {response['error']}"
            }
        
        try:
            content = response["choices"][0]["message"]["content"]
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            result["_metadata"] = {
                "model": self.model,
                "provider": "perplexity",
                "usage": response.get("usage", {})
            }
            return result
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {
                "error": f"Failed to parse response: {e}",
                "raw_response": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "contract_number": "UNKNOWN",
                "creditor": "Неразпознат",
                "summary": "Грешка при обработка на отговор"
            }


def test_perplexity():
    """Test Perplexity API connection."""
    client = PerplexityClient()
    
    if not client.api_key:
        print("Error: PERPLEXITY_API_KEY not set")
        return
    
    test_prompt = "Кои са основните закони за защита на потребителите при кредити в България?"
    
    messages = [
        {"role": "system", "content": "Ти си експерт по българско законодателство."},
        {"role": "user", "content": test_prompt}
    ]
    
    print("Testing Perplexity API...")
    response = client.chat_completion(messages, max_tokens=500)
    
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Success! Model: {client.model}")
        print(f"Response: {response['choices'][0]['message']['content'][:200]}...")
        print(f"Usage: {response.get('usage', {})}")


if __name__ == "__main__":
    test_perplexity()
