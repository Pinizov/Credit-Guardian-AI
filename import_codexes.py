"""
Import Bulgarian legal codes (Кодекс / Кодекси) from provided list (attachment excerpt).
Fetches actual code content from ciela.net and populates legal_documents and legal_articles tables.
Run: python import_codexes.py
"""

import time
import requests
import re
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

# Static list derived from attachment "ciela (1).csv" excerpt provided by user
CODEX_LIST = [
    ("КОДЕКС НА ТЪРГОВСКОТО КОРАБОПЛАВАНЕ (ЗАГЛ. ИЗМ. - ДВ, БР. 113 ОТ 2002 Г.)", "https://www.ciela.net/svobodna-zona-normativi/view/1590193665/kodeks-na-targovskoto-koraboplavane-(zagl-izm---dv-br-113-ot-2002-g)"),
    ("КОДЕКС ЗА СОЦИАЛНО ОСИГУРЯВАНЕ (ЗАГЛ. ИЗМ. - ДВ, БР. 67 ОТ 2003 Г.)", "https://www.ciela.net/svobodna-zona-normativi/view/1597824512/kodeks-za-sotsialno-osiguryavane-(zagl-izm---dv-br-67-ot-2003-g)"),
    ("НАКАЗАТЕЛЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/1589654529/nakazatelen-kodeks"),
    ("КОДЕКС НА ТРУДА", "https://www.ciela.net/svobodna-zona-normativi/view/1594373121/kodeks-na-truda"),
    ("КОДЕКС ЗА ПОВЕДЕНИЕ НА СЛУЖИТЕЛИТЕ В ДЪРЖАВНАТА АДМИНИСТРАЦИЯ ОТ 2004 Г.", "https://www.ciela.net/svobodna-zona-normativi/view/2135486505/kodeks-za-povedenie-na-sluzhitelite-v-darzhavnata-administratsiya-ot-2004-g"),
    ("КОДЕКС ЗА ЗАСТРАХОВАНЕТО ОТ 2005 Г.", "https://www.ciela.net/svobodna-zona-normativi/view/2135514184/kodeks-za-zastrahovaneto-ot-2005-g"),
    ("ДАНЪЧНО-ОСИГУРИТЕЛЕН ПРОЦЕСУАЛЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/2135514513/danachno-osiguritelen-protsesualen-kodeks"),
    ("АДМИНИСТРАТИВНОПРОЦЕСУАЛЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/2135521015/administrativnoprotsesualen-kodeks"),
    ("НАКАЗАТЕЛНО-ПРОЦЕСУАЛЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/2135512224/nakazatelno-protsesualen-kodeks"),
    ("ГРАЖДАНСКИ ПРОЦЕСУАЛЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/2135558368/grazhdanski-protsesualen-kodeks"),
    ("ЕТИЧЕН КОДЕКС НА АДВОКАТА", "https://www.ciela.net/svobodna-zona-normativi/view/2135507578/etichen-kodeks-na-advokata"),
    ("СЕМЕЕН КОДЕКС", "https://www.ciela.net/svobodna-zona-normativi/view/2135637484/semeen-kodeks"),
    ("КОДЕКС ЗА ПРОФЕСИОНАЛНА ЕТИКА НА МАГИСТЪР-ФАРМАЦЕВТА", "https://www.ciela.net/svobodna-zona-normativi/view/2135896487/kodeks-za-profesionalna-etika-na-magistar-farmatsevta"),
    ("КОДЕКС ЗА ПРОФЕСИОНАЛНА ЕТИКА НА ЛЕКАРИТЕ ПО ДЕНТАЛНА МЕДИЦИНА (ЗАГЛ. ИЗМ. - ДВ, БР. 18 ОТ 2017 Г.)", "https://www.ciela.net/svobodna-zona-normativi/view/2135896489/kodeks-za-profesionalna-etika-na-lekarite-po-dentalna-meditsina-(zagl-izm---dv-br-18-ot-2017-g)"),
    ("ИЗБОРЕН КОДЕКС ОТ 2011 Г.", "https://www.ciela.net/svobodna-zona-normativi/view/2135715515/izboren-kodeks-ot-2011-g"),
    ("КОДЕКС НА МЕЖДУНАРОДНОТО ЧАСТНО ПРАВО", "https://www.ciela.net/svobodna-zona-normativi/view/2135503651/kodeks-na-mezhdunarodnoto-chastno-pravo"),
]

class CodexImporter:
    def __init__(self, db_path='credit_guardian.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.conn.execute('PRAGMA synchronous=NORMAL;')
        self.cur = self.conn.cursor()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36'
        }

    def fetch_content(self, url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=35)
            resp.encoding = 'utf-8'
            if resp.status_code != 200:
                print(f"  ❌ HTTP {resp.status_code}")
                return None
            soup = BeautifulSoup(resp.content, 'html.parser')
            container = (soup.find('div', class_='law-content') or
                         soup.find('div', class_='document-content') or
                         soup.find('div', id='content') or
                         soup.find('article') or
                         soup.find('main') or
                         soup.find('body'))
            if not container:
                print("  ⚠️ No container found")
                return None
            text = container.get_text(separator='\n', strip=True)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            articles = self.extract_articles(text)
            return {
                'full_text': text[:50000],
                'articles': articles,
                'summary': text[:1000]
            }
        except requests.exceptions.Timeout:
            print("  ⏱️ Timeout")
            return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None

    def extract_articles(self, text):
        pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.'
        matches = list(re.finditer(pattern, text))
        articles = []
        for i, m in enumerate(matches):
            num = m.group(1)
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else min(start + 5000, len(text))
            segment = text[start:end].strip()
            if len(segment) > 50:
                articles.append({'number': num, 'text': segment})
        return articles

    def import_codex(self, title, url):
        print(f"\n📘 {title}")
        self.cur.execute("SELECT id FROM legal_documents WHERE title = ? LIMIT 1", (title,))
        row = self.cur.fetchone()
        if row:
            print("  ✅ Already exists (skip)")
            return row[0], False
        content = self.fetch_content(url)
        if not content:
            print("  ⚠️ Skipped - no content")
            return None, False
        now = datetime.utcnow()
        self.cur.execute(
            "INSERT INTO legal_documents (title, document_type, document_number, promulgation_date, effective_date, full_text, source_url, is_active, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (title, 'code', None, None, None, content['full_text'], url, 1, now, now)
        )
        doc_id = self.cur.lastrowid
        added_articles = 0
        for a in content['articles'][:150]:  # cap 150
            now_a = datetime.utcnow()
            self.cur.execute(
                "INSERT INTO legal_articles (document_id, article_number, title, content, chapter, section, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (doc_id, a['number'], f"Член {a['number']}", a['text'], None, None, now_a, now_a)
            )
            added_articles += 1
        self.conn.commit()
        print(f"  ✅ Imported doc ID {doc_id} with {added_articles} articles")
        return doc_id, True

    def import_all(self, delay=2.5):
        print("=" * 70)
        print("🇧🇬 BULGARIAN CODEX IMPORT")
        print("=" * 70)
        imported = 0
        for title, url in CODEX_LIST:
            try:
                _, created = self.import_codex(title, url)
                if created:
                    imported += 1
                time.sleep(delay)
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"  ❌ Unexpected error for {title}: {e}")
        # Totals
        self.cur.execute("SELECT COUNT(*) FROM legal_documents")
        total_docs = self.cur.fetchone()[0]
        self.cur.execute("SELECT COUNT(*) FROM legal_articles")
        total_articles = self.cur.fetchone()[0]
        print("\n" + "=" * 70)
        print("✅ CODEX IMPORT COMPLETE")
        print("=" * 70)
        print(f"Imported new codes: {imported}/{len(CODEX_LIST)}")
        print(f"Database now -> Documents: {total_docs} | Articles: {total_articles}")

    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    print("🚀 Starting Codex Import")
    importer = CodexImporter()
    try:
        importer.import_all()
    finally:
        importer.close()
    print("\n✅ Codex import finished.")
