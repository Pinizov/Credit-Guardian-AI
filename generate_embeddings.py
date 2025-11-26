"""
Batch processor to generate and store embeddings for legal articles.

Uses sentence-transformers 'paraphrase-multilingual-MiniLM-L12-v2' model (384 dimensions).
FREE - Runs locally without API calls. Supports Bulgarian language.
Processes articles from article_ingestion table and stores vectors in article_embeddings.
"""

import sqlite3
import json
import hashlib
import math
import os
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Sentence Transformers configuration (FREE, local)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384  # Output dimension for this model
BATCH_SIZE = 50  # Process 50 articles per batch (local processing)
MAX_RETRIES = 1  # No retries needed for local model
RETRY_DELAY = 0

# Global model instance (loaded once)
_model = None


def get_db_connection():
    """Open database connection."""
    db_path = Path(__file__).parent / "credit_guardian.db"
    return sqlite3.connect(str(db_path))


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of article content for change detection."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compute_l2_norm(vector: List[float]) -> float:
    """Compute L2 norm for cosine similarity optimization."""
    return math.sqrt(sum(x * x for x in vector))


def get_model():
    """Load sentence-transformers model (singleton pattern)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading embedding model (first time only)...")
            _model = SentenceTransformer(EMBEDDING_MODEL)
            print(f"✓ Model loaded: {EMBEDDING_MODEL}")
        except ImportError:
            print("✗ sentence-transformers not installed")
            print("  Install with: pip install sentence-transformers")
            raise
    return _model


def get_embedding(text: str) -> Optional[List[float]]:
    """
    Get embedding vector using local sentence-transformers model.
    
    FREE - No API calls, runs locally. Supports Bulgarian.
    Returns None if encoding fails.
    """
    try:
        model = get_model()
        
        # Truncate text to reasonable length (model handles tokenization)
        text = text[:5000]  # ~5000 chars is safe for most models
        
        # Generate embedding
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Convert to list of floats
        return embedding.tolist()
        
    except Exception as e:
        print(f"  Encoding failed: {e}")
        return None


def get_pending_articles(conn: sqlite3.Connection, limit: int = None) -> List[Dict]:
    """
    Get articles that need embeddings (not yet in article_embeddings or content changed).
    
    Returns list of dicts with article_id, document_id, content, content_hash.
    """
    cursor = conn.cursor()
    
    # Get articles without embeddings or with changed content
    query = """
        SELECT 
            ai.article_id,
            ai.document_id,
            ai.content,
            ai.tag_primary,
            ai.tags
        FROM article_ingestion ai
        LEFT JOIN article_embeddings ae ON ai.article_id = ae.article_id
        WHERE ae.id IS NULL
           OR ae.content_hash != ?
    """
    
    articles = []
    
    if limit:
        query += f" LIMIT {limit}"
    
    for row in cursor.execute(query, (compute_content_hash(""),)):  # Dummy hash for initial run
        article_id, document_id, content, tag_primary, tags_json = row
        
        # Build composite text for embedding: content + primary tag + all tags
        embedding_text = content
        if tag_primary:
            embedding_text += f"\n\nПървичен таг: {tag_primary}"
        if tags_json:
            try:
                tags = json.loads(tags_json)
                tag_names = [t['tag'] for t in tags[:5]]  # Top 5 tags
                if tag_names:
                    embedding_text += f"\nТагове: {', '.join(tag_names)}"
            except:
                pass
        
        articles.append({
            'article_id': article_id,
            'document_id': document_id,
            'content': embedding_text,
            'content_hash': compute_content_hash(content)  # Hash original content only
        })
    
    return articles


def store_embedding(conn: sqlite3.Connection, article_id: int, document_id: int, 
                    vector: List[float], content_hash: str):
    """Store embedding vector in database."""
    cursor = conn.cursor()
    
    norm = compute_l2_norm(vector)
    vector_json = json.dumps(vector)
    
    # Upsert (INSERT OR REPLACE)
    cursor.execute("""
        INSERT OR REPLACE INTO article_embeddings 
        (article_id, document_id, model_name, embedding_dim, vector, norm, content_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (article_id, document_id, EMBEDDING_MODEL, EMBEDDING_DIM, vector_json, norm, content_hash))
    
    conn.commit()


def process_batch(articles: List[Dict], conn: sqlite3.Connection) -> Tuple[int, int]:
    """
    Process a batch of articles and store embeddings.
    
    Returns (success_count, failure_count).
    """
    success = 0
    failure = 0
    
    for i, article in enumerate(articles, 1):
        article_id = article['article_id']
        document_id = article['document_id']
        content = article['content']
        content_hash = article['content_hash']
        
        print(f"  [{i}/{len(articles)}] Article {article_id}...", end=" ")
        
        vector = get_embedding(content)
        
        if vector:
            if len(vector) == EMBEDDING_DIM:
                store_embedding(conn, article_id, document_id, vector, content_hash)
                print("✓")
                success += 1
            else:
                print(f"✗ Wrong dimension: {len(vector)} != {EMBEDDING_DIM}")
                failure += 1
        else:
            print("✗ Encoding failed")
            failure += 1
    
    return success, failure


def main():
    """Main entry point for batch processing."""
    print(f"Embedding Pipeline (FREE - Local Model)")
    print(f"Model: {EMBEDDING_MODEL} ({EMBEDDING_DIM} dims)")
    print(f"Batch size: {BATCH_SIZE}")
    print()
    
    # Load model once before processing
    try:
        get_model()
    except ImportError:
        return
    
    conn = get_db_connection()
    
    # Get pending articles
    print("Scanning for articles needing embeddings...")
    pending = get_pending_articles(conn)
    print(f"Found {len(pending)} articles to process")
    
    if not pending:
        print("✓ All articles already have embeddings")
        conn.close()
        return
    
    # Process in batches
    total_success = 0
    total_failure = 0
    
    for batch_num, start_idx in enumerate(range(0, len(pending), BATCH_SIZE), 1):
        batch = pending[start_idx:start_idx + BATCH_SIZE]
        print(f"\nBatch {batch_num}/{math.ceil(len(pending) / BATCH_SIZE)} ({len(batch)} articles)")
        
        success, failure = process_batch(batch, conn)
        total_success += success
        total_failure += failure
        
        print(f"  Batch result: {success} success, {failure} failed")
    
    conn.close()
    
    print()
    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Total processed: {total_success + total_failure}")
    print(f"  Success: {total_success}")
    print(f"  Failed: {total_failure}")
    if total_success + total_failure > 0:
        print(f"  Success rate: {total_success / (total_success + total_failure) * 100:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
