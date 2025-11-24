"""Apply SQLite schema changes for normalized chapter/section and tag score columns."""
import sqlite3

def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == column for r in cur.fetchall())

def add_column(cur, table, column_def):
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")

def main():
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()

    # legal_articles new columns
    article_cols = [
        ('chapter_number', 'TEXT'),
        ('chapter_title', 'TEXT'),
        ('section_number', 'TEXT'),
        ('section_title', 'TEXT'),
    ]
    for col, ctype in article_cols:
        if not column_exists(cur, 'legal_articles', col):
            print(f"Adding column legal_articles.{col}")
            add_column(cur, 'legal_articles', f"{col} {ctype}")

    # legal_article_tags score column
    if not column_exists(cur, 'legal_article_tags', 'score'):
        print("Adding column legal_article_tags.score")
        add_column(cur, 'legal_article_tags', 'score REAL')

    conn.commit()
    conn.close()
    print("✅ Schema updates applied.")

if __name__ == '__main__':
    main()
