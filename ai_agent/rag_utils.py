# ai_agent/rag_utils.py
"""
RAG (Retrieval-Augmented Generation) utilities for Credit Guardian.

Provides functions to retrieve relevant legal context from the vector database
for augmenting LLM prompts with accurate, up-to-date legal information.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path for semantic_search import
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def retrieve_relevant_laws(query: str, top_k: int = 7, min_similarity: float = 0.3) -> List[Dict]:
    """
    Retrieve relevant legal articles for a given query using semantic search.
    
    Uses the local sentence-transformers model for embedding and cosine similarity
    search against the article_embeddings table.
    
    Args:
        query: Natural language query (e.g., "ГПР, нелегални такси, забранени практики")
        top_k: Maximum number of results to return (default: 7)
        min_similarity: Minimum similarity threshold (default: 0.3)
    
    Returns:
        List of dicts with keys:
            - document_title: Name of the source law/document
            - article_number: Article identifier (e.g., "чл. 10а")
            - content: Full article text
            - similarity: Cosine similarity score (0-1)
            - tag_primary: Primary classification tag
    """
    try:
        from semantic_search import search_by_text
        
        results = search_by_text(
            query_text=query,
            top_k=top_k,
            min_similarity=min_similarity
        )
        
        # Format results for LLM context
        formatted = []
        for r in results:
            formatted.append({
                'document_title': r.get('document_title', 'Неизвестен документ'),
                'article_number': r.get('article_number', ''),
                'content': r.get('full_content', r.get('content', '')),
                'similarity': r.get('similarity', 0.0),
                'tag_primary': r.get('tag_primary', ''),
                'chapter_title': r.get('chapter_title', ''),
                'section_title': r.get('section_title', ''),
            })
        
        return formatted
        
    except ImportError as e:
        print(f"Warning: semantic_search not available: {e}")
        return []
    except Exception as e:
        print(f"Warning: RAG retrieval failed: {e}")
        return []


def format_context_for_llm(articles: List[Dict], max_chars: int = 6000) -> str:
    """
    Format retrieved articles into a context string for LLM consumption.
    
    Args:
        articles: List of article dicts from retrieve_relevant_laws()
        max_chars: Maximum total characters for context (default: 6000)
    
    Returns:
        Formatted string with relevant legal passages
    """
    if not articles:
        return ""
    
    parts = []
    total_chars = 0
    
    for article in articles:
        doc_title = article.get('document_title', '')
        art_num = article.get('article_number', '')
        content = article.get('content', '')
        
        # Build article reference
        header = f"[{doc_title}]"
        if art_num:
            header += f" {art_num}"
        
        entry = f"{header}:\n{content}\n"
        
        # Check character limit
        if total_chars + len(entry) > max_chars:
            # Try to fit truncated version
            remaining = max_chars - total_chars - len(header) - 10
            if remaining > 100:
                entry = f"{header}:\n{content[:remaining]}...\n"
                parts.append(entry)
            break
        
        parts.append(entry)
        total_chars += len(entry)
    
    return "\n".join(parts)


def get_rag_context(query: str, top_k: int = 7) -> str:
    """
    One-liner to get formatted RAG context for a query.
    
    Combines retrieve_relevant_laws() and format_context_for_llm().
    
    Args:
        query: Search query
        top_k: Number of articles to retrieve
    
    Returns:
        Formatted context string ready for LLM
    """
    articles = retrieve_relevant_laws(query, top_k=top_k)
    return format_context_for_llm(articles)


# Predefined queries for common use cases
CREDIT_ANALYSIS_QUERY = "ГПР годишен процент на разходите, нелегални такси, забранени практики, потребителски кредит, неравноправни клаузи"
COMPLAINT_GENERATION_QUERY = "жалба КЗП, защита на потребителите, нарушения кредитор, незаконни практики"


def get_credit_analysis_context(top_k: int = 7) -> str:
    """Get RAG context optimized for credit contract analysis."""
    return get_rag_context(CREDIT_ANALYSIS_QUERY, top_k=top_k)


def get_complaint_context(top_k: int = 5) -> str:
    """Get RAG context optimized for complaint generation."""
    return get_rag_context(COMPLAINT_GENERATION_QUERY, top_k=top_k)


if __name__ == "__main__":
    # Demo: test RAG retrieval
    print("Testing RAG utilities...")
    print("=" * 60)
    
    articles = retrieve_relevant_laws("максимален ГПР потребителски кредит", top_k=3)
    
    if articles:
        print(f"Found {len(articles)} relevant articles:\n")
        for i, art in enumerate(articles, 1):
            print(f"{i}. [{art['document_title']}] {art['article_number']}")
            print(f"   Similarity: {art['similarity']:.3f}")
            print(f"   Content: {art['content'][:100]}...")
            print()
    else:
        print("No articles found. Make sure embeddings are generated.")
    
    print("=" * 60)
    print("\nFormatted context for LLM:")
    print(get_credit_analysis_context(top_k=3)[:500] + "...")

