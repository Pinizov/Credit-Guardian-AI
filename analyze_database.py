#!/usr/bin/env python
"""
Database Analysis Script for Credit Guardian
Analyzes the SQLite database and identifies unused/redundant data
"""

import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent / "credit_guardian.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))

def analyze_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=" * 70)
    print("CREDIT GUARDIAN DATABASE ANALYSIS")
    print("=" * 70)
    print(f"Database: {DB_PATH}")
    print(f"Size: {DB_PATH.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    # 1. List all tables
    print("=" * 70)
    print("1. ALL TABLES")
    print("=" * 70)
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    table_stats = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            table_stats[table] = count
            print(f"  {table}: {count:,} rows")
        except Exception as e:
            print(f"  {table}: ERROR - {e}")
            table_stats[table] = -1
    
    # 2. Analyze each table's structure and content
    print()
    print("=" * 70)
    print("2. TABLE DETAILS & ANALYSIS")
    print("=" * 70)
    
    for table in tables:
        print(f"\n--- {table} ---")
        
        # Get columns
        cursor.execute(f"PRAGMA table_info([{table}])")
        columns = cursor.fetchall()
        print(f"  Columns: {', '.join([c[1] for c in columns])}")
        
        # Sample data
        try:
            cursor.execute(f"SELECT * FROM [{table}] LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print(f"  Sample (first row): {str(rows[0])[:200]}...")
        except:
            pass
    
    # 3. Identify potential issues
    print()
    print("=" * 70)
    print("3. POTENTIAL ISSUES & RECOMMENDATIONS")
    print("=" * 70)
    
    issues = []
    recommendations = []
    
    # Empty tables
    empty_tables = [t for t, c in table_stats.items() if c == 0]
    if empty_tables:
        issues.append(f"Empty tables ({len(empty_tables)}): {', '.join(empty_tables)}")
        recommendations.append("Consider removing empty tables or populating them")
    
    # Very small tables (< 10 rows)
    small_tables = [t for t, c in table_stats.items() if 0 < c < 10]
    if small_tables:
        issues.append(f"Very small tables (< 10 rows): {', '.join(small_tables)}")
    
    # Check for duplicate data
    print("\n  Checking for duplicates...")
    
    # Check legal_documents for duplicates
    if 'legal_documents' in tables:
        cursor.execute("""
            SELECT title, COUNT(*) as cnt 
            FROM legal_documents 
            GROUP BY title 
            HAVING cnt > 1
            ORDER BY cnt DESC
            LIMIT 10
        """)
        dups = cursor.fetchall()
        if dups:
            issues.append(f"Duplicate legal_documents titles: {len(dups)} duplicates found")
            print(f"\n  Duplicate titles in legal_documents:")
            for title, cnt in dups[:5]:
                print(f"    - '{title[:50]}...' appears {cnt} times")
    
    # Check legal_articles for duplicates
    if 'legal_articles' in tables:
        cursor.execute("""
            SELECT document_id, article_number, COUNT(*) as cnt 
            FROM legal_articles 
            GROUP BY document_id, article_number 
            HAVING cnt > 1
            LIMIT 10
        """)
        dups = cursor.fetchall()
        if dups:
            issues.append(f"Duplicate legal_articles: {len(dups)} duplicates found")
    
    # Check article_ingestion vs legal_articles
    if 'article_ingestion' in tables and 'legal_articles' in tables:
        cursor.execute("SELECT COUNT(*) FROM article_ingestion")
        ing_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM legal_articles")
        art_count = cursor.fetchone()[0]
        
        if ing_count > 0 and art_count > 0:
            if abs(ing_count - art_count) > 100:
                issues.append(f"article_ingestion ({ing_count}) vs legal_articles ({art_count}) mismatch")
    
    # Check embeddings coverage
    if 'article_embeddings' in tables and 'article_ingestion' in tables:
        cursor.execute("SELECT COUNT(*) FROM article_embeddings")
        emb_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM article_ingestion")
        ing_count = cursor.fetchone()[0]
        
        if ing_count > 0:
            coverage = (emb_count / ing_count) * 100 if ing_count > 0 else 0
            print(f"\n  Embeddings coverage: {emb_count}/{ing_count} ({coverage:.1f}%)")
            if coverage < 90:
                recommendations.append(f"Run generate_embeddings.py to complete coverage (currently {coverage:.1f}%)")
    
    # 4. Data quality checks
    print()
    print("=" * 70)
    print("4. DATA QUALITY CHECKS")
    print("=" * 70)
    
    # Check for NULL content
    if 'legal_documents' in tables:
        cursor.execute("""
            SELECT COUNT(*) FROM legal_documents 
            WHERE full_text IS NULL OR full_text = ''
        """)
        null_content = cursor.fetchone()[0]
        if null_content > 0:
            print(f"  legal_documents with empty content: {null_content}")
            issues.append(f"{null_content} legal_documents have empty content")
    
    # Check for very short content
    if 'legal_documents' in tables:
        cursor.execute("""
            SELECT COUNT(*) FROM legal_documents 
            WHERE LENGTH(full_text) < 100 AND full_text IS NOT NULL
        """)
        short_content = cursor.fetchone()[0]
        if short_content > 0:
            print(f"  legal_documents with very short content (<100 chars): {short_content}")
    
    # Check source_url patterns
    if 'legal_documents' in tables:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN source_url LIKE 'file:///%' THEN 'Local files'
                    WHEN source_url LIKE 'http%' THEN 'Web URLs'
                    WHEN source_url IS NULL THEN 'No URL'
                    ELSE 'Other'
                END as source_type,
                COUNT(*) as cnt
            FROM legal_documents
            GROUP BY source_type
        """)
        sources = cursor.fetchall()
        print(f"\n  Document sources:")
        for src_type, cnt in sources:
            print(f"    - {src_type}: {cnt}")
    
    # 5. Storage analysis
    print()
    print("=" * 70)
    print("5. STORAGE ANALYSIS")
    print("=" * 70)
    
    # Estimate table sizes
    print("\n  Estimated table sizes:")
    for table in sorted(tables, key=lambda t: table_stats.get(t, 0), reverse=True):
        if table_stats.get(table, 0) > 0:
            # Get a rough estimate
            cursor.execute(f"SELECT * FROM [{table}] LIMIT 1")
            row = cursor.fetchone()
            if row:
                row_size = len(str(row))
                total_est = row_size * table_stats[table]
                print(f"    {table}: ~{total_est / (1024*1024):.2f} MB ({table_stats[table]:,} rows)")
    
    # 6. Summary
    print()
    print("=" * 70)
    print("6. SUMMARY & RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n  ISSUES FOUND:")
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. {issue}")
    else:
        print("    No major issues found!")
    
    print("\n  RECOMMENDATIONS:")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"    {i}. {rec}")
    
    # Tables that might not be needed
    print("\n  POTENTIALLY UNNECESSARY TABLES:")
    unnecessary = []
    
    # Empty tables
    for t in empty_tables:
        unnecessary.append((t, "Empty - no data"))
    
    # Check for test/temp tables
    for t in tables:
        t_lower = t.lower()
        if any(x in t_lower for x in ['test', 'temp', 'backup', 'old', '_copy']):
            if t not in [u[0] for u in unnecessary]:
                unnecessary.append((t, "Appears to be test/temp table"))
    
    # SQLite internal tables
    for t in tables:
        if t.startswith('sqlite_'):
            unnecessary.append((t, "SQLite internal table"))
    
    if unnecessary:
        for t, reason in unnecessary:
            print(f"    - {t}: {reason}")
    else:
        print("    All tables appear to be in use")
    
    # 7. Cleanup suggestions
    print()
    print("=" * 70)
    print("7. CLEANUP COMMANDS (if needed)")
    print("=" * 70)
    
    if empty_tables:
        print("\n  To remove empty tables, run:")
        for t in empty_tables:
            print(f"    DROP TABLE IF EXISTS [{t}];")
    
    print("\n  To optimize database size after cleanup:")
    print("    VACUUM;")
    
    conn.close()
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)

if __name__ == "__main__":
    analyze_database()

