#!/usr/bin/env python3
"""
Ollama Integration Test & Demo Script

This script tests and demonstrates the Ollama integration for Credit Guardian.

Usage:
    # First, start Ollama server:
    ollama serve
    
    # Pull a model (if not already):
    ollama pull llama3.2
    
    # Run this test:
    python test_ollama.py
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success: bool, message: str):
    """Print a test result."""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def test_ollama_connection() -> bool:
    """Test if Ollama server is running."""
    print_header("Test 1: Ollama Server Connection")
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            print_result(True, f"Ollama server is running at {OLLAMA_URL}")
            print(f"   Available models: {', '.join(models) if models else 'none'}")
            return True
        else:
            print_result(False, f"Ollama server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result(False, f"Cannot connect to Ollama at {OLLAMA_URL}")
        print("   💡 Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_model_available() -> bool:
    """Test if the configured model is available."""
    print_header(f"Test 2: Model '{OLLAMA_MODEL}' Availability")
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"].split(":")[0] for m in data.get("models", [])]
            
            model_base = OLLAMA_MODEL.split(":")[0]
            if model_base in models or OLLAMA_MODEL in [m["name"] for m in data.get("models", [])]:
                print_result(True, f"Model '{OLLAMA_MODEL}' is available")
                return True
            else:
                print_result(False, f"Model '{OLLAMA_MODEL}' not found")
                print(f"   💡 Pull with: ollama pull {OLLAMA_MODEL}")
                return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_simple_generation() -> bool:
    """Test basic text generation."""
    print_header("Test 3: Simple Text Generation")
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "Кажи 'Здравей' на български.",
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "")
            print_result(True, "Text generation works!")
            print(f"   Response: {result[:100]}...")
            return True
        else:
            print_result(False, f"Generation failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_result(False, "Request timed out (model may be loading)")
        print("   💡 First request can be slow. Try again.")
        return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_chat_completion() -> bool:
    """Test chat completion format (used by CreditAnalysisAgent)."""
    print_header("Test 4: Chat Completion Format")
    
    messages = [
        {"role": "system", "content": "Вие сте експерт по защита на потребителите."},
        {"role": "user", "content": "Какъв е максималният ГПР по закон?"}
    ]
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.2}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("message", {}).get("content", "")
            print_result(True, "Chat completion works!")
            print(f"   Response: {result[:150]}...")
            return True
        else:
            print_result(False, f"Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_json_output() -> bool:
    """Test JSON structured output (critical for contract analysis)."""
    print_header("Test 5: JSON Structured Output")
    
    messages = [
        {"role": "system", "content": "Винаги отговаряй с валиден JSON."},
        {"role": "user", "content": """Анализирай: "Кредит 5000 лева, ГПР 45%, срок 24 месеца"
        
Върни JSON:
{
  "principal": число,
  "apr": число,
  "term_months": число,
  "is_legal": true/false
}"""}
    ]
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("message", {}).get("content", "")
            
            # Try to parse JSON from response
            try:
                # Extract JSON if wrapped in code blocks
                json_str = result
                if "```json" in result:
                    json_str = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    json_str = result.split("```")[1].split("```")[0]
                
                parsed = json.loads(json_str.strip())
                print_result(True, "JSON output works!")
                print(f"   Parsed: {json.dumps(parsed, ensure_ascii=False)}")
                return True
            except json.JSONDecodeError:
                print_result(False, "Response is not valid JSON")
                print(f"   Raw response: {result[:200]}")
                return False
        else:
            print_result(False, f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_credit_analysis_agent() -> bool:
    """Test the actual CreditAnalysisAgent with Ollama."""
    print_header("Test 6: CreditAnalysisAgent Integration")
    
    try:
        from ai_agent import CreditAnalysisAgent
        
        # Create agent with Ollama
        agent = CreditAnalysisAgent(provider="ollama", model=OLLAMA_MODEL)
        
        # Test contract text
        contract_text = """
        ДОГОВОР ЗА ПОТРЕБИТЕЛСКИ КРЕДИТ №2025-001
        
        Кредитор: Бърз Кредит ЕООД
        Кредитополучател: Иван Иванов
        
        Главница: 5,000 лева
        ГПР: 48%
        Срок: 24 месеца
        
        Такси:
        - Такса за разглеждане: 150 лева
        - Такса усвояване: 100 лева
        - Месечна такса управление: 25 лева
        """
        
        print("   Analyzing sample contract...")
        result = agent.analyze_contract(contract_text)
        
        if "summary" in result or "violations" in result:
            print_result(True, "CreditAnalysisAgent works with Ollama!")
            print(f"   Summary: {result.get('summary', 'N/A')[:150]}...")
            if result.get("violations"):
                print(f"   Found {len(result['violations'])} violation(s)")
            return True
        else:
            print_result(False, "Analysis returned unexpected format")
            print(f"   Result: {str(result)[:200]}")
            return False
            
    except ImportError as e:
        print_result(False, f"Import error: {e}")
        print("   💡 Make sure you're in the project directory")
        return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def demo_contract_analysis():
    """Run a full demo of contract analysis."""
    print_header("DEMO: Full Contract Analysis")
    
    try:
        from ai_agent import CreditAnalysisAgent
        
        agent = CreditAnalysisAgent(provider="ollama", model=OLLAMA_MODEL)
        
        contract = """
        ДОГОВОР ЗА ПОТРЕБИТЕЛСКИ КРЕДИТ
        Номер: CRD-2025-0042
        Дата: 15.01.2025
        
        КРЕДИТОР: Бърз Кредит АД, ЕИК 123456789
        
        УСЛОВИЯ:
        - Главница: 10,000 лева
        - Годишен процент на разходите (ГПР): 55%
        - Лихвен процент: 35%
        - Срок: 36 месеца
        
        ТАКСИ:
        - Такса за бързо разглеждане: 500 лева
        - Такса за усвояване: 2% от главницата
        - Месечна такса за управление: 50 лева
        - Такса при предсрочно погасяване: 5%
        
        Общо дължима сума: 18,500 лева
        """
        
        print("\n📄 Contract being analyzed:\n")
        print(contract)
        print("\n⏳ Analyzing with Ollama (this may take 30-60 seconds)...\n")
        
        start = datetime.now()
        result = agent.analyze_contract(contract)
        elapsed = (datetime.now() - start).total_seconds()
        
        print(f"⏱️  Analysis completed in {elapsed:.1f} seconds\n")
        print("-" * 60)
        print("📊 ANALYSIS RESULT:")
        print("-" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("\n   CREDIT GUARDIAN - OLLAMA INTEGRATION TEST")
    print(f"   Server: {OLLAMA_URL}")
    print(f"   Model: {OLLAMA_MODEL}")
    print("\n" + "🧪" * 30)
    
    results = []
    
    # Run tests
    results.append(("Ollama Connection", test_ollama_connection()))
    
    if results[-1][1]:  # Only continue if server is running
        results.append(("Model Available", test_model_available()))
        
        if results[-1][1]:  # Only continue if model is available
            results.append(("Simple Generation", test_simple_generation()))
            results.append(("Chat Completion", test_chat_completion()))
            results.append(("JSON Output", test_json_output()))
            results.append(("CreditAnalysisAgent", test_credit_analysis_agent()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        print_result(result, name)
    
    print(f"\n📊 Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! Ollama integration is working.\n")
        
        # Ask for demo
        try:
            response = input("Run full contract analysis demo? [y/N]: ")
            if response.lower() == 'y':
                demo_contract_analysis()
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        print("\n⚠️  Some tests failed. Check the errors above.\n")
        print("Quick fixes:")
        print("  1. Start Ollama: ollama serve")
        print(f"  2. Pull model: ollama pull {OLLAMA_MODEL}")
        print("  3. Run this script again\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

