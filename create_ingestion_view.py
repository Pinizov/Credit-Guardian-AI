"""Create materialized ingestion table and view combining articles and tags for AI embedding pipeline."""
import sqlite3, json

def main():
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()

    # Create materialized table (drop if exists for rebuild)
    cur.execute("DROP TABLE IF EXISTS article_ingestion")
    cur.execute("""
        CREATE TABLE article_ingestion (
            article_id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL,
            article_number TEXT,
            content TEXT,
            chapter_number TEXT,
            chapter_title TEXT,
            section_number TEXT,
            section_title TEXT,
            tags TEXT,           -- JSON array of tag objects {tag, score}
            tag_primary TEXT,    -- top scoring tag
            tag_vector_hint TEXT -- comma separated tags for quick indexing
        )
    """)

    # Aggregate tags per article
    cur.execute("""SELECT a.id, a.document_id, a.article_number, a.content, a.chapter_number, a.chapter_title,
               a.section_number, a.section_title,
               GROUP_CONCAT(t.tag || ':' || COALESCE(t.score,'')) as tag_scores
        FROM legal_articles a
        LEFT JOIN legal_article_tags t ON t.article_id = a.id
        GROUP BY a.id""")

    rows = cur.fetchall()
    insert_rows = []
    for r in rows:
        (aid, doc_id, num, content, chap_num, chap_title, sec_num, sec_title, tag_scores) = r
        tag_list = []
        primary = None
        if tag_scores:
            pairs = []
            for part in tag_scores.split(','):
                if ':' in part:
                    tag, score = part.split(':',1)
                    try:
                        score_val = float(score) if score else None
                    except ValueError:
                        score_val = None
                    pairs.append((tag, score_val))
            # sort for primary
            pairs.sort(key=lambda x: (x[1] is not None, x[1]), reverse=True)
            if pairs:
                primary = pairs[0][0]
            tag_list = [{'tag': t, 'score': s} for t, s in pairs]
        tag_json = json.dumps(tag_list, ensure_ascii=False)
        tag_vector_hint = ','.join([p['tag'] for p in tag_list])
        insert_rows.append((aid, doc_id, num, content, chap_num, chap_title, sec_num, sec_title, tag_json, primary, tag_vector_hint))

    cur.executemany("""
        INSERT INTO article_ingestion (article_id, document_id, article_number, content, chapter_number, chapter_title, section_number, section_title, tags, tag_primary, tag_vector_hint)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, insert_rows)
    conn.commit()

    # Create a view for lightweight joins
    cur.execute("DROP VIEW IF EXISTS vw_article_ingestion")
    cur.execute("""
        CREATE VIEW vw_article_ingestion AS
        SELECT i.article_id, i.document_id, i.article_number, i.tag_primary, i.tag_vector_hint,
               LENGTH(i.content) as content_len, i.chapter_number, i.section_number
        FROM article_ingestion i
    """)
    conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM article_ingestion")
    count = cur.fetchone()[0]
    print(f"Materialized rows: {count}")
    cur.execute("SELECT tag_primary, COUNT(*) FROM article_ingestion GROUP BY tag_primary ORDER BY COUNT(*) DESC LIMIT 10")
    print("Top primary tags:")
    for row in cur.fetchall():
        print(row)

    conn.close()
    print("✅ Ingestion table and view ready.")

if __name__ == '__main__':
    main()
