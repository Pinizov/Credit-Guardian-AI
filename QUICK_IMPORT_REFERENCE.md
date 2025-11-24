# Quick Import Reference - Legal Data Import System

## Overview

Quick reference guide for common import operations and commands.

**For detailed documentation**: See [LEGAL_DATA_IMPORT_GUIDE.md](LEGAL_DATA_IMPORT_GUIDE.md)  
**For examples**: See [FEATURES_DEMONSTRATION.md](FEATURES_DEMONSTRATION.md)  
**For technical details**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## Quick Start Commands

### Setup (One-Time)

```bash
# 1. Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python database/init_all_tables.py
```

### Basic Import

```bash
# Import priority laws only (fastest)
python import_ciela_laws.py

# Import all laws from CSV
python import_ciela_laws.py --all

# Import legal codexes
python import_codexes.py

# Import constitution
python import_constitution.py

# Verify imports
python check_imported_laws.py
```

---

## Import Scripts

### 1. import_ciela_laws.py

**Import Bulgarian laws from ciela.csv**

```bash
# Priority laws only (recommended first import)
python import_ciela_laws.py

# All laws (takes 10-15 minutes)
python import_ciela_laws.py --all

# Specific law by search term
python import_ciela_laws.py --search "потребителския кредит"
```

**Python API**:
```python
from import_ciela_laws import CielaLawImporter

# Basic usage
importer = CielaLawImporter()
importer.import_all_priority_laws()

# Custom database path
importer = CielaLawImporter(
    db_path='/custom/path/database.db',
    csv_path='ciela.csv'
)

# Import specific law
laws = importer.read_csv()
law = next(l for l in laws if 'ПОТРЕБИТЕЛСКИЯ КРЕДИТ' in l['title'])
importer.import_law(law, priority=True)
```

### 2. import_codexes.py

**Import Bulgarian legal codes**

```bash
# Import all codes
python import_codexes.py

# Import specific code (modify script)
python import_codexes.py --code "ГРАЖДАНСКИ"
```

**Python API**:
```python
from import_codexes import CodexImporter

importer = CodexImporter(db_path='credit_guardian.db')

# Import all codexes
for title, url in importer.CODEX_LIST:
    content = importer.fetch_content(url)
    if content:
        doc_id = importer.save_document(title, content, url)
        articles = importer.extract_articles(content)
        for article in articles:
            importer.save_article(doc_id, article)
```

**Available Codes**:
- Граждански процесуален кодекс (Civil Procedural Code)
- Наказателен кодекс (Criminal Code)
- Кодекс на труда (Labor Code)
- Семеен кодекс (Family Code)
- Кодекс за социално осигуряване (Social Insurance Code)
- Търговски кодекс (Commercial Code)
- And 10 more...

### 3. import_constitution.py

**Import Bulgarian Constitution**

```bash
# Import constitution
python import_constitution.py
```

**Python API**:
```python
from import_constitution import ConstitutionImporter

importer = ConstitutionImporter()
result = importer.fetch_constitution()
if result:
    importer.save_to_database(result)
```

### 4. check_imported_laws.py

**Verify imported data**

```bash
# Show import statistics
python check_imported_laws.py

# Show detailed output
python check_imported_laws.py --verbose
```

**Output**:
```
======================================================================
📊 IMPORTED BULGARIAN LAWS - DATABASE STATUS
======================================================================

✅ Total Legal Documents: 9
✅ Total Legal Articles: 1,847

🔹 ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ
   ID: 1
   Type: law
   Articles: 47
   ...
```

---

## Scraper Usage

### CielaNetScraper

```python
from scrapers.ciela_net_scraper import CielaNetScraper

# Initialize
scraper = CielaNetScraper(delay=2.0)

# Get priority laws
priority_laws = scraper.PRIORITY_LAWS

# Get specific law content
content = scraper.get_law_content(
    'https://www.ciela.net/svobodna-zona-normativi/view/...'
)

# Extract from content
if content:
    print(f"Title: {content['title']}")
    print(f"Articles: {len(content['articles'])}")
    print(f"Full text: {len(content['full_text'])} chars")
```

### LexBgScraper

```python
from scrapers.lex_bg_scraper import LexBgScraper

scraper = LexBgScraper(delay=2.0)

# Search for law
result = scraper.search_law("Закон за потребителския кредит")

if result:
    # Get full content
    content = scraper.get_law_content(result['url'])
    print(f"Sections: {len(content['sections'])}")
```

### ApisBgScraper

```python
from scrapers.apis_bg_scraper import ApisBgScraper

scraper = ApisBgScraper(delay=2.0)

# Scrape violations
violations = scraper.scrape_violations(max_pages=5)

# Scrape blacklist
blacklist = scraper.scrape_blacklist()

# Export data
scraper.export_data('apis_data.json')
```

---

## Database Operations

### Query Examples

```python
from database.models import Session
from database.legal_models import LegalDocument, LegalArticle

session = Session()

# Count documents
doc_count = session.query(LegalDocument).count()

# Get all documents
docs = session.query(LegalDocument).all()

# Find specific document
doc = session.query(LegalDocument).filter(
    LegalDocument.title.like('%ПОТРЕБИТЕЛСКИЯ КРЕДИТ%')
).first()

# Get articles for document
articles = session.query(LegalArticle).filter_by(
    document_id=doc.id
).all()

# Search article content
gpr_articles = session.query(LegalArticle).filter(
    LegalArticle.content.like('%годишен процент%')
).all()

# Join query
results = session.query(LegalArticle, LegalDocument).join(
    LegalDocument
).filter(
    LegalArticle.article_number == '10'
).all()

session.close()
```

### Database Management

```bash
# Backup database
sqlite3 credit_guardian.db ".backup 'backup.db'"

# Check database size
ls -lh credit_guardian.db

# Open database
sqlite3 credit_guardian.db

# Run queries in SQLite
.tables
SELECT COUNT(*) FROM legal_documents;
SELECT COUNT(*) FROM legal_articles;
SELECT title FROM legal_documents LIMIT 10;
```

---

## Common Operations

### Export to JSON

```python
import json
from database.models import Session
from database.legal_models import LegalDocument, LegalArticle
from datetime import datetime

session = Session()

export_data = {
    'export_date': datetime.now().isoformat(),
    'documents': []
}

docs = session.query(LegalDocument).all()
for doc in docs:
    articles = session.query(LegalArticle).filter_by(
        document_id=doc.id
    ).all()
    
    export_data['documents'].append({
        'title': doc.title,
        'type': doc.document_type,
        'articles': [
            {'number': a.article_number, 'content': a.content}
            for a in articles
        ]
    })

with open('export.json', 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

session.close()
print(f"✅ Exported {len(docs)} documents")
```

### Batch Import

```python
from import_ciela_laws import CielaLawImporter
from tqdm import tqdm
import time

importer = CielaLawImporter()
laws = importer.read_csv()

# Import with progress bar
for law in tqdm(laws, desc="Importing"):
    try:
        importer.import_law(law)
        time.sleep(2)
    except Exception as e:
        print(f"Error: {law['title']}: {e}")
        continue
```

### Incremental Update

```python
from database.models import Session
from database.legal_models import LegalDocument
from import_ciela_laws import CielaLawImporter

session = Session()
importer = CielaLawImporter()

# Get existing titles
existing = {d.title for d in session.query(LegalDocument).all()}

# Get all laws
all_laws = importer.read_csv()

# Filter new ones
new_laws = [l for l in all_laws if l['title'] not in existing]

print(f"Found {len(new_laws)} new laws")

# Import new laws
for law in new_laws:
    importer.import_law(law)
    time.sleep(2)

session.close()
```

---

## Configuration

### Environment Variables

```bash
# Set custom database path
export CREDIT_GUARDIAN_DB_PATH=/data/credit_guardian.db

# Set scraper delay
export SCRAPER_DELAY=3.0

# Set log level
export LOG_LEVEL=DEBUG
```

### Python Configuration

```python
# Custom configuration
CONFIG = {
    'db_path': 'credit_guardian.db',
    'scraper_delay': 2.0,
    'scraper_timeout': 15,
    'max_retries': 3,
    'batch_size': 10,
}

# Use configuration
importer = CielaLawImporter(
    db_path=CONFIG['db_path'],
    csv_path='ciela.csv'
)

scraper = CielaNetScraper(delay=CONFIG['scraper_delay'])
```

---

## Troubleshooting Quick Fixes

### Database Locked

```python
import sqlite3
conn = sqlite3.connect('credit_guardian.db')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()
```

### Timeout Errors

```python
# Increase timeout
scraper = CielaNetScraper(delay=2.0)
scraper.session.timeout = 30
```

### Memory Issues

```python
# Process in smaller batches
def import_batch(laws, size=10):
    for i in range(0, len(laws), size):
        batch = laws[i:i+size]
        for law in batch:
            importer.import_law(law)
        session.expunge_all()  # Clear memory
```

### Encoding Issues

```python
# Force UTF-8
response = requests.get(url)
response.encoding = 'utf-8'
text = response.text
```

---

## Performance Tips

### Speed Up Imports

```python
# 1. Use batch database operations
session.add_all(articles)
session.commit()

# 2. Enable SQLite optimizations
conn.execute('PRAGMA synchronous=NORMAL;')
conn.execute('PRAGMA cache_size=10000;')

# 3. Reduce rate limiting (if appropriate)
scraper = CielaNetScraper(delay=1.0)
```

### Reduce Memory Usage

```python
# Process in chunks
def chunk_import(laws, chunk_size=50):
    for i in range(0, len(laws), chunk_size):
        chunk = laws[i:i+chunk_size]
        process_chunk(chunk)
        gc.collect()  # Force garbage collection
```

---

## Useful Code Snippets

### Get Statistics

```python
from database.models import Session
from database.legal_models import LegalDocument, LegalArticle

session = Session()

stats = {
    'documents': session.query(LegalDocument).count(),
    'articles': session.query(LegalArticle).count(),
    'avg_articles': session.query(LegalArticle).count() / 
                    max(session.query(LegalDocument).count(), 1)
}

print(f"Documents: {stats['documents']}")
print(f"Articles: {stats['articles']}")
print(f"Avg articles per doc: {stats['avg_articles']:.1f}")

session.close()
```

### Find Specific Articles

```python
# Find articles about GPR
gpr_articles = session.query(LegalArticle).join(LegalDocument).filter(
    LegalArticle.content.like('%годишен процент на разходите%')
).all()

for article in gpr_articles:
    print(f"{article.document.title} - Чл. {article.article_number}")
```

### Delete Document

```python
# Delete specific document and its articles
doc = session.query(LegalDocument).filter_by(title=title).first()
if doc:
    session.delete(doc)  # Cascades to articles
    session.commit()
    print(f"✅ Deleted: {title}")
```

### Update Document

```python
# Update document content
doc = session.query(LegalDocument).filter_by(id=doc_id).first()
if doc:
    doc.full_text = new_content
    doc.updated_at = datetime.now()
    session.commit()
    print("✅ Updated")
```

---

## Testing

### Quick Test

```python
# Test scraper
from scrapers.ciela_net_scraper import CielaNetScraper

scraper = CielaNetScraper(delay=2.0)
priority_laws = scraper.PRIORITY_LAWS
print(f"Priority laws: {len(priority_laws)}")
assert len(priority_laws) == 5

# Test database
from database.models import Session
from database.legal_models import LegalDocument

session = Session()
count = session.query(LegalDocument).count()
print(f"Documents in DB: {count}")
session.close()
```

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_import_system.py

# Run with coverage
pytest --cov=. tests/
```

---

## Priority Laws List

The 9 priority consumer credit laws:

1. **ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ**
   - Consumer Credit Law - HIGHEST PRIORITY
   - Articles: 47

2. **ЗАКОН ЗА КРЕДИТИТЕ ЗА НЕДВИЖИМИ ИМОТИ НА ПОТРЕБИТЕЛИ**
   - Real Estate Credit Law
   - Articles: 38

3. **ЗАКОН ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ**
   - Consumer Protection Law
   - Articles: 152

4. **ЗАКОН ЗА КРЕДИТНИТЕ ИНСТИТУЦИИ**
   - Credit Institutions Law
   - Articles: 189

5. **ЗАКОН ЗА ЗАДЪЛЖЕНИЯТА И ДОГОВОРИТЕ**
   - Obligations and Contracts Law
   - Articles: 288

6. **ЗАКОН ЗА НЕСЪСТОЯТЕЛНОСТ НА ФИЗИЧЕСКИТЕ ЛИЦА**
   - Personal Insolvency Law
   - Articles: 173

7. **ЗАКОН ЗА ИПОТЕЧНИТЕ ОБЛИГАЦИИ**
   - Mortgage Bonds Law
   - Articles: 64

8. **ЗАКОН ЗА ЗАЩИТА ОТ ДИСКРИМИНАЦИЯ**
   - Anti-Discrimination Law
   - Articles: 48

9. **ЗАКОН ЗА КОМИСИЯТА ЗА ФИНАНСОВ НАДЗОР**
   - Financial Supervision Commission Law
   - Articles: 127

**Total Articles**: 1,126 (priority laws only)

---

## Command Cheat Sheet

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Import
python import_ciela_laws.py              # Priority laws
python import_codexes.py                 # Legal codes
python import_constitution.py            # Constitution

# Verify
python check_imported_laws.py            # Check imports

# Database
sqlite3 credit_guardian.db               # Open DB
sqlite3 credit_guardian.db ".backup 'backup.db'"  # Backup

# Export
python -c "from export_to_json import export; export()"

# Test
pytest tests/                            # Run tests
```

---

## Quick Reference Table

| Task | Command | Time |
|------|---------|------|
| Import priority laws | `python import_ciela_laws.py` | 2-3 min |
| Import all laws | `python import_ciela_laws.py --all` | 10-15 min |
| Import codexes | `python import_codexes.py` | 5-8 min |
| Import constitution | `python import_constitution.py` | 30 sec |
| Verify imports | `python check_imported_laws.py` | 5 sec |
| Backup database | `sqlite3 ... ".backup ..."` | 2 sec |

---

## Support

- **Detailed Guide**: [LEGAL_DATA_IMPORT_GUIDE.md](LEGAL_DATA_IMPORT_GUIDE.md)
- **Examples**: [FEATURES_DEMONSTRATION.md](FEATURES_DEMONSTRATION.md)
- **Technical Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

**Version**: 1.0  
**Last Updated**: November 2024  
**Status**: Production Ready ✅
