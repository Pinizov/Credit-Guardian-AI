# Local Legal Data - Quick Reference

## 📂 Source Folder
```
C:\Users\User\Downloads\Legal Data
```

## ✅ Import Status
- **35 files** successfully imported into database
- **All file types** supported: PDF, CSV, XLS, XLSX, DOC, DOCX
- **Database table**: `legal_documents`

## 🚀 Quick Commands

### Run Full Import
```powershell
python import_local_legal_data.py
```

### Quick Import with Progress
```powershell
python quick_import.py
```

### Check Database Status
```powershell
python status_check.py
```

### View Local Documents Only
```powershell
python check_local_docs.py
```

### View All Documents
```powershell
python check_imports.py
```

## 📊 Current Database State

**Total Documents**: 59
- Web-scraped: 24
- Local folder: 35

**By Type**:
- Laws: 22
- Codes: 16
- Registries: 11
- Other: 8
- Constitution: 1
- Regulation: 1

## 📝 File Types in Local Folder

| Type | Count | Examples |
|------|-------|----------|
| XLS/XLSX | 12 | BNB registers, payment services |
| DOC | 6 | Bank lists, administrative codes |
| CSV | 3 | Ciela legal data |
| PDF | 2 | Legal ordinances, laws |

## 🔍 Query Examples

### Python Query (All Local Documents)
```python
from database.models import SessionLocal
from database.legal_models import LegalDocument

session = SessionLocal()
local_docs = session.query(LegalDocument).filter(
    LegalDocument.source_url.like('file:///%')
).all()

for doc in local_docs:
    print(f"{doc.title}: {len(doc.full_text)} chars")
```

### Python Query (Specific File Type)
```python
registry_docs = session.query(LegalDocument).filter(
    LegalDocument.document_type == 'registry',
    LegalDocument.source_url.like('file:///%')
).all()
```

## 🔧 Key Features

✅ Automatic document type classification  
✅ Multi-format content extraction  
✅ Error handling for problematic files  
✅ Duplicate prevention  
✅ Progress tracking  
✅ Full database integration  

## ⚠️ Notes

- Some DOC files show minimal content (specialized formats may need additional processing)
- PDF extraction is optimized for speed (first 20 pages, max 30k chars)
- Excel files are fully extracted as text
- All documents maintain original filename and source path

## 🎯 Next Steps

1. **Article Extraction**: Parse individual articles from legal documents
2. **Register Structuring**: Convert registry Excel files to structured data
3. **Embeddings**: Generate vector embeddings for semantic search
4. **Linking**: Connect registry data to existing creditor records
5. **Monitoring**: Set up automated re-import for folder changes

---
Last Updated: November 24, 2025
