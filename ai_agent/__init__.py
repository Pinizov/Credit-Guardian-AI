"""
AI Agent package for Credit Guardian.

Provides LLM-based contract analysis and complaint generation
with support for multiple providers (Ollama, Perplexity).

Usage:
    from ai_agent import LLMClient
    
    # Using Ollama (local, free)
    client = LLMClient(provider="ollama")
    
    # Using Perplexity (cloud, requires API key)
    client = LLMClient(provider="perplexity")
    
    # Analyze a contract
    analysis = client.analyze_contract(contract_text)
    
    # Generate a complaint
    complaint = client.generate_complaint(analysis, "Name", "Address")

Environment Variables:
    AI_PROVIDER: "ollama" or "perplexity" (default: "ollama")
    OLLAMA_URL: Ollama server URL (default: http://localhost:11434)
    OLLAMA_MODEL: Model name for Ollama (default: llama3.2)
    PERPLEXITY_API_KEY: API key for Perplexity
    PERPLEXITY_MODEL: Model name for Perplexity
"""

from .llm_client import LLMClient, CreditAnalysisAgent

# Optional imports (don't fail if dependencies missing)
try:
    from .ollama_client import OllamaClient
except ImportError:
    OllamaClient = None

try:
    from .perplexity_client import PerplexityClient
except ImportError:
    PerplexityClient = None

try:
    from .pdf_processor import PDFProcessor
except ImportError:
    PDFProcessor = None

try:
    from .rag_utils import retrieve_relevant_laws, get_rag_context
except ImportError:
    retrieve_relevant_laws = None
    get_rag_context = None

__all__ = [
    "LLMClient",
    "CreditAnalysisAgent",  # Backward compatibility alias
    "OllamaClient",
    "PerplexityClient",
    "PDFProcessor",
    "retrieve_relevant_laws",
    "get_rag_context",
]
