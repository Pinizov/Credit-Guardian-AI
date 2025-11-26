# 📦 Publishing Credit Guardian to GitHub

## Current Project Status

### ✅ **What Works (Production-Ready)**

#### 1. **Bulgarian Legal Code Import** (5,763 articles)
- 16 Bulgarian codes imported from ciela.net
- Full metadata with chapters, sections, article numbers
- Database: `credit_guardian.db` (SQLite)

#### 2. **Advanced Tagging System**
- Bulgarian NLP stemmer
- TF-IDF scoring (7,980 tagged articles)
- 13 legal categories
- Tag scores for ranking

#### 3. **FREE Embedding Pipeline**
- Local sentence-transformers model
- 384-dimensional vectors
- Semantic search with cosine similarity
- No API costs

#### 4. **Database Schema**
- `legal_documents` - 16 codes
- `legal_articles` - 5,763 articles with normalized metadata
- `legal_article_tags` - 7,980 scored tags
- `article_ingestion` - Materialized view for AI
- `article_embeddings` - Vector storage

#### 5. **Core Features**
- Contract analysis
- GPR (Guaranteed Payment Rate) calculator
- Clause detection
- Report generation

---

## 🚀 Step-by-Step GitHub Publishing

### **Step 1: Review What to Commit**

```powershell
# Check git status
git status

# See what's staged
git diff --cached
```

**Files to EXCLUDE** (already in .gitignore):
- `credit_guardian.db` (8.5 MB - too large, contains data)
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `frontend/node_modules/` (NPM dependencies - 300MB+)
- `htmlcov/` (coverage reports)

### **Step 2: Add Essential Files**

```powershell
# Add core Python code
git add *.py
git add ai_agent/*.py analyzers/*.py database/*.py utils/*.py

# Add configuration
git add requirements.txt setup.cfg pyproject.toml alembic.ini
git add Dockerfile docker-compose.yml

# Add documentation
git add README*.md *.md
git add .gitignore

# Add frontend (but not node_modules)
git add frontend/src frontend/public frontend/package.json frontend/vite.config.js
```

### **Step 3: Check What Will Be Committed**

```powershell
git status
```

Should show:
- Python source files (.py)
- Config files
- Documentation (.md)
- Frontend source (not node_modules)

### **Step 4: Create Initial Commit**

```powershell
git add .
git commit -m "Initial commit: Credit Guardian - Bulgarian Legal Analysis Platform

Features:
- 5,763 Bulgarian legal articles from 16 codes
- Advanced tagging with TF-IDF scoring
- FREE embedding pipeline (sentence-transformers)
- Semantic search with cosine similarity
- Contract analysis and GPR calculator
- Flask API + React frontend
"
```

### **Step 5: Create GitHub Repository**

1. Go to https://github.com/new
2. Repository name: `credit-guardian`
3. Description: `Bulgarian legal analysis platform with AI-powered semantic search`
4. Choose: **Public** or **Private**
5. Do NOT initialize with README (you already have one)
6. Click "Create repository"

### **Step 6: Push to GitHub**

```powershell
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/credit-guardian.git

# Push to main branch
git push -u origin main
```

If you get authentication errors:
```powershell
# Use GitHub CLI
gh auth login

# Or use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/credit-guardian.git
git push -u origin main
```

---

## 📊 Repository Structure (What Gets Uploaded)

```
credit-guardian/
├── .gitignore                    # Excludes db, venv, cache
├── README.md                     # Main documentation
├── README_EMBEDDINGS_FREE.md     # Embedding guide
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project metadata
├── setup.cfg                    # Linting config
├── Dockerfile                   # Docker container
├── docker-compose.yml           # Multi-container setup
├── alembic.ini                  # DB migrations
│
├── app.py                       # Main Flask app
├── start_server.py              # Server entry point
│
├── ai_agent/                    # AI components
│   ├── agent_executor.py
│   ├── llm_client.py
│   ├── pdf_processor.py
│   └── tracing.py
│
├── analyzers/                   # Legal analysis
│   ├── clause_detector.py
│   ├── contract_analyzer.py
│   └── gpr_calculator.py
│
├── database/                    # Database models
│   ├── models.py
│   ├── legal_models.py
│   ├── embedding_models.py
│   ├── init_db.py
│   └── seed_db.py
│
├── utils/                       # Utilities
│   ├── helpers.py
│   ├── report_generator.py
│   ├── legal_texts.py
│   └── s3_storage.py
│
├── scrapers/                    # Data importers
│   └── (scraper files)
│
├── tests/                       # Unit tests
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_clause_detector.py
│   └── ...
│
├── frontend/                    # React app
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── Legal code import scripts:
    ├── import_codexes.py
    ├── enrich_metadata.py
    ├── tag_articles.py
    ├── advanced_tagging.py
    ├── create_ingestion_view.py
    ├── generate_embeddings.py      # FREE embedding generator
    ├── semantic_search.py          # Search engine
    └── test_embedding_pipeline.py
```

**Total size (without node_modules, .venv, db)**: ~5-10 MB

---

## 🔒 Security Checklist

Before pushing, ensure NO sensitive data:

```powershell
# Check for API keys
Get-Content -Path (Get-ChildItem -Recurse -Include *.py,*.js,*.env) | Select-String -Pattern "sk-|api_key|password|secret"

# Check for hardcoded credentials
Get-Content app.py,database/models.py | Select-String -Pattern "password|secret|key"
```

**If found**, replace with environment variables:
```python
# BAD
api_key = "sk-abc123..."

# GOOD
api_key = os.getenv("PERPLEXITY_API_KEY")  # Or use Ollama locally
```

---

## 📝 Update README.md

Make sure your README includes:

```markdown
# Credit Guardian

Bulgarian legal analysis platform with AI-powered semantic search.

## Features
- 5,763 legal articles from 16 Bulgarian codes
- Advanced tagging with TF-IDF scoring
- FREE semantic search (sentence-transformers)
- Contract analysis and GPR calculator
- React frontend + Flask API

## Quick Start

### 1. Clone Repository
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/credit-guardian.git
cd credit-guardian
\`\`\`

### 2. Setup Backend
\`\`\`bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 3. Import Legal Codes (Optional - or download pre-built DB)
\`\`\`bash
python import_codexes.py
python enrich_metadata.py
python advanced_tagging.py
\`\`\`

### 4. Generate Embeddings (FREE)
\`\`\`bash
pip install sentence-transformers
python generate_embeddings.py
\`\`\`

### 5. Run Server
\`\`\`bash
python start_server.py
# Server: http://localhost:5000
\`\`\`

### 6. Run Frontend
\`\`\`bash
cd frontend
npm install
npm run dev
# Frontend: http://localhost:5173
\`\`\`

## Documentation
- [Embedding Pipeline (FREE)](README_EMBEDDINGS_FREE.md)
- [Database Setup](README_DB.md)
- [API Documentation](README_API.md)
```

---

## 🎯 Post-Upload Tasks

### 1. **Add GitHub Topics**
Go to repository settings → Topics, add:
- `bulgarian`
- `legal-tech`
- `nlp`
- `semantic-search`
- `sentence-transformers`
- `flask`
- `react`

### 2. **Enable GitHub Actions** (optional)
Create `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
```

### 3. **Add License**
Create `LICENSE` file (MIT recommended):
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

### 4. **Database Distribution** (Optional)
Since `credit_guardian.db` is 8.5 MB, you have options:

**Option A:** Upload to GitHub Releases
```powershell
# Compress database
Compress-Archive -Path credit_guardian.db -DestinationPath credit_guardian_db.zip
# Upload manually via GitHub Releases page
```

**Option B:** Provide import scripts
Users run `import_codexes.py` to build their own DB (takes 10 min).

**Option C:** Use Git LFS (Large File Storage)
```powershell
git lfs install
git lfs track "*.db"
git add .gitattributes
git commit -m "Track database with LFS"
```

---

## 📤 Final Push Commands

```powershell
# Review changes
git status
git diff

# Stage all (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit: Credit Guardian platform"

# Push
git push -u origin main
```

---

## ✅ Verification Checklist

After pushing, verify on GitHub:

- [ ] All Python files visible
- [ ] Frontend source code present
- [ ] Documentation readable
- [ ] No sensitive data (API keys, passwords)
- [ ] No large binary files (except via LFS)
- [ ] .gitignore working (no .venv, __pycache__)
- [ ] README displays correctly
- [ ] requirements.txt complete

---

## 🔄 Ongoing Maintenance

### **Adding New Features**
```powershell
git checkout -b feature/new-analyzer
# Make changes
git add .
git commit -m "Add new analyzer for X"
git push origin feature/new-analyzer
# Create Pull Request on GitHub
```

### **Updating Dependencies**
```powershell
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

---

## 🆘 Common Issues

### **"Repository too large"**
Remove large files:
```powershell
git rm --cached credit_guardian.db
git commit -m "Remove database from git"
git push
```

### **"node_modules uploaded by mistake"**
```powershell
git rm -r --cached frontend/node_modules
git commit -m "Remove node_modules"
git push
```

### **"Authentication failed"**
Use Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (repo scope)
3. Use token as password

---

## 📊 Repository Stats Preview

Once published, your repo will show:

- **Language**: Python 85%, JavaScript 12%, HTML/CSS 3%
- **Lines of code**: ~15,000
- **Files**: ~80 source files
- **Features**: 5 core modules, 7 utilities, 16 legal codes

**Congratulations! Your Bulgarian Legal AI Platform is now on GitHub!** 🎉
