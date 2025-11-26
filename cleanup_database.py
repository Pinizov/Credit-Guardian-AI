#!/usr/bin/env python
"""
Database Cleanup Script for Credit Guardian
Removes duplicates and optimizes the database
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "credit_guardian.db"

def cleanup_database(dry_run=True):
    """
    Clean up the database:
    1. Remove duplicate legal_documents
    2. Remove documents with empty/very short content
    3. Remove orphaned records
    4. Vacuum the database
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("=" * 70)
    print(f"DATABASE CLEANUP {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print("=" * 70)
    print()
    
    # 1. Find and remove duplicate legal_documents
    print("1. DUPLICATE LEGAL DOCUMENTS")
    print("-" * 40)
    
    cursor.execute("""
        SELECT title, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM legal_documents 
        GROUP BY title 
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()
    
    total_dups_removed = 0
    for title, count, ids in duplicates:
        id_list = [int(x) for x in ids.split(',')]
        keep_id = min(id_list)  # Keep the first (oldest) one
        remove_ids = [x for x in id_list if x != keep_id]
        
        print(f"  '{title[:50]}...'")
        print(f"    Keeping ID: {keep_id}, Removing IDs: {remove_ids}")
        
        if not dry_run:
            for rid in remove_ids:
                # First remove related articles and their data
                cursor.execute("DELETE FROM legal_article_tags WHERE article_id IN (SELECT id FROM legal_articles WHERE document_id = ?)", (rid,))
                cursor.execute("DELETE FROM article_embeddings WHERE document_id = ?", (rid,))
                cursor.execute("DELETE FROM article_ingestion WHERE document_id = ?", (rid,))
                cursor.execute("DELETE FROM legal_articles WHERE document_id = ?", (rid,))
                cursor.execute("DELETE FROM legal_documents WHERE id = ?", (rid,))
        
        total_dups_removed += len(remove_ids)
    
    print(f"\n  Total duplicate documents to remove: {total_dups_removed}")
    
    # 2. Find documents with empty/very short content
    print("\n2. DOCUMENTS WITH EMPTY/SHORT CONTENT")
    print("-" * 40)
    
    cursor.execute("""
        SELECT id, title, LENGTH(full_text) as len
        FROM legal_documents 
        WHERE full_text IS NULL OR LENGTH(full_text) < 50
    """)
    short_docs = cursor.fetchall()
    
    print(f"  Found {len(short_docs)} documents with very short content:")
    for doc_id, title, length in short_docs[:5]:
        print(f"    ID {doc_id}: '{title[:40]}...' ({length or 0} chars)")
    if len(short_docs) > 5:
        print(f"    ... and {len(short_docs) - 5} more")
    
    # Don't auto-delete these - they might have been imported for a reason
    print("\n  (Not auto-deleting - review manually if needed)")
    
    # 3. Find orphaned records
    print("\n3. ORPHANED RECORDS")
    print("-" * 40)
    
    # Articles without documents
    cursor.execute("""
        SELECT COUNT(*) FROM legal_articles la
        LEFT JOIN legal_documents ld ON la.document_id = ld.id
        WHERE ld.id IS NULL
    """)
    orphan_articles = cursor.fetchone()[0]
    print(f"  Orphaned legal_articles: {orphan_articles}")
    
    if orphan_articles > 0 and not dry_run:
        cursor.execute("""
            DELETE FROM legal_articles WHERE document_id NOT IN 
            (SELECT id FROM legal_documents)
        """)
    
    # Embeddings without articles
    cursor.execute("""
        SELECT COUNT(*) FROM article_embeddings ae
        LEFT JOIN article_ingestion ai ON ae.article_id = ai.article_id
        WHERE ai.article_id IS NULL
    """)
    orphan_embeddings = cursor.fetchone()[0]
    print(f"  Orphaned article_embeddings: {orphan_embeddings}")
    
    if orphan_embeddings > 0 and not dry_run:
        cursor.execute("""
            DELETE FROM article_embeddings WHERE article_id NOT IN 
            (SELECT article_id FROM article_ingestion)
        """)
    
    # Tags without articles
    cursor.execute("""
        SELECT COUNT(*) FROM legal_article_tags lat
        LEFT JOIN legal_articles la ON lat.article_id = la.id
        WHERE la.id IS NULL
    """)
    orphan_tags = cursor.fetchone()[0]
    print(f"  Orphaned legal_article_tags: {orphan_tags}")
    
    if orphan_tags > 0 and not dry_run:
        cursor.execute("""
            DELETE FROM legal_article_tags WHERE article_id NOT IN 
            (SELECT id FROM legal_articles)
        """)
    
    # 4. Summary of essential vs optional tables
    print("\n4. TABLE ANALYSIS")
    print("-" * 40)
    
    essential_tables = [
        'legal_documents', 'legal_articles', 'article_ingestion', 
        'article_embeddings', 'legal_article_tags',
        'contracts', 'users'  # Core app tables
    ]
    
    optional_tables = [
        'complaints', 'consumer_cases', 'contract_violations',
        'court_cases', 'credit_products', 'fees', 'payments',
        'unfair_clauses', 'creditors', 'violations', 'training_examples'
    ]
    
    print("\n  ESSENTIAL TABLES (keep):")
    for table in essential_tables:
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
        count = cursor.fetchone()[0]
        status = "[OK]" if count > 0 else "[EMPTY but needed]"
        print(f"    {status} {table}: {count} rows")
    
    print("\n  OPTIONAL TABLES (can be populated later):")
    for table in optional_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            status = "[OK]" if count > 0 else "[EMPTY]"
            print(f"    {status} {table}: {count} rows")
        except:
            print(f"    [X] {table}: table not found")
    
    # 5. Vacuum database
    print("\n5. DATABASE OPTIMIZATION")
    print("-" * 40)
    
    # Get size before
    size_before = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"  Size before: {size_before:.2f} MB")
    
    if not dry_run:
        conn.commit()
        cursor.execute("VACUUM")
        conn.commit()
        
        size_after = DB_PATH.stat().st_size / (1024 * 1024)
        print(f"  Size after: {size_after:.2f} MB")
        print(f"  Saved: {size_before - size_after:.2f} MB")
    else:
        print("  (VACUUM will run in actual cleanup)")
    
    conn.close()
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Duplicate documents to remove: {total_dups_removed}")
    print(f"  Orphaned articles: {orphan_articles}")
    print(f"  Orphaned embeddings: {orphan_embeddings}")
    print(f"  Orphaned tags: {orphan_tags}")
    print()
    
    if dry_run:
        print("This was a DRY RUN. To actually clean up, run:")
        print("  python cleanup_database.py --execute")
    else:
        print("Cleanup completed successfully!")

if __name__ == "__main__":
    import sys
    
    execute = "--execute" in sys.argv or "-e" in sys.argv
    cleanup_database(dry_run=not execute)

