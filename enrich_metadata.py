"""Reparse high-value Bulgarian codes to enrich chapters/sections and lift article caps."""
import re, time, requests, sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

HIGH_VALUE_CODES = [
    "КОДЕКС НА ТРУДА",
    "КОДЕКС ЗА СОЦИАЛНО ОСИГУРЯВАНЕ",
    "ДАНЪЧНО-ОСИГУРИТЕЛЕН ПРОЦЕСУАЛЕН КОДЕКС",
    "ГРАЖДАНСКИ ПРОЦЕСУАЛЕН КОДЕКС",
    "НАКАЗАТЕЛЕН КОДЕКС",
    "АДМИНИСТРАТИВНОПРОЦЕСУАЛЕН КОДЕКС",
    "НАКАЗАТЕЛНО-ПРОЦЕСУАЛЕН КОДЕКС",
    "СЕМЕЕН КОДЕКС",
    "КОДЕКС НА ТЪРГОВСКОТО КОРАБОПЛАВАНЕ",
    "КОДЕКС НА МЕЖДУНАРОДНОТО ЧАСТНО ПРАВО",
    "КОДЕКС ЗА ЗАСТРАХОВАНЕТО",
]

UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'}

CHAPTER_PATTERNS = [
    ("chapter", re.compile(r"(^|\n)(ЧАСТ\s+[IVXLC\d]+(?:\s*[-–—]\s*[^\n]+)?)", re.IGNORECASE)),
    ("chapter", re.compile(r"(^|\n)(ГЛАВА\s+[IVXLC\d]+(?:\s*[-–—]\s*[^\n]+)?)", re.IGNORECASE)),
]
SECTION_PATTERNS = [
    ("section", re.compile(r"(^|\n)(РАЗДЕЛ\s+[IVXLC\d]+(?:\s*[-–—]\s*[^\n]+)?)", re.IGNORECASE)),
    ("section", re.compile(r"(^|\n)(ПОДРАЗДЕЛ\s+[IVXLC\d]+(?:\s*[-–—]\s*[^\n]+)?)", re.IGNORECASE)),
]
ARTICLE_PATTERN = re.compile(r"(^|\n)(?:Чл\.|Член)\s*(\d+[а-я]?)\.\s*", re.IGNORECASE)

MAX_ARTICLE_LEN = 15000  # lift cap


def fetch(url: str):
    try:
        r = requests.get(url, headers=UA, timeout=40)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.content, 'html.parser')
        c = soup.find('div', class_='law-content') or soup.find('div', class_='document-content') or soup.find('div', id='content') or soup.find('article') or soup.find('main') or soup.find('body')
        if not c:
            return None
        text = c.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text
    except Exception:
        return None


def parse_articles(full_text: str):
    # Precompute heading positions
    headings = []
    for kind, pat in CHAPTER_PATTERNS + SECTION_PATTERNS:
        for m in pat.finditer(full_text):
            headings.append((m.start(), kind, m.group(2)))
    headings.sort(key=lambda x: x[0])

    # Build list of article matches
    matches = list(ARTICLE_PATTERN.finditer(full_text))
    articles = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else min(start + MAX_ARTICLE_LEN, len(full_text))
        segment = full_text[start:end].strip()
        if len(segment) < 50:
            continue
        art_num = m.group(2)
        # Find nearest preceding chapter/section
        chapter = section = None
        for pos, kind, text in reversed([h for h in headings if h[0] <= start]):
            if kind == 'chapter' and chapter is None:
                chapter = text
            if kind == 'section' and section is None:
                section = text
            if chapter and section:
                break
        articles.append((art_num, segment, chapter, section))
    return articles


def enrich():
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, source_url, full_text FROM legal_documents WHERE document_type='code'")
    docs = cur.fetchall()
    total_new = 0
    for doc_id, title, url, stored_text in docs:
        if not any(title.startswith(hv) for hv in HIGH_VALUE_CODES):
            continue
        print(f"\n🔄 Reparse {title[:60]}")
        full_text = fetch(url) or stored_text
        if not full_text:
            print("  ⚠️ No text")
            continue
        articles = parse_articles(full_text)
        if not articles:
            print("  ⚠️ No articles parsed")
            continue
        # Replace articles
        cur.execute("DELETE FROM legal_articles WHERE document_id=?", (doc_id,))
        now = datetime.utcnow()
        added = 0
        for num, content, chapter, section in articles:
            cur.execute("INSERT INTO legal_articles (document_id, article_number, title, content, chapter, section, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                        (doc_id, num, f"Член {num}", content[:MAX_ARTICLE_LEN], chapter, section, now, now))
            added += 1
        conn.commit()
        print(f"  ✅ Articles: {added}")
        total_new += added
        time.sleep(1.2)
    cur.execute("SELECT COUNT(*) FROM legal_articles")
    print(f"\n📊 Total articles after enrichment: {cur.fetchone()[0]}")
    conn.close()
    print("\n✅ Enrichment complete")

if __name__ == '__main__':
    enrich()
