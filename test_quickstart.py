#!/usr/bin/env python3
"""Quick Start Test Script"""
import time
import sys

print("=" * 60)
print("CREDIT GUARDIAN AI - QUICK START TEST")
print("=" * 60)

# Test 1: Tracing System
print("\n[1/3] Testing Tracing System...")
try:
    from ai_agent.tracing import trace_span, add_trace_event
    
    with trace_span('test_operation', attributes={'test': 'quick_start'}):
        add_trace_event('test_started')
        time.sleep(0.1)
        add_trace_event('test_completed')
    
    print("✓ Tracing system works!")
except Exception as e:
    print(f"✗ Tracing error: {e}")

# Test 2: Evaluation Framework
print("\n[2/3] Testing Evaluation Framework...")
try:
    from evaluation.dataset import EvaluationDataset
    from evaluation.metrics import EvaluationMetrics
    
    # Test metrics calculation
    accuracy = EvaluationMetrics.calculate_accuracy(
        predicted={'creditor': 'Bank A', 'principal': 5000},
        expected={'creditor': 'Bank A', 'principal': 5000}
    )
    print(f"✓ Evaluation framework works! Accuracy: {accuracy:.2%}")
except Exception as e:
    print(f"✗ Evaluation error: {e}")

# Test 3: Database Connection
print("\n[3/3] Testing Database Connection...")
try:
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent / "credit_guardian.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count articles
        cursor.execute("SELECT COUNT(*) FROM legal_articles")
        article_count = cursor.fetchone()[0]
        
        # Count embeddings
        cursor.execute("SELECT COUNT(*) FROM article_embeddings")
        embedding_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✓ Database connected!")
        print(f"  - Articles: {article_count:,}")
        print(f"  - Embeddings: {embedding_count:,}")
    else:
        print("✗ Database not found")
except Exception as e:
    print(f"✗ Database error: {e}")

# Test 4: Semantic Search
print("\n[4/4] Testing Semantic Search...")
try:
    from semantic_search import search_by_text
    
    results = search_by_text("кредит договор", top_k=3)
    print(f"✓ Semantic search works!")
    print(f"  - Found {len(results)} results")
    if results:
        print(f"  - Top match: {results[0]['code_name']} - Article {results[0]['article_number']}")
except Exception as e:
    print(f"✗ Semantic search error: {e}")

print("\n" + "=" * 60)
print("QUICK START TEST COMPLETED")
print("=" * 60)
