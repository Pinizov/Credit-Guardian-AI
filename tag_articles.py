"""Assign heuristic thematic tags to legal articles based on keyword matching."""
import re, sqlite3, time
from datetime import datetime

TAG_KEYWORDS = {
    'labor': ['труд', 'работник', 'работодател', 'заплата', 'отпуск'],
    'social_security': ['осигуряване', 'пенсия', 'инвалидност', 'осигурителен'],
    'tax_procedure': ['данък', 'данъчен', 'осигурителен', 'ревизия', 'декларация'],
    'civil_procedure': ['иск', 'заповед', 'съд', 'дело', 'процедура'],
    'penal_substantive': ['престъпление', 'наказание', 'лишаване от свобода', 'глоба'],
    'criminal_procedure': ['досъдебно', 'обвиняем', 'разследване', 'съдебно производство'],
    'family': ['брак', 'съпруг', 'родител', 'осиновяване', 'семейство'],
    'maritime': ['кораб', 'плаване', 'морско', 'пристанище'],
    'private_international_law': ['приложимо право', 'колизия', 'международно частно', 'компетентност'],
    'insurance': ['застраховка', 'застраховател', 'премия', 'застрахован'],
    'elections': ['избор', 'кампания', 'гласуване', 'секция'],
    'ethics_lawyer': ['адвокат', 'етичен', 'поведение'],
    'ethics_medical': ['дентална', 'фармацевт', 'медицинска', 'етика'],
}

MIN_MATCHES = 1  # at least one keyword occurrence

NORMALIZE_MAP = {
    'й': 'и',
}


def normalize(text: str) -> str:
    t = text.lower()
    for k,v in NORMALIZE_MAP.items():
        t = t.replace(k,v)
    return t


def tag_articles(batch_size: int = 1000):
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS legal_article_tags (id INTEGER PRIMARY KEY AUTOINCREMENT, article_id INTEGER NOT NULL, tag TEXT NOT NULL, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_tag_article_id ON legal_article_tags(article_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_tag_value ON legal_article_tags(tag)")
    cur.execute("SELECT COUNT(*) FROM legal_article_tags")
    existing = cur.fetchone()[0]
    print(f"Existing tags: {existing}")

    cur.execute("SELECT id, content FROM legal_articles")
    rows = cur.fetchall()
    total = len(rows)
    print(f"Scanning articles: {total}")

    now = datetime.utcnow()
    tagged = 0
    for i, (article_id, content) in enumerate(rows, 1):
        text = normalize(content[:4000])  # limit for speed
        added_tags = []
        for tag, keywords in TAG_KEYWORDS.items():
            hits = 0
            for kw in keywords:
                # word boundary tolerant match
                if re.search(r"\b" + re.escape(kw) + r"\b", text):
                    hits += 1
            if hits >= MIN_MATCHES:
                added_tags.append(tag)
        for t in added_tags:
            cur.execute("INSERT INTO legal_article_tags (article_id, tag, created_at, updated_at) VALUES (?,?,?,?)", (article_id, t, now, now))
        tagged += len(added_tags)
        if i % batch_size == 0:
            conn.commit()
            print(f"  Progress {i}/{total} (tags added {tagged})")
            time.sleep(0.2)
    conn.commit()

    cur.execute("SELECT tag, COUNT(*) FROM legal_article_tags GROUP BY tag ORDER BY COUNT(*) DESC")
    dist = cur.fetchall()
    print("\nTag distribution:")
    for tag, cnt in dist:
        print(f"  {tag}: {cnt}")
    print(f"\nTotal tags added: {tagged}")
    conn.close()

if __name__ == '__main__':
    tag_articles()
