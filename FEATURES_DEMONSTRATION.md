# Legal Data Import System - Features Demonstration

## Overview

This document showcases all implemented features of the Credit Guardian AI Legal Data Import System with practical examples, code snippets, and usage scenarios.

## Table of Contents

1. [Web Scrapers](#web-scrapers)
2. [Legal Document Import](#legal-document-import)
3. [Article Extraction](#article-extraction)
4. [Database Population](#database-population)
5. [Data Verification](#data-verification)
6. [Advanced Features](#advanced-features)

---

## Web Scrapers

The system includes three specialized web scrapers for Bulgarian legal data sources.

### 1. Ciela.net Scraper

Scrapes legal documents from ciela.net's Svobodna Zona (Free Zone).

**Features:**
- Dynamic content handling
- Rate limiting and polite scraping
- Priority law identification
- Article-level extraction

**Example Usage:**

```python
from scrapers.ciela_net_scraper import CielaNetScraper

# Initialize scraper with 2-second delay between requests
scraper = CielaNetScraper(delay=2.0)

# Get priority consumer credit laws
priority_laws = scraper.PRIORITY_LAWS

# Fetch a specific law
law_content = scraper.get_law_content(
    'https://www.ciela.net/svobodna-zona-normativi/view/2135540562/...'
)

if law_content:
    print(f"Title: {law_content['title']}")
    print(f"Articles found: {len(law_content['articles'])}")
    print(f"Full text length: {len(law_content['full_text'])} characters")
```

**Output Example:**
```
Title: Закон за потребителския кредит
Articles found: 47
Full text length: 28,543 characters
```

### 2. Lex.bg Scraper

Scrapes from the official Bulgarian government legal database.

**Features:**
- Government-endorsed source
- Search functionality by law name
- Comprehensive legal metadata
- Multiple document format support

**Example Usage:**

```python
from scrapers.lex_bg_scraper import LexBgScraper

scraper = LexBgScraper(delay=2.0)

# Search for Consumer Credit Law
result = scraper.search_law("Закон за потребителския кредит")

if result:
    print(f"Found: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Document ID: {result['doc_id']}")
    
    # Fetch full content
    content = scraper.get_law_content(result['url'])
    print(f"Content sections: {len(content['sections'])}")
```

**Output Example:**
```
Found: Закон за потребителския кредит
URL: https://www.lex.bg/laws/ldoc/2135540562
Document ID: 2135540562
Content sections: 8
```

### 3. APIS.bg Scraper

Scrapes consumer protection violation records and enforcement actions.

**Features:**
- Violation record extraction
- Company blacklist monitoring
- Administrative decision tracking
- Penalty information collection

**Example Usage:**

```python
from scrapers.apis_bg_scraper import ApisBgScraper

scraper = ApisBgScraper(delay=2.0)

# Scrape violation records
violations = scraper.scrape_violations(max_pages=5)

print(f"Total violations found: {len(violations)}")

# Display sample violation
if violations:
    violation = violations[0]
    print(f"\nCompany: {violation['company_name']}")
    print(f"Violation: {violation['violation_type']}")
    print(f"Penalty: {violation['penalty_amount']} BGN")
    print(f"Date: {violation['date']}")
```

**Output Example:**
```
Total violations found: 127

Company: ABC Finance Ltd
Violation: Неразкриване на ГПР в договора
Penalty: 5000 BGN
Date: 2024-03-15
```

---

## Legal Document Import

### Import from Ciela.net CSV

Import Bulgarian laws using a pre-compiled CSV list.

**Features:**
- Priority-based import (consumer credit laws first)
- Duplicate detection
- Automatic article extraction
- Progress tracking

**Example Usage:**

```python
from import_ciela_laws import CielaLawImporter

# Initialize importer
importer = CielaLawImporter(
    db_path='credit_guardian.db',
    csv_path='ciela.csv'
)

# Read laws from CSV
laws = importer.read_csv()
print(f"Found {len(laws)} laws in CSV")

# Import priority laws first
for priority_law in importer.PRIORITY_LAWS:
    matching_laws = [l for l in laws if priority_law in l['title']]
    for law in matching_laws:
        importer.import_law(law, priority=True)
        time.sleep(2)  # Rate limiting

# Import remaining laws
for law in laws:
    if not any(p in law['title'] for p in importer.PRIORITY_LAWS):
        importer.import_law(law, priority=False)
        time.sleep(2)
```

**Output Example:**
```
Found 147 laws in CSV

🔥 ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ
  Fetching: https://www.ciela.net/...
  ✅ Extracted 47 articles
  ✅ Saved to database (ID: 1)

🔥 ЗАКОН ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ
  Fetching: https://www.ciela.net/...
  ✅ Extracted 152 articles
  ✅ Saved to database (ID: 2)
```

### Import Legal Codexes

Import major Bulgarian legal codes (Criminal, Civil, Labor, etc.).

**Example Usage:**

```python
from import_codexes import CodexImporter

importer = CodexImporter(db_path='credit_guardian.db')

# Import all codexes from predefined list
for title, url in importer.CODEX_LIST:
    print(f"\n📚 Importing: {title}")
    
    content = importer.fetch_content(url)
    if content:
        articles = importer.extract_articles(content)
        doc_id = importer.save_document(title, content, url)
        
        for article in articles:
            importer.save_article(doc_id, article)
        
        print(f"  ✅ Saved {len(articles)} articles")
    
    time.sleep(3)  # Rate limiting
```

**Output Example:**
```
📚 Importing: ГРАЖДАНСКИ ПРОЦЕСУАЛЕН КОДЕКС
  ✅ Saved 632 articles

📚 Importing: НАКАЗАТЕЛЕН КОДЕКС
  ✅ Saved 412 articles

📚 Importing: КОДЕКС НА ТРУДА
  ✅ Saved 358 articles
```

### Import Bulgarian Constitution

Special import for the Constitution of Bulgaria.

**Example Usage:**

```python
from import_constitution import ConstitutionImporter

importer = ConstitutionImporter(db_path='credit_guardian.db')

# Fetch and import constitution
result = importer.fetch_constitution()

if result:
    print(f"Title: {result['title']}")
    print(f"Articles: {len(result['articles'])}")
    print(f"Chapters: {result['chapter_count']}")
    
    # Save to database
    importer.save_to_database(result)
    print("✅ Constitution imported successfully")
```

**Output Example:**
```
Title: Конституция на Република България
Articles: 169
Chapters: 11
✅ Constitution imported successfully
```

---

## Article Extraction

The system automatically extracts individual articles from legal documents.

### Bulgarian Article Pattern Recognition

**Supported Patterns:**
- `Чл. 1.` - Article 1
- `Член 1.` - Member 1 (formal)
- `Чл. 1а.` - Article 1a (amendments)
- `§ 1.` - Paragraph 1

**Example:**

```python
import re

def extract_articles(text):
    """Extract articles from Bulgarian legal text."""
    articles = []
    
    # Pattern for Bulgarian law articles
    pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.'
    matches = list(re.finditer(pattern, text))
    
    for i, match in enumerate(matches):
        article_number = match.group(1)
        start = match.start()
        
        # Get text until next article
        if i < len(matches) - 1:
            end = matches[i + 1].start()
        else:
            end = min(start + 5000, len(text))
        
        article_text = text[start:end].strip()
        
        if len(article_text) > 50:
            articles.append({
                'number': article_number,
                'text': article_text
            })
    
    return articles

# Example usage
law_text = """
Чл. 10. Кредиторът е длъжен да посочи годишния процент на разходите...

Чл. 11. Кредиторът не може да променя лихвения процент едностранно...

Чл. 12. Всички такси и комисионни трябва да са разкрити в договора...
"""

articles = extract_articles(law_text)
print(f"Extracted {len(articles)} articles")
for article in articles:
    print(f"  • Article {article['number']}: {article['text'][:60]}...")
```

**Output:**
```
Extracted 3 articles
  • Article 10: Чл. 10. Кредиторът е длъжен да посочи годишния проце...
  • Article 11: Чл. 11. Кредиторът не може да променя лихвения проц...
  • Article 12: Чл. 12. Всички такси и комисионни трябва да са разкр...
```

### Advanced Article Extraction

Extract articles with metadata (title, chapter, subsections).

```python
def extract_articles_advanced(text):
    """Extract articles with full metadata."""
    articles = []
    current_chapter = None
    
    # First, find all chapters
    chapter_pattern = r'(Глава|ГЛАВА)\s+([IVX]+|[А-Я]+)\s*\n\s*([^\n]+)'
    chapters = list(re.finditer(chapter_pattern, text))
    
    # Then find all articles
    article_pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.\s*(?:\(([^\)]+)\))?\s*([^\n]*)'
    article_matches = list(re.finditer(article_pattern, text))
    
    for i, match in enumerate(article_matches):
        article_number = match.group(1)
        article_title = match.group(3) if match.group(3) else None
        
        # Find which chapter this belongs to
        for j, chapter in enumerate(chapters):
            if chapter.start() < match.start():
                if j + 1 >= len(chapters) or chapters[j+1].start() > match.start():
                    current_chapter = chapter.group(3).strip()
                    break
        
        # Extract full content
        start = match.start()
        if i < len(article_matches) - 1:
            end = article_matches[i + 1].start()
        else:
            end = len(text)
        
        content = text[start:end].strip()
        
        articles.append({
            'number': article_number,
            'title': article_title,
            'chapter': current_chapter,
            'content': content
        })
    
    return articles
```

---

## Database Population

### Database Schema

The system uses SQLAlchemy models for legal data storage.

**Key Tables:**

1. **legal_documents** - Main legal documents
   - `id` - Primary key
   - `title` - Document title
   - `document_type` - law/regulation/decree
   - `document_number` - Official number
   - `promulgation_date` - When enacted
   - `effective_date` - When became effective
   - `full_text` - Complete document text
   - `source_url` - Original source URL
   - `is_active` - Active status

2. **legal_articles** - Individual articles
   - `id` - Primary key
   - `document_id` - Foreign key to legal_documents
   - `article_number` - Article number (e.g., "10", "15а")
   - `title` - Article title/heading
   - `content` - Full article text
   - `chapter` - Chapter/section name

### Saving Documents

**Example:**

```python
from database.models import Base, Session
from database.legal_models import LegalDocument, LegalArticle
from sqlalchemy import create_engine
from datetime import datetime

# Initialize database
engine = create_engine('sqlite:///credit_guardian.db')
Base.metadata.create_all(engine)
session = Session()

# Create legal document
document = LegalDocument(
    title="ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ",
    document_type="law",
    document_number="ДВ. бр.18 от 2010г.",
    promulgation_date=datetime(2010, 3, 5),
    effective_date=datetime(2010, 5, 11),
    full_text=law_text,
    source_url="https://www.ciela.net/...",
    is_active=True
)

session.add(document)
session.commit()

print(f"✅ Document saved with ID: {document.id}")

# Add articles
for article_data in articles:
    article = LegalArticle(
        document_id=document.id,
        article_number=article_data['number'],
        title=article_data.get('title'),
        content=article_data['content'],
        chapter=article_data.get('chapter')
    )
    session.add(article)

session.commit()
print(f"✅ Saved {len(articles)} articles")
```

**Output:**
```
✅ Document saved with ID: 1
✅ Saved 47 articles
```

---

## Data Verification

### Check Imported Laws

Verify what has been imported into the database.

**Example:**

```python
from check_imported_laws import *

# Run verification script
print("=" * 70)
print("📊 IMPORTED BULGARIAN LAWS - DATABASE STATUS")
print("=" * 70)

# Get statistics
docs = session.query(LegalDocument).all()
print(f"\n✅ Total Legal Documents: {len(docs)}")
print(f"✅ Total Legal Articles: {session.query(LegalArticle).count()}")

# Show each document
for doc in docs:
    article_count = session.query(LegalArticle).filter_by(
        document_id=doc.id
    ).count()
    
    print(f"\n🔹 {doc.title}")
    print(f"   ID: {doc.id}")
    print(f"   Type: {doc.document_type}")
    print(f"   Articles: {article_count}")
    print(f"   Text Length: {len(doc.full_text) if doc.full_text else 0} chars")
```

**Output Example:**
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
   Text Length: 28,543 chars

🔹 ЗАКОН ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ
   ID: 2
   Type: law
   Articles: 152
   Text Length: 67,234 chars
```

### Query Specific Articles

Search for specific legal articles:

```python
from database.models import Session
from database.legal_models import LegalDocument, LegalArticle

session = Session()

# Find articles about GPR (годишен процент на разходите)
gpr_articles = session.query(LegalArticle).join(LegalDocument).filter(
    LegalArticle.content.like('%годишен процент на разходите%')
).all()

print(f"Found {len(gpr_articles)} articles mentioning GPR")

for article in gpr_articles:
    print(f"\n{article.document.title} - Чл. {article.article_number}")
    print(f"  {article.content[:200]}...")
```

**Output:**
```
Found 3 articles mentioning GPR

ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ - Чл. 10
  Кредиторът е длъжен да посочи годишния процент на разходите (ГПР)
  при представяне на оферта и при сключване на договор...

ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ - Чл. 19
  ГПР се изчислява по стандартна формула, определена в приложение 1...
```

---

## Advanced Features

### 1. Batch Import with Progress Tracking

Import multiple documents with detailed progress:

```python
from tqdm import tqdm
import time

def batch_import_with_progress(law_list, importer):
    """Import multiple laws with progress bar."""
    
    stats = {
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'total_articles': 0
    }
    
    for law in tqdm(law_list, desc="Importing laws"):
        try:
            # Check if exists
            existing = session.query(LegalDocument).filter_by(
                title=law['title']
            ).first()
            
            if existing:
                stats['skipped'] += 1
                continue
            
            # Import
            content = importer.fetch_law_content(law['url'])
            if content:
                doc = importer.save_document(law['title'], content)
                articles = importer.save_articles(doc.id, content['articles'])
                
                stats['successful'] += 1
                stats['total_articles'] += len(articles)
            else:
                stats['failed'] += 1
                
        except Exception as e:
            print(f"\n❌ Error importing {law['title']}: {e}")
            stats['failed'] += 1
        
        time.sleep(2)  # Rate limiting
    
    return stats

# Usage
stats = batch_import_with_progress(law_list, importer)
print(f"\n📊 Import Statistics:")
print(f"  ✅ Successful: {stats['successful']}")
print(f"  ❌ Failed: {stats['failed']}")
print(f"  ⏭️ Skipped: {stats['skipped']}")
print(f"  📄 Total articles: {stats['total_articles']}")
```

### 2. Incremental Updates

Check for and import new content:

```python
def check_for_updates(scraper, session):
    """Check if any laws have been updated."""
    
    updates_found = []
    
    # Get all documents in database
    existing_docs = session.query(LegalDocument).all()
    
    for doc in existing_docs:
        if not doc.source_url:
            continue
        
        # Fetch current content
        current_content = scraper.get_law_content(doc.source_url)
        
        if current_content:
            # Compare content length (simple check)
            if len(current_content['full_text']) != len(doc.full_text or ''):
                updates_found.append({
                    'document': doc,
                    'old_length': len(doc.full_text or ''),
                    'new_length': len(current_content['full_text']),
                    'content': current_content
                })
        
        time.sleep(2)
    
    return updates_found

# Usage
updates = check_for_updates(scraper, session)
if updates:
    print(f"Found {len(updates)} documents with updates")
    for update in updates:
        print(f"  • {update['document'].title}")
        print(f"    Old: {update['old_length']} chars")
        print(f"    New: {update['new_length']} chars")
```

### 3. Export to JSON

Export legal data for backup or analysis:

```python
import json

def export_legal_data(output_file='legal_data_export.json'):
    """Export all legal data to JSON."""
    
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
        
        doc_data = {
            'id': doc.id,
            'title': doc.title,
            'document_type': doc.document_type,
            'source_url': doc.source_url,
            'article_count': len(articles),
            'articles': [
                {
                    'number': art.article_number,
                    'title': art.title,
                    'content': art.content,
                    'chapter': art.chapter
                }
                for art in articles
            ]
        }
        
        export_data['documents'].append(doc_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exported {len(docs)} documents to {output_file}")
    return output_file

# Usage
export_legal_data('legal_data_backup.json')
```

---

## Integration with AI Agent

The imported legal data integrates seamlessly with the Credit Guardian AI agent.

**Example:**

```python
from ai_agent.agent_executor import AgentExecutor

# Initialize agent
agent = AgentExecutor()

# The agent can now reference imported legal articles
result = agent.analyze_contract(
    contract_pdf_path='contract.pdf',
    check_legal_compliance=True
)

# Output includes legal references
print(f"Violations found: {len(result['violations'])}")
for violation in result['violations']:
    print(f"\n• {violation['description']}")
    print(f"  Legal basis: {violation['legal_reference']}")
    print(f"  Article: {violation['article_number']}")
```

---

## Performance Metrics

### Import Performance

Typical performance metrics for the import system:

| Operation | Time | Notes |
|-----------|------|-------|
| Fetch single law | 2-5s | Includes rate limiting |
| Extract articles | 0.1-0.5s | Per document |
| Save to database | 0.05-0.2s | Per document + articles |
| Import 10 laws | ~30-60s | With 2s delay between requests |
| Full import (150 laws) | ~8-12 min | Priority laws first |

### Database Statistics

After full import:

- **Legal Documents**: 150-200
- **Legal Articles**: 15,000-20,000
- **Database Size**: 50-100 MB
- **Average articles per law**: 80-120
- **Largest document**: Civil Procedural Code (600+ articles)

---

## Error Handling

The system includes comprehensive error handling:

```python
try:
    content = scraper.get_law_content(url)
    if not content:
        print("❌ Failed to fetch content")
except requests.exceptions.Timeout:
    print("⏱️ Request timeout - server may be slow")
except requests.exceptions.ConnectionError:
    print("🔌 Connection error - check network")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    # Log error for debugging
    import traceback
    traceback.print_exc()
```

---

## Conclusion

The Legal Data Import System provides comprehensive functionality for:

✅ **Automated scraping** from multiple Bulgarian legal sources  
✅ **Intelligent article extraction** with pattern recognition  
✅ **Structured database storage** for efficient querying  
✅ **Data verification** and quality control  
✅ **Integration with AI agent** for legal analysis  
✅ **Export and backup** capabilities  

For quick reference commands, see [QUICK_IMPORT_REFERENCE.md](QUICK_IMPORT_REFERENCE.md).  
For complete usage guide, see [LEGAL_DATA_IMPORT_GUIDE.md](LEGAL_DATA_IMPORT_GUIDE.md).  
For technical details, see [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md).
