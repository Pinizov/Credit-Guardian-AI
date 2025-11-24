"""Advanced Bulgarian legal article tagging with heuristic stemming and TF-IDF scoring.
Rebuilds tag table with scores.
"""
import re, math, sqlite3
from collections import Counter, defaultdict
from datetime import datetime

RAW_TAG_KEYWORDS = {
    'labor': ['труд', 'работник', 'работодател', 'възнаграждение', 'заплата', 'отпуск'],
    'social_security': ['осигуряване', 'пенсия', 'инвалидност', 'осигурителен', 'болничен'],
    'tax_procedure': ['данък', 'данъчен', 'декларация', 'ревизия', 'обжалване'],
    'civil_procedure': ['иск', 'заповед', 'съд', 'дело', 'процедура', 'жалба'],
    'penal_substantive': ['престъпление', 'наказание', 'лишаване', 'свобода', 'глоба', 'умисъл'],
    'criminal_procedure': ['досъдебно', 'обвиняем', 'разследване', 'съдебно', 'производство', 'арест'],
    'family': ['брак', 'съпруг', 'родител', 'осиновяване', 'семейство', 'издръжка'],
    'maritime': ['кораб', 'плаване', 'морско', 'пристанище', 'капитан'],
    'private_international_law': ['приложимо', 'колизия', 'международно', 'частно', 'компетентност'],
    'insurance': ['застраховка', 'застраховател', 'премия', 'застрахован', 'щета'],
    'elections': ['избор', 'кампания', 'гласуване', 'секция', 'мандат'],
    'ethics_lawyer': ['адвокат', 'етичен', 'поведение', 'достойно'],
    'ethics_medical': ['дентална', 'фармацевт', 'медицинска', 'етика'],
}

# Simple Bulgarian stemming heuristic (rule-based, approximate)
SUFFIXES = [
    'ите','ият','ията','овете','евете','ове','еве','ия','ът','ят','та','то','те','ените','ения','ени','ността','ност','чески','ов','ев','ите','ки','ски','ско','ни','на','ен','ий','ия','а','и'
]

def stem(word: str) -> str:
    w = word.lower()
    w = w.replace('й','и')
    # strip non-letter edges
    w = re.sub(r'^[^а-я]+|[^а-я]+$', '', w)
    for suf in sorted(SUFFIXES, key=len, reverse=True):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]
            break
    return w

TOKEN_PATTERN = re.compile(r'[а-яА-Я]+')

def tokenize(text: str):
    return [stem(t) for t in TOKEN_PATTERN.findall(text.lower())]

def build_tag_vocab():
    vocab = {}
    for tag, words in RAW_TAG_KEYWORDS.items():
        vocab[tag] = {stem(w) for w in words}
    return vocab

def main():
    conn = sqlite3.connect('credit_guardian.db')
    cur = conn.cursor()

    # Load articles
    cur.execute("SELECT id, content FROM legal_articles")
    articles = cur.fetchall()
    print(f"Loaded articles: {len(articles)}")

    tag_vocab = build_tag_vocab()

    # Compute DF for stemmed tokens
    df_counter = Counter()
    article_tokens = {}
    for aid, content in articles:
        toks = tokenize(content[:12000])  # limit for performance
        article_tokens[aid] = toks
        unique = set(toks)
        for u in unique:
            df_counter[u] += 1
    N = len(articles)

    # Precompute keyword idf for each tag's vocabulary (idf of token if appears)
    tag_idf = defaultdict(dict)
    for tag, vocab in tag_vocab.items():
        for token in vocab:
            df = df_counter.get(token, 0)
            # smooth idf
            idf = math.log((N + 1) / (df + 1)) + 1
            tag_idf[tag][token] = idf

    print("Scoring tags...")
    tag_scores = defaultdict(list)  # article_id -> list[(tag, score)]

    for aid, toks in article_tokens.items():
        tf = Counter(toks)
        for tag, vocab in tag_vocab.items():
            score = 0.0
            for token in vocab:
                if token in tf:
                    # augmented frequency
                    freq = 1 + math.log(tf[token])
                    score += freq * tag_idf[tag][token]
            if score > 0:
                tag_scores[aid].append((tag, score))
        # keep top 5 tags
        tag_scores[aid].sort(key=lambda x: x[1], reverse=True)
        tag_scores[aid] = tag_scores[aid][:5]

    # Rebuild tag table
    print("Rebuilding tag table with scores...")
    cur.execute("DELETE FROM legal_article_tags")
    conn.commit()

    now = datetime.utcnow()
    inserted = 0
    for aid, pairs in tag_scores.items():
        for tag, score in pairs:
            cur.execute("INSERT INTO legal_article_tags (article_id, tag, score, created_at, updated_at) VALUES (?,?,?,?,?)",
                        (aid, tag, score, now, now))
            inserted += 1
    conn.commit()
    print(f"Inserted tag rows: {inserted}")

    # Distribution report
    cur.execute("SELECT tag, COUNT(*) c FROM legal_article_tags GROUP BY tag ORDER BY c DESC")
    for tag, c in cur.fetchall():
        print(f"  {tag}: {c}")

    # Sample scores
    cur.execute("SELECT article_id, tag, score FROM legal_article_tags ORDER BY score DESC LIMIT 10")
    print("\nTop scored tags samples:")
    for row in cur.fetchall():
        print(row)

    conn.close()
    print("✅ Advanced tagging complete.")

if __name__ == '__main__':
    main()
