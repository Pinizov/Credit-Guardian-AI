"""
Creates the article_embeddings table in the database.

Uses raw sqlite3 to avoid SQLAlchemy/greenlet build issues.
"""

import sqlite3
from pathlib import Path


def create_embeddings_table():
    """Create article_embeddings table with indexes."""
    db_path = Path(__file__).parent / "credit_guardian.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL UNIQUE,
            document_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            embedding_dim INTEGER NOT NULL,
            vector TEXT NOT NULL,
            norm REAL NOT NULL,
            content_hash TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES legal_articles (id)
        )
    """)
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_article_embeddings_article_id ON article_embeddings(article_id)",
        "CREATE INDEX IF NOT EXISTS idx_article_embeddings_document_id ON article_embeddings(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_article_embeddings_model ON article_embeddings(model_name)",
        "CREATE INDEX IF NOT EXISTS idx_article_embeddings_content_hash ON article_embeddings(content_hash)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    
    # Verify table
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='article_embeddings'")
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✓ Table 'article_embeddings' created successfully")
        
        # Show schema
        cursor.execute("PRAGMA table_info(article_embeddings)")
        columns = cursor.fetchall()
        print(f"  Columns: {len(columns)}")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='article_embeddings'")
        indexes = cursor.fetchall()
        print(f"  Indexes: {len(indexes)}")
        for idx in indexes:
            print(f"    - {idx[0]}")
    else:
        print("✗ Failed to create table")
    
    conn.close()


if __name__ == "__main__":
    create_embeddings_table()
