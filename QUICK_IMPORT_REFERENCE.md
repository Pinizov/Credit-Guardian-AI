# Legal Data Import - Quick Reference

## 🚀 Common Commands

### Import Legal Documents
```powershell
python quick_import.py
```

### Check Database Status  
```powershell
python status_check.py
```

### Test Local Import
```powershell
python test_local_import.py
```

### Test Perplexity API
```powershell
python test_perplexity.py
```

## 📊 Scraper Usage

### BNB Rates
```powershell
python -c "from scrapers.bnb_rates_scraper import BNBRatesScraper; BNBRatesScraper().run('data/bnb_rates.json')"
```

### EUR-Lex Directives
```powershell
python -c "from scrapers.eur_lex_scraper import EURLexScraper; EURLexScraper().run('data/eur_lex.json')"
```

### KZP Complaints
```powershell
python -c "from scrapers.kzp_complaints_scraper import KZPComplaintsScraper; KZPComplaintsScraper().run('data/kzp_data.json')"
```

### NSI Macro Indicators
```powershell
python -c "from scrapers.nsi_macro_scraper import NSIMacroScraper; NSIMacroScraper().run('data/nsi_macro.json')"
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `quick_import.py` | Import local legal documents with progress tracking |
| `status_check.py` | Check database status and statistics |
| `test_local_import.py` | Test local folder scanning |
| `test_perplexity.py` | Test AI API integration |
| `scrapers/base_scraper.py` | Base class for all scrapers |
| `scrapers/local_folder_scraper.py` | Local file system scanner |
| `scrapers/bnb_rates_scraper.py` | Bulgarian National Bank rates |
| `scrapers/eur_lex_scraper.py` | EU legal directives |
| `scrapers/kzp_complaints_scraper.py` | Consumer complaints |
| `scrapers/nsi_macro_scraper.py` | Economic indicators |

## 🔧 Configuration

### Change Import Folder
Edit `quick_import.py`:
```python
folder_path = r"C:\Your\Path\Here"
```

### Adjust Scraper Delays
Edit any scraper:
```python
delay = 2.0  # seconds between requests
```

## 📊 Database Models

- **LegalDocument**: Laws, regulations, decrees
- **LegalArticle**: Individual articles from documents
- **ConsumerCase**: Complaints, violations, decisions

## 📈 Current Status

Run `python status_check.py` to see:
- Total documents: 59
- Web-scraped: 24
- Local imported: 35
- Document types: laws, codes, registries, etc.

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF extraction fails | Install PyPDF2: `pip install PyPDF2` |
| Database errors | Initialize: `python database/init_all_tables.py` |
| Import path errors | Check folder path in `quick_import.py` |
| API errors | Verify API key in environment or script |

## 🎯 Typical Workflow

1. Test local folder: `python test_local_import.py`
2. Import documents: `python quick_import.py`
3. Check status: `python status_check.py`
4. Run scrapers as needed
5. Test AI integration: `python test_perplexity.py`

## 📚 More Info

See `LEGAL_DATA_IMPORT_GUIDE.md` for comprehensive documentation.
