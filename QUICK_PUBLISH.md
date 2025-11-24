# 🎯 Quick GitHub Publishing Commands

## Current Status ✅
- ✓ 24 Bulgarian legal documents
- ✓ 5,763 articles with full metadata
- ✓ 7,980 TF-IDF scored tags
- ✓ 5,763 embeddings (FREE local model)
- ✓ Clean codebase (no __pycache__, no node_modules)
- ✓ .gitignore configured
- ✓ All documentation ready

## Step-by-Step Publishing

### 1. Check What Will Be Uploaded
```powershell
git status
```

**Should show:**
- Python files (.py)
- Documentation (.md)
- Configuration files
- Frontend source (but NOT node_modules)

**Should NOT show** (excluded by .gitignore):
- credit_guardian.db
- __pycache__/
- .venv/
- node_modules/
- htmlcov/

### 2. Stage All Files
```powershell
git add .
```

### 3. Verify What's Staged
```powershell
git status
```

### 4. Create Commit
```powershell
git commit -m "Initial commit: Credit Guardian - Bulgarian Legal AI Platform

Complete Features:
- 5,763 Bulgarian legal articles from 24 codes
- Advanced tagging with TF-IDF scoring (Bulgarian NLP)
- FREE semantic search (sentence-transformers)
- Contract analysis and GPR calculator
- Flask API + React frontend
- Full documentation and tests
"
```

### 5. Create GitHub Repository
1. Go to: https://github.com/new
2. Repository name: `credit-guardian`
3. Description: `Bulgarian legal analysis platform with AI semantic search`
4. Choose: **Public** or **Private**
5. Do NOT check "Initialize with README"
6. Click "Create repository"

### 6. Connect and Push
```powershell
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/credit-guardian.git

# Push
git push -u origin main
```

**If authentication fails:**
```powershell
# Option A: Use GitHub CLI
gh auth login

# Option B: Use Personal Access Token
# 1. GitHub → Settings → Developer settings → Personal access tokens
# 2. Generate new token (repo scope)
# 3. Use:
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/credit-guardian.git
git push -u origin main
```

---

## Database Distribution Options

Your `credit_guardian.db` is 8.5 MB (already populated with 5,763 articles).

### Option A: Upload to GitHub Releases (Recommended)
1. Compress database:
```powershell
Compress-Archive -Path credit_guardian.db -DestinationPath credit_guardian_db.zip
```

2. Go to: https://github.com/YOUR_USERNAME/credit-guardian/releases
3. Click "Create a new release"
4. Tag: `v1.0.0`
5. Title: "Initial Release - Pre-populated Database"
6. Upload `credit_guardian_db.zip`
7. Add description:
```
Includes:
- 24 Bulgarian legal documents
- 5,763 articles
- 7,980 scored tags
- 5,763 embeddings

Download and extract to project root.
```

### Option B: Let Users Build Their Own
Users run:
```powershell
python import_codexes.py
python enrich_metadata.py
python advanced_tagging.py
python generate_embeddings.py
```
Takes ~30 minutes but ensures fresh data.

---

## Verify Upload Success

After pushing, check on GitHub:
- [ ] All Python files visible
- [ ] Documentation renders correctly
- [ ] No .pyc or __pycache__ files
- [ ] No .venv directory
- [ ] frontend/ has source but not node_modules/
- [ ] No API keys or secrets
- [ ] credit_guardian.db not in repo (or use Git LFS)

---

## Post-Upload Tasks

### 1. Add Repository Topics
Settings → Topics → Add:
- `bulgarian`
- `legal-tech`
- `nlp`
- `semantic-search`
- `sentence-transformers`
- `flask`
- `react`
- `ai`

### 2. Update README.md
Add your GitHub repo URL:
```markdown
## Installation
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/credit-guardian.git
cd credit-guardian
\`\`\`
```

### 3. Add License (Optional)
Create `LICENSE` file:
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge...
```

### 4. Enable GitHub Pages (Optional)
Settings → Pages → Source: main branch /docs folder

---

## Example Full Workflow

```powershell
# 1. Clean and stage
git add .
git status

# 2. Commit
git commit -m "Initial commit: Credit Guardian platform"

# 3. Create repo on GitHub (via web browser)

# 4. Push
git remote add origin https://github.com/YOUR_USERNAME/credit-guardian.git
git push -u origin main

# 5. Compress database
Compress-Archive -Path credit_guardian.db -DestinationPath credit_guardian_db.zip

# 6. Upload to GitHub Releases (via web browser)

# 7. Done! Share your repo
echo "https://github.com/YOUR_USERNAME/credit-guardian"
```

---

## File Size Summary

**Will be uploaded to GitHub:**
- Python source: ~500 KB
- Frontend source: ~100 KB
- Documentation: ~200 KB
- Tests: ~50 KB
- Config files: ~50 KB
- **Total: ~900 KB**

**Will be excluded (.gitignore):**
- credit_guardian.db: 8.5 MB
- .venv/: ~200 MB
- node_modules/: ~300 MB
- __pycache__/: ~5 MB

---

## Troubleshooting

### "File too large"
```powershell
# Remove accidentally added large file
git rm --cached credit_guardian.db
git commit -m "Remove database from repo"
git push
```

### "node_modules uploaded"
```powershell
git rm -r --cached frontend/node_modules
git commit -m "Remove node_modules"
git push
```

### "Permission denied"
- Check SSH key: `ssh -T git@github.com`
- Or use HTTPS with token (see step 6 above)

---

## Success Checklist ✅
- [ ] Repository created on GitHub
- [ ] Code pushed successfully
- [ ] README.md displays correctly
- [ ] No sensitive data visible
- [ ] .gitignore working (no large files)
- [ ] Database uploaded to Releases (optional)
- [ ] Repository topics added
- [ ] License added (optional)

**Your Bulgarian Legal AI Platform is now open source! 🎉**

Share: `https://github.com/YOUR_USERNAME/credit-guardian`
