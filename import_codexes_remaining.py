"""Import remaining Bulgarian codes not yet in database."""
import time, re, requests, sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

REMAINING_CODES = [
    ("НАКАЗАТЕЛНО-ПРОЦЕСУАЛЕН КОДЕКС","https://www.ciela.net/svobodna-zona-normativi/view/2135512224/nakazatelno-protsesualen-kodeks"),
    ("ГРАЖДАНСКИ ПРОЦЕСУАЛЕН КОДЕКС","https://www.ciela.net/svobodna-zona-normativi/view/2135558368/grazhdanski-protsesualen-kodeks"),
    ("ЕТИЧЕН КОДЕКС НА АДВОКАТА","https://www.ciela.net/svobodna-zona-normativi/view/2135507578/etichen-kodeks-na-advokata"),
    ("СЕМЕЕН КОДЕКС","https://www.ciela.net/svobodna-zona-normativi/view/2135637484/semeen-kodeks"),
    ("КОДЕКС ЗА ПРОФЕСИОНАЛНА ЕТИКА НА МАГИСТЪР-ФАРМАЦЕВТА","https://www.ciela.net/svobodna-zona-normativi/view/2135896487/kodeks-za-profesionalna-etika-na-magistar-farmatsevta"),
    ("КОДЕКС ЗА ПРОФЕСИОНАЛНА ЕТИКА НА ЛЕКАРИТЕ ПО ДЕНТАЛНА МЕДИЦИНА (ЗАГЛ. ИЗМ. - ДВ, БР. 18 ОТ 2017 Г.)","https://www.ciela.net/svobodna-zona-normativi/view/2135896489/kodeks-za-profesionalna-etika-na-lekarite-po-dentalna-meditsina-(zagl-izm---dv-br-18-ot-2017-g)"),
    ("ИЗБОРЕН КОДЕКС ОТ 2011 Г.","https://www.ciela.net/svobodna-zona-normativi/view/2135715515/izboren-kodeks-ot-2011-g"),
    ("КОДЕКС НА МЕЖДУНАРОДНОТО ЧАСТНО ПРАВО","https://www.ciela.net/svobodna-zona-normativi/view/2135503651/kodeks-na-mezhdunarodnoto-chastno-pravo"),
]

UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36'}

def fetch(url):
    try:
        r = requests.get(url, headers=UA, timeout=35)
        r.encoding='utf-8'
        if r.status_code!=200:
            print(f"  ❌ HTTP {r.status_code}")
            return None
        soup = BeautifulSoup(r.content,'html.parser')
        c = soup.find('div',class_='law-content') or soup.find('div',class_='document-content') or soup.find('div',id='content') or soup.find('article') or soup.find('main') or soup.find('body')
        if not c:
            return None
        text = c.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\s*\n','\n\n',text)
        text = re.sub(r' +',' ',text)
        arts = []
        pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.'
        ms = list(re.finditer(pattern,text))
        for i,m in enumerate(ms):
            start=m.start(); end= ms[i+1].start() if i+1 < len(ms) else min(start+5000,len(text))
            seg=text[start:end].strip()
            if len(seg)>50:
                arts.append((m.group(1), seg))
        return text[:50000], arts
    except Exception as e:
        print(f"  ❌ Error {e}")
        return None

def main():
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()
    imported=0
    for title,url in REMAINING_CODES:
        cur.execute("SELECT id FROM legal_documents WHERE title=? LIMIT 1",(title,))
        if cur.fetchone():
            print(f"✅ Skip existing: {title[:40]}")
            continue
        print(f"\n📘 {title}")
        data = fetch(url)
        if not data:
            print("  ⚠️ Skip no content")
            continue
        full_text, articles = data
        now = datetime.utcnow()
        cur.execute("INSERT INTO legal_documents (title, document_type, document_number, promulgation_date, effective_date, full_text, source_url, is_active, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (title,'code',None,None,None,full_text,url,1,now,now))
        doc_id = cur.lastrowid
        added=0
        for num, text in articles[:150]:
            cur.execute("INSERT INTO legal_articles (document_id, article_number, title, content, chapter, section, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                        (doc_id,num,f"Член {num}",text,None,None,now,now))
            added+=1
        conn.commit()
        imported+=1
        print(f"  ✅ Imported ID {doc_id} articles {added}")
        time.sleep(1.5)
    cur.execute("SELECT COUNT(*) FROM legal_documents WHERE document_type='code'")
    print("\nCode documents total:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM legal_articles")
    print("Total articles:", cur.fetchone()[0])
    conn.close()
    print(f"\n✅ Remaining codes imported: {imported}")

if __name__=='__main__':
    main()
