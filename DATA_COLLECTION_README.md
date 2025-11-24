# Credit Guardian - Data Collection System

## Overview
Comprehensive data ingestion system for Bulgarian legal, financial, and regulatory data to power Credit Guardian's AI agent and risk analysis.

## ✅ Completed Integrations

### 1. Local Legal Data Folder ✅
**Status**: Fully operational  
**Location**: `C:\Users\User\Downloads\Legal Data`  
**Documents**: 35 files imported  
**Types**: PDF, CSV, XLS, XLSX, DOC  
**Script**: `import_local_legal_data.py`  
**Details**: See `LOCAL_DATA_IMPORT_SUMMARY.md`

### 2. Web Scrapers (Existing)
- **lex.bg**: 24 documents scraped
- **ciela.net**: Laws and regulations  
- **apis.bg**: Consumer protection data (needs selector fixes)

## 📊 Current Database State

```
Total Legal Documents: 59
├── Web-scraped: 24
└── Local folder: 35

By Type:
├── Laws: 22
├── Codes: 16
├── Registries: 11
├── Other: 8
├── Constitution: 1
└── Regulation: 1
```

## 🚀 Quick Start

### Import Local Folder Data
```powershell
cd C:\credit-guardian
python import_local_legal_data.py
```

### Check Status
```powershell
python status_check.py
```

### Verify Local Documents
```powershell
python check_local_docs.py
```

## 📁 Project Structure

```
credit-guardian/
├── scrapers/
│   ├── base_scraper.py              # Base interface for all scrapers
│   ├── local_folder_scraper.py      # ✅ Local file system scanner
│   ├── apis_bg_scraper.py           # Consumer protection authority
│   ├── ciela_net_scraper.py         # Legal database
│   ├── lex_bg_scraper.py            # Legal database
│   ├── bnb_rates_scraper.py         # 🔜 BNB interest rates
│   ├── nsi_macro_scraper.py         # 🔜 NSI macro indicators
│   ├── kzp_complaints_scraper.py    # 🔜 KZP complaints
│   └── eur_lex_scraper.py           # 🔜 EU directives
├── database/
│   ├── models.py                    # Core data models
│   └── legal_models.py              # Legal document models
├── data/                            # Scraped data cache (JSON)
├── import_local_legal_data.py       # ✅ Main local import script
├── quick_import.py                  # ✅ Fast import with progress
├── status_check.py                  # ✅ Database status checker
├── check_local_docs.py              # ✅ Local doc verifier
└── DATA_COLLECTION_PLAN.md          # Master plan document
```

## 🔧 Technical Details

### Supported File Formats
- **PDF**: Text extraction with error handling (PyPDF2)
- **CSV**: Multi-encoding support (pandas)
- **XLS/XLSX**: Full spreadsheet parsing (xlrd, openpyxl)
- **DOC/DOCX**: Document text extraction (python-docx)

### Database Schema
**Table**: `legal_documents`
- `id`: Primary key
- `title`: Document title (filename for local files)
- `document_type`: Classification (law, code, registry, etc.)
- `full_text`: Extracted content
- `source_url`: Origin reference (file:/// for local)
- `is_active`: Status flag
- `created_at`, `updated_at`: Timestamps

### Error Handling
- ✅ Corrupted PDF handling
- ✅ Encoding detection for CSVs
- ✅ Graceful fallback for unsupported formats
- ✅ Transaction rollback on errors
- ✅ Detailed logging

## 📋 Dependencies

```txt
PyPDF2==3.0.1          # PDF processing
pandas==2.1.3          # Data manipulation
xlrd==2.0.1            # Excel .xls files
openpyxl==3.1.2        # Excel .xlsx files
python-docx==1.1.0     # Word documents
sqlalchemy==2.0.23     # ORM
requests==2.31.0       # HTTP client
beautifulsoup4==4.12.2 # HTML parsing
```

## 🎯 Next Steps

### Phase 1 (Priority)
1. ✅ Local folder integration (COMPLETE)
2. 🔜 Fix apis.bg selectors
3. 🔜 Implement BNB rates scraper
4. 🔜 Implement NSI macro indicators
5. 🔜 Article extraction from legal documents

### Phase 2
1. KZP complaints scraper
2. EUR-Lex directives integration
3. Trade register enrichment
4. Structured registry parsing
5. Embedding generation

### Phase 3
1. Automated update detection
2. Delta tracking for amendments
3. Entity linking (creditors)
4. Quality dashboards
5. Real-time monitoring

## 📖 Documentation

- **Master Plan**: `DATA_COLLECTION_PLAN.md`
- **Local Import Summary**: `LOCAL_DATA_IMPORT_SUMMARY.md`
- **Quick Reference**: `LOCAL_DATA_QUICK_REFERENCE.md`
- **API Endpoints**: `API Endpoints.md`

## 🔍 Example Queries

### Get All Local Documents
```python
from database.models import SessionLocal
from database.legal_models import LegalDocument

session = SessionLocal()
docs = session.query(LegalDocument).filter(
    LegalDocument.source_url.like('file:///%')
).all()
```

### Get Registries
```python
registries = session.query(LegalDocument).filter(
    LegalDocument.document_type == 'registry'
).all()
```

### Search by Title
```python
results = session.query(LegalDocument).filter(
    LegalDocument.title.contains('BNB')
).all()
```

## 🛠️ Maintenance

### Re-import Local Folder
```powershell
python import_local_legal_data.py
```

### Update Web Scrapers
```powershell
python scrapers/ciela_net_scraper.py
python scrapers/lex_bg_scraper.py
```

### Database Backup
```powershell
Copy-Item credit_guardian.db credit_guardian_backup_$(Get-Date -Format 'yyyyMMdd').db
```

## 📞 Support

For issues or questions, check:
1. Log files in terminal output
2. `status_check.py` for database state
3. `DATA_COLLECTION_PLAN.md` for architecture details

---
**Version**: 1.0  
**Last Updated**: November 24, 2025  
**Status**: ✅ Production Ready
