# Credit Guardian - Training & Database Guide

## 📍 Database Location

**Primary Database:** `C:\credit-guardian\credit_guardian.db` (56 KB)

### Database Schema

The system uses **SQLite** with the following tables:

#### Core Tables (credit_guardian.db)
- **`creditors`** - Financial institutions and lenders
- **`violations`** - Historical violation records
- **`unfair_clauses`** - Detected unfair contract terms
- **`court_cases`** - Legal precedents and cases
- **`credit_products`** - Credit product details and GPR analysis

#### Legal Knowledge Base Tables (NEW)
- **`legal_documents`** - Bulgarian laws from lex.bg
- **`legal_articles`** - Individual articles from laws
- **`consumer_cases`** - APIS.bg violation records
- **`training_examples`** - AI agent training data

## 🎓 Training the AI Agent

### Quick Start Training

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run training pipeline
python train_agent.py
```

### Training Pipeline Steps

The `train_agent.py` script performs:

1. **Scrapes lex.bg** - Downloads Bulgarian consumer protection laws:
   - Закон за потребителския кредит (Consumer Credit Act)
   - Закон за защита на потребителите (Consumer Protection Act)
   - Закон за кредитните институции (Credit Institutions Act)
   - Наредба № 8 за лихвите (Interest Rates Regulation)

2. **Scrapes apis.bg** - Collects violation records:
   - Company violations and penalties
   - Blacklisted entities
   - Administrative decisions

3. **Imports into Database** - Populates:
   - Legal documents table (laws & regulations)
   - Violation records (linked to creditors)
   - Blacklist (flagged companies)
   - Training examples (for evaluation)

4. **Generates Training Data** - Creates examples for:
   - GPR calculation validation
   - Unfair clause detection
   - Violation checking

## 🔧 Manual Training Options

### 1. Use Cached Data (Faster)

Edit `train_agent.py` line 235:
```python
trainer.train_agent(use_cached=True)  # Uses cached JSON files
```

### 2. Fresh Scraping (Slower, Updated)

```python
trainer.train_agent(use_cached=False)  # Scrapes live data
```

### 3. Run Individual Scrapers

```powershell
# Scrape lex.bg only
python -m scrapers.lex_bg_scraper

# Scrape apis.bg only
python -m scrapers.apis_bg_scraper
```

## 📂 Data Files Structure

```
C:\credit-guardian\
├── credit_guardian.db          # Main database (56 KB)
├── data/                       # Scraped data cache
│   ├── lex_bg_laws.json       # Bulgarian laws
│   └── apis_bg_data.json      # Violation records
├── database/
│   ├── models.py              # Core database models
│   └── legal_models.py        # Legal knowledge base models
├── scrapers/
│   ├── lex_bg_scraper.py      # Law scraper
│   └── apis_bg_scraper.py     # Violation scraper
└── train_agent.py             # Training orchestrator
```

## 🌐 Frontend User Experience

### Enhanced UI Features

1. **Welcome Message** - Clear instructions on Contract Analyzer page
2. **Visual Icons** - Emoji indicators for better navigation
3. **Help Text** - Inline guidance for each feature
4. **Better Labels** - Bulgarian language with professional terminology

### Improved Components

- ✅ **ContractAnalyzer** - Added welcome message with feature list
- ✅ **App Header** - Enhanced with professional description
- ✅ **Navigation** - Clear emoji icons for each section

## 🚀 Running the Complete System

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Set OpenAI API key
$env:OPENAI_API_KEY = 'your-key-here'

# 3. Train the agent (first time only)
python train_agent.py

# 4. Start the backend server
python app.py
```

Then open: http://localhost:8000/docs

## 📊 Verifying Training Success

```powershell
# Check database contents
python -c "from database.models import Session; from database.legal_models import LegalDocument, ConsumerCase; s = Session(); print(f'Legal Docs: {s.query(LegalDocument).count()}'); print(f'Consumer Cases: {s.query(ConsumerCase).count()}')"
```

Expected output after training:
```
Legal Docs: 5+
Consumer Cases: 50+
Violations: 100+
```

## 🔍 Data Sources

- **lex.bg** - Official Bulgarian legal database
- **apis.bg** - Consumer Protection Commission (КЗП)
- Both sources are publicly accessible Bulgarian government resources

## ⚠️ Important Notes

1. **Rate Limiting** - Scrapers include 2-second delays to respect server limits
2. **Bulgarian Language** - All data is in Bulgarian (Cyrillic)
3. **Legal Compliance** - Only public data is scraped
4. **Cache Usage** - Recommended for development to avoid repeated scraping

## 🆘 Troubleshooting

### "Module not found" error
```powershell
pip install beautifulsoup4 requests
```

### Database locked
```powershell
# Stop the server first
# Then run training
```

### Slow scraping
```python
# Use cached data instead
trainer.train_agent(use_cached=True)
```

---

**Ready to train?** Run `python train_agent.py` now!
