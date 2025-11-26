# Legal Data Import & Scraping Guide

This guide covers the comprehensive legal data import and scraping functionality for Credit Guardian AI.

## 📁 File Structure

```
credit-guardian/
├── quick_import.py                  # Streamlined import with progress tracking
├── status_check.py                  # Database status checker
├── test_local_import.py            # Test local data import
├── test_perplexity.py              # Test Perplexity API integration
└── scrapers/
    ├── base_scraper.py             # Abstract base class for scrapers
    ├── bnb_rates_scraper.py        # Bulgarian National Bank rates
    ├── eur_lex_scraper.py          # EUR-Lex directives
    ├── kzp_complaints_scraper.py   # KZP consumer complaints
    ├── nsi_macro_scraper.py        # NSI macro indicators
    └── local_folder_scraper.py     # Local folder document scanner
```

## 🚀 Quick Start

### 1. Import Local Legal Documents

The `quick_import.py` script provides streamlined importing with progress tracking:

```powershell
python quick_import.py
```

**Features:**
- Automatically scans a local folder for legal documents
- Supports PDF, DOC, DOCX, TXT, HTML, XML, JSON, CSV, XLS, XLSX formats
- Progress tracking with detailed statistics
- Smart document type detection (law, regulation, registry, etc.)
- Automatic content extraction and validation
- Skips files with insufficient content

**Example Output:**
```
Starting quick import from: C:\Users\User\Downloads\Legal Data

Scanning folder...

Found 45 files

[1/45] Processing: Consumer_Protection_Law.pdf...
  Saved as ID 101
[2/45] Processing: Credit_Institutions_Act.pdf...
  Saved as ID 102
...

============================================================
IMPORT COMPLETE
============================================================
  Total files: 45
  Successfully imported: 38
  Skipped (no content): 5
  Errors: 2
============================================================
```

### 2. Check Database Status

Use `status_check.py` to get comprehensive statistics:

```powershell
python status_check.py
```

**Provides:**
- Total document count
- Documents by source (web-scraped vs. local)
- Documents by type (law, regulation, registry, etc.)
- Content statistics (average length, documents with content)
- Sample list of local documents with validation status

### 3. Test Local Import

Before running a full import, test with:

```powershell
python test_local_import.py
```

This provides:
- File count and structure
- Breakdown by file extension
- Sample file listings
- Quick validation without database writes

### 4. Test Perplexity API Integration

Verify AI integration with:

```powershell
python test_perplexity.py
```

**Tests:**
- Basic API connection
- Contract analysis functionality
- Bulgarian legal question answering
- Fee detection and violation identification

## 📚 Scraper Architecture

### Base Scraper (`base_scraper.py`)

Abstract base class providing common functionality for all scrapers:

**Key Features:**
- Network request handling with retries
- Automatic rate limiting with jitter
- Session management with custom headers
- JSON data persistence
- Consistent error logging

**Usage:**
```python
from scrapers.base_scraper import BaseScraper

class MyScraper(BaseScraper):
    name = "my_scraper"
    base_url = "https://example.com"
    delay = 1.5  # seconds between requests
    
    def scrape_all(self) -> Dict[str, Any]:
        # Your implementation
        pass
```

### Local Folder Scraper (`local_folder_scraper.py`)

Processes legal documents from local filesystem.

**Supported Formats:**
- **Text:** TXT, HTML, XML, JSON
- **PDFs:** Automatic text extraction (with page limits for performance)
- **Office:** DOC, DOCX (marked for specialized extraction)
- **Spreadsheets:** CSV, XLS, XLSX

**Features:**
- Recursive folder scanning
- Smart timeout protection for PDF extraction
- Multiple encoding detection for CSV files
- File metadata collection (size, modified time)
- Content validation and error handling

**Usage:**
```python
from scrapers.local_folder_scraper import LocalFolderScraper

scraper = LocalFolderScraper(r"C:\Legal Data")
data = scraper.scrape_all()

print(f"Found {data['total_files']} files")
for file in data['files']:
    print(f"  {file['filename']}: {len(file['content'])} chars")
```

### Bulgarian National Bank Rates (`bnb_rates_scraper.py`)

Scrapes base interest rates and reference indicators from BNB.

**Data Collected:**
- Historical base interest rates
- Monthly rate changes
- Date and rate value pairs

**Usage:**
```python
from scrapers.bnb_rates_scraper import BNBRatesScraper

scraper = BNBRatesScraper()
data = scraper.run("data/bnb_rates.json")
print(f"Collected {len(data['base_interest_rates'])} rate points")
```

### EUR-Lex Directives (`eur_lex_scraper.py`)

Fetches EU consumer protection directives relevant to credit law.

**Data Collected:**
- Directive titles
- Official EUR-Lex URLs
- Metadata for local indexing

**Usage:**
```python
from scrapers.eur_lex_scraper import EURLexScraper

scraper = EURLexScraper()
data = scraper.run("data/eur_lex.json")
print(f"Directives collected: {len(data['directives'])}")
```

### KZP Complaints (`kzp_complaints_scraper.py`)

Extracts consumer complaints and decisions from the Consumer Protection Commission.

**Data Collected:**
- Complaint summaries
- Decision metadata
- Company information
- Case dates and URLs

**Usage:**
```python
from scrapers.kzp_complaints_scraper import KZPComplaintsScraper

scraper = KZPComplaintsScraper()
data = scraper.run("data/kzp_data.json")
print(f"Complaints: {len(data['complaints'])}")
print(f"Decisions: {len(data['decisions'])}")
```

### NSI Macro Indicators (`nsi_macro_scraper.py`)

Scrapes macro-economic indicators from the National Statistical Institute.

**Indicators Tracked:**
- Consumer Price Index (CPI)
- Unemployment rate
- Average wage

**Usage:**
```python
from scrapers.nsi_macro_scraper import NSIMacroScraper

scraper = NSIMacroScraper()
data = scraper.run("data/nsi_macro.json")
print(f"Indicators collected: {len(data['indicators'])}")
```

## 🗄️ Database Models

Legal documents are stored using these models (defined in `database/legal_models.py`):

### LegalDocument
- `title`: Document name
- `document_type`: law, regulation, decree, registry, other
- `document_number`: Official document number
- `promulgation_date`: When law was enacted
- `effective_date`: When law became effective
- `full_text`: Full document content
- `source_url`: Source (file path or web URL)
- `is_active`: Whether document is currently in force

### LegalArticle
- Related to parent `LegalDocument`
- Individual articles with structured sections
- Chapter and section metadata
- Full article content

### ConsumerCase
- Consumer protection cases and precedents
- Violations, complaints, and lawsuits
- Authority (APIS, KZP, BNB, Court)
- Penalties and decisions

## 🔧 Configuration

### Folder Path
Edit `quick_import.py` to change the default folder:
```python
folder_path = r"C:\Your\Legal\Data\Folder"
```

### Scraper Settings
Adjust delay and retry settings in each scraper:
```python
class MyScraper(BaseScraper):
    delay = 2.0           # seconds between requests
    max_retries = 3       # number of retry attempts
    timeout = 15          # request timeout in seconds
```

## 📊 Performance Tips

1. **Local Import:** First 20 pages of PDFs only (configurable in `local_folder_scraper.py`)
2. **Rate Limiting:** All web scrapers include automatic delays to respect server limits
3. **Error Recovery:** Automatic retry with exponential backoff
4. **Content Limits:** Text limited to 50,000 characters per document to manage database size

## 🔍 Troubleshooting

### Issue: PDF text extraction fails
**Solution:** Check that `PyPDF2` is installed. Some PDFs may be scanned images and require OCR.

### Issue: Database connection errors
**Solution:** Ensure database is initialized with:
```powershell
python database/init_all_tables.py
```

### Issue: Encoding errors with CSV/text files
**Solution:** `local_folder_scraper.py` tries multiple encodings automatically (utf-8, cp1251, latin-1, windows-1252)

### Issue: Perplexity API errors
**Solution:** Verify API key is set in environment or in `test_perplexity.py`

## 📈 Next Steps

1. **Add More Scrapers:** Create new scrapers by extending `BaseScraper`
2. **Schedule Regular Updates:** Use Windows Task Scheduler or cron to run scrapers periodically
3. **Enhance Extraction:** Add OCR support for scanned PDFs
4. **Add Validation:** Implement schema validation for scraped data
5. **Create API Endpoints:** Expose scraped data through REST API

## 🛡️ Legal Compliance

This system is designed for:
- Academic research
- Consumer protection
- Legal analysis
- Public interest transparency

Always respect:
- robots.txt files
- Rate limits
- Copyright and licensing
- Terms of service of data sources

## 📝 Example Workflow

```powershell
# 1. Test local data folder
python test_local_import.py

# 2. Import legal documents
python quick_import.py

# 3. Check database status
python status_check.py

# 4. Scrape Bulgarian National Bank rates
python -c "from scrapers.bnb_rates_scraper import BNBRatesScraper; BNBRatesScraper().run('data/bnb_rates.json')"

# 5. Scrape KZP complaints
python -c "from scrapers.kzp_complaints_scraper import KZPComplaintsScraper; KZPComplaintsScraper().run('data/kzp_data.json')"

# 6. Verify Perplexity API integration
python test_perplexity.py
```

## 📚 Dependencies

```
sqlalchemy>=2.0.0
pandas>=2.0.0
PyPDF2>=3.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
openpyxl>=3.1.0  # for Excel files
xlrd>=2.0.0      # for old .xls files
```

## 🤝 Contributing

To add a new scraper:

1. Create a new file in `scrapers/` directory
2. Extend `BaseScraper` class
3. Implement `scrape_all()` method
4. Add documentation and example usage
5. Create test script
6. Update this guide

## 📞 Support

For issues or questions:
- Check `status_check.py` output for database status
- Review error logs in console output
- Verify all dependencies are installed
- Ensure database tables are initialized

---

**Status:** ✅ All components implemented and tested
**Last Updated:** November 24, 2025
**Version:** 1.0
