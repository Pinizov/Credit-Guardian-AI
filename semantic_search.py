"""
Semantic search for legal articles using vector embeddings.

Provides nearest-neighbor search via cosine similarity.
Uses FREE local sentence-transformers model.
"""

import sqlite3
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Global model instance
_model = None


def get_model():
    """Load sentence-transformers model (singleton pattern)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model


def get_db_connection():
    """Open database connection."""
    db_path = Path(__file__).parent / "credit_guardian.db"
    return sqlite3.connect(str(db_path))


def cosine_similarity(vec1: List[float], vec2: List[float], norm1: float = None, norm2: float = None) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Optimized with pre-computed norms.
    Returns value in [-1, 1], where 1 = identical, 0 = orthogonal, -1 = opposite.
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vector dimension mismatch: {len(vec1)} != {len(vec2)}")
    
    # Dot product
    dot = sum(a * b for a, b in zip(vec1, vec2))
    
    # Norms
    if norm1 is None:
        norm1 = math.sqrt(sum(x * x for x in vec1))
    if norm2 is None:
        norm2 = math.sqrt(sum(x * x for x in vec2))
    
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot / (norm1 * norm2)


def search_similar_articles(query_vector: List[float], top_k: int = 10, 
                           document_id: int = None, min_similarity: float = 0.0) -> List[Dict]:
    """
    Find most similar articles to a query vector using cosine similarity.
    
    Args:
        query_vector: Embedding vector (1536 dims for text-embedding-3-small)
        top_k: Number of results to return
        document_id: Optional filter by document ID
        min_similarity: Minimum similarity threshold [0, 1]
    
    Returns:
        List of dicts with article details and similarity scores, sorted by similarity (desc).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT 
            ae.article_id,
            ae.document_id,
            ae.vector,
            ae.norm,
            ai.article_number,
            ai.content,
            ai.chapter_title,
            ai.section_title,
            ai.tag_primary,
            ai.tags,
            ld.title as document_title
        FROM article_embeddings ae
        JOIN article_ingestion ai ON ae.article_id = ai.article_id
        JOIN legal_documents ld ON ae.document_id = ld.id
    """
    
    params = []
    if document_id:
        query += " WHERE ae.document_id = ?"
        params.append(document_id)
    
    # Compute query norm
    query_norm = math.sqrt(sum(x * x for x in query_vector))
    
    # Load all embeddings and compute similarities (brute force for now)
    results = []
    
    for row in cursor.execute(query, params):
        (article_id, doc_id, vector_json, norm, article_number, 
         content, chapter_title, section_title, tag_primary, tags_json, doc_title) = row
        
        # Parse vector
        vector = json.loads(vector_json)
        
        # Compute similarity
        similarity = cosine_similarity(query_vector, vector, query_norm, norm)
        
        # Filter by threshold
        if similarity < min_similarity:
            continue
        
        # Parse tags
        tags = []
        if tags_json:
            try:
                tags = json.loads(tags_json)
            except:
                pass
        
        results.append({
            'article_id': article_id,
            'document_id': doc_id,
            'document_title': doc_title,
            'article_number': article_number,
            'content': content[:200] + "..." if len(content) > 200 else content,  # Truncate for display
            'full_content': content,
            'chapter_title': chapter_title,
            'section_title': section_title,
            'tag_primary': tag_primary,
            'tags': tags[:3],  # Top 3 tags
            'similarity': round(similarity, 4)
        })
    
    conn.close()
    
    # Sort by similarity (descending) and return top K
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]


def search_by_text(query_text: str, top_k: int = 10,
                   document_id: int = None, min_similarity: float = 0.5) -> List[Dict]:
    """
    Search articles by natural language query.
    
    Converts query text to embedding using local model, then performs vector search.
    FREE - No API calls required.
    
    Args:
        query_text: Natural language search query in Bulgarian
        top_k: Number of results
        document_id: Optional document filter
        min_similarity: Minimum similarity threshold
    
    Returns:
        List of matching articles with similarity scores.
    """
    # Get query embedding using local model
    model = get_model()
    query_vector = model.encode(query_text[:5000], convert_to_numpy=True).tolist()
    
    # Perform vector search
    return search_similar_articles(query_vector, top_k, document_id, min_similarity)


def get_embedding_stats() -> Dict:
    """Get statistics about stored embeddings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total embeddings
    cursor.execute("SELECT COUNT(*) FROM article_embeddings")
    stats['total_embeddings'] = cursor.fetchone()[0]
    
    # By document
    cursor.execute("""
        SELECT ld.title, COUNT(ae.id) as count
        FROM article_embeddings ae
        JOIN legal_documents ld ON ae.document_id = ld.id
        GROUP BY ae.document_id
        ORDER BY count DESC
    """)
    stats['by_document'] = [{'document': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Model distribution
    cursor.execute("""
        SELECT model_name, COUNT(*) as count
        FROM article_embeddings
        GROUP BY model_name
    """)
    stats['by_model'] = [{'model': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return stats


if __name__ == "__main__":
    # Demo: show embedding stats
    print("Embedding Statistics")
    print("=" * 60)
    
    stats = get_embedding_stats()
    
    print(f"Total embeddings: {stats['total_embeddings']}")
    print()
    
    if stats['by_model']:
        print("By model:")
        for item in stats['by_model']:
            print(f"  {item['model']}: {item['count']}")
        print()
    
    if stats['by_document']:
        print("By document (top 10):")
        for item in stats['by_document'][:10]:
            print(f"  {item['document']}: {item['count']}")
