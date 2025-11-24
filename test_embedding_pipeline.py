"""
Test the embedding pipeline with a small sample of articles.

This validates the full workflow: table creation → embedding generation → similarity search.
Uses first 5 articles to avoid excessive API costs during testing.
"""

import os
import sys
import sqlite3
from pathlib import Path


def get_db_connection():
    """Open database connection."""
    db_path = Path(__file__).parent / "credit_guardian.db"
    return sqlite3.connect(str(db_path))


def test_embedding_generation():
    """Test generating embeddings for sample articles."""
    print("=" * 70)
    print("TEST 1: Embedding Generation (FREE Local Model)")
    print("=" * 70)
    print()
    
    # Load model
    try:
        from generate_embeddings import get_model, EMBEDDING_DIM
        print("Loading sentence-transformers model...")
        get_model()
        print("✓ Model loaded successfully")
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Install with: pip install sentence-transformers")
        return False
    print()
    
    # Get sample articles
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT article_id, document_id, content, tag_primary
        FROM article_ingestion
        ORDER BY article_id
        LIMIT 5
    """)
    
    samples = cursor.fetchall()
    print(f"Selected {len(samples)} sample articles:")
    for article_id, doc_id, content, tag in samples:
        preview = content[:80].replace('\n', ' ')
        print(f"  Article {article_id} (doc {doc_id}): {preview}... [tag: {tag}]")
    print()
    
    # Import and run embedding generator
    from generate_embeddings import get_embedding, store_embedding, compute_content_hash
    
    success = 0
    for article_id, doc_id, content, tag in samples:
        print(f"Processing article {article_id}...", end=" ")
        
        vector = get_embedding(content)
        if vector and len(vector) == EMBEDDING_DIM:
            content_hash = compute_content_hash(content)
            store_embedding(conn, article_id, doc_id, vector, content_hash)
            print("✓")
            success += 1
        else:
            print("✗")
    
    conn.close()
    
    print()
    print(f"Generated {success}/{len(samples)} embeddings")
    print()
    
    return success == len(samples)


def test_similarity_search():
    """Test semantic search functionality."""
    print("=" * 70)
    print("TEST 2: Similarity Search")
    print("=" * 70)
    print()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we have embeddings
    cursor.execute("SELECT COUNT(*) FROM article_embeddings")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("✗ No embeddings found. Run test_embedding_generation() first.")
        conn.close()
        return False
    
    print(f"✓ Found {count} embeddings in database")
    print()
    
    # Get one article as query
    cursor.execute("""
        SELECT ae.article_id, ae.vector, ai.content, ai.tag_primary
        FROM article_embeddings ae
        JOIN article_ingestion ai ON ae.article_id = ai.article_id
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if not row:
        print("✗ Could not fetch test article")
        conn.close()
        return False
    
    query_id, vector_json, content, tag = row
    print(f"Query article: {query_id}")
    print(f"  Content: {content[:100]}...")
    print(f"  Tag: {tag}")
    print()
    
    conn.close()
    
    # Perform similarity search
    import json
    from semantic_search import search_similar_articles
    
    query_vector = json.loads(vector_json)
    results = search_similar_articles(query_vector, top_k=3)
    
    print(f"Top {len(results)} similar articles:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Article {result['article_id']} (similarity: {result['similarity']:.4f})")
        print(f"   Document: {result['document_title']}")
        print(f"   Content: {result['content']}")
        print(f"   Tag: {result['tag_primary']}")
    
    print()
    
    # Validate results
    if not results:
        print("✗ No results returned")
        return False
    
    if results[0]['article_id'] != query_id:
        print("✗ Top result should be the query article itself")
        return False
    
    if results[0]['similarity'] < 0.99:
        print(f"✗ Self-similarity should be ~1.0, got {results[0]['similarity']}")
        return False
    
    print("✓ Similarity search working correctly")
    return True


def test_text_search():
    """Test natural language search."""
    print()
    print("=" * 70)
    print("TEST 3: Natural Language Search (FREE Local Model)")
    print("=" * 70)
    print()
    
    # Sample query in Bulgarian
    query = "трудови отношения и заплата"
    print(f"Query: '{query}'")
    print()
    
    from semantic_search import search_by_text
    
    try:
        results = search_by_text(query, top_k=3, min_similarity=0.3)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Article {result['article_id']} (similarity: {result['similarity']:.4f})")
            print(f"   Document: {result['document_title']}")
            print(f"   Content: {result['content']}")
            print(f"   Tag: {result['tag_primary']}")
        
        print()
        print("✓ Text search working")
        return True
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("█" * 70)
    print("  EMBEDDING PIPELINE TEST SUITE")
    print("█" * 70)
    print()
    
    results = []
    
    # Test 1: Generate embeddings
    results.append(("Embedding Generation", test_embedding_generation()))
    
    # Test 2: Similarity search
    results.append(("Similarity Search", test_similarity_search()))
    
    # Test 3: Text search
    results.append(("Natural Language Search", test_text_search()))
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed! Embedding pipeline is ready.")
        print()
        print("Next steps:")
        print("  1. Generate embeddings for all articles: python generate_embeddings.py")
        print("  2. Use semantic_search.py in your AI agent for retrieval")
    else:
        print()
        print("⚠ Some tests failed. Please review errors above.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
