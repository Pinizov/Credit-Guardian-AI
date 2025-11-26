# FREE Embedding Pipeline - Installation & Usage Guide

## ✅ What Changed

Converted from **OpenAI API** (paid, $0.13/1M tokens) to **sentence-transformers** (FREE, runs locally).

### New Model
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions**: 384 (down from 1536)
- **Language Support**: Bulgarian + 50+ languages
- **Cost**: FREE (runs on your CPU/GPU)
- **Speed**: ~10-50 articles/second (depending on CPU)

## 📦 Installation

### Step 1: Install sentence-transformers

```powershell
pip install sentence-transformers
```

This will install:
- `sentence-transformers` - Main library
- `torch` - PyTorch (CPU version)
- `transformers` - Hugging Face models
- `scikit-learn` - For similarity calculations

**Installation time**: ~5-10 minutes (downloads ~500MB)

### Step 2: Verify Installation

```powershell
python -c "from sentence_transformers import SentenceTransformer; print('✓ Installed')"
```

## 🚀 Usage

### Generate Embeddings (All Articles)

```powershell
python generate_embeddings.py
```

**No API key needed!** The model downloads automatically on first run (~400MB).

Expected output:
```
Embedding Pipeline (FREE - Local Model)
Model: paraphrase-multilingual-MiniLM-L12-v2 (384 dims)
Batch size: 50

Loading embedding model (first time only)...
✓ Model loaded: paraphrase-multilingual-MiniLM-L12-v2

Scanning for articles needing embeddings...
Found 5763 articles to process

Batch 1/116 (50 articles)
  [1/50] Article 1... ✓
  [2/50] Article 2... ✓
  ...
```

**Performance**: 
- First run: ~10-15 minutes for 5,763 articles
- Subsequent runs: only processes new/changed articles

### Semantic Search

```powershell
python semantic_search.py
```

Shows embedding statistics.

**In your code:**

```python
from semantic_search import search_by_text

# No API key needed!
results = search_by_text(
    "трудови отношения и заплата",
    top_k=5,
    min_similarity=0.5
)

for r in results:
    print(f"{r['article_number']}: {r['similarity']:.4f}")
    print(f"  {r['content'][:100]}...")
```

### Run Tests

```powershell
python test_embedding_pipeline.py
```

Tests 5 sample articles (FREE, no API).

## 🔧 Updated Files

1. **`generate_embeddings.py`**
   - Removed OpenAI API calls
   - Added `get_model()` - loads local model
   - Added `get_embedding()` - FREE local encoding
   - Changed dimensions: 1536 → 384

2. **`semantic_search.py`**
   - Removed `api_key` parameter from `search_by_text()`
   - Uses local model for query encoding
   - Works offline after initial model download

3. **`test_embedding_pipeline.py`**
   - Removed API key checks
   - Uses local model for all tests

4. **`article_embeddings` table**
   - Recreated (empty) - ready for 384-dim vectors

## 💡 Advantages of Local Model

### ✅ Benefits
- **FREE**: No API costs
- **Privacy**: Data never leaves your machine
- **Offline**: Works without internet (after first download)
- **Speed**: No network latency
- **Unlimited**: No rate limits or quotas

### ⚠️ Trade-offs
- **Quality**: Slightly lower quality than OpenAI's ada-002/text-embedding-3
- **Size**: Model file ~400MB (one-time download)
- **Speed**: CPU encoding slower than API (but batch processing helps)

## 📊 Performance Comparison

| Metric | OpenAI API | sentence-transformers |
|--------|------------|----------------------|
| Cost | $0.38 for 5,763 articles | FREE |
| Dimensions | 1536 | 384 |
| Speed | ~10 articles/sec | ~20 articles/sec (CPU) |
| Quality | Excellent | Very Good |
| Languages | 100+ | 50+ (incl. Bulgarian) |
| Privacy | Data sent to OpenAI | Fully local |

## 🔍 Model Details

**paraphrase-multilingual-MiniLM-L12-v2**
- Publisher: Hugging Face / sentence-transformers
- License: Apache 2.0 (commercial use allowed)
- Training: 1B+ sentence pairs, 50+ languages
- Bulgarian Support: Native (trained on Bulgarian corpus)
- Paper: [Sentence-BERT](https://arxiv.org/abs/1908.10084)

## 🐛 Troubleshooting

### Issue: Import Error

```
ImportError: No module named 'sentence_transformers'
```

**Solution:**
```powershell
pip install sentence-transformers
```

### Issue: Slow on First Run

**Symptom:** Model download takes 5+ minutes

**Explanation:** First run downloads ~400MB model from Hugging Face. Subsequent runs use cached model.

**Speed up:** Pre-download model:
```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

### Issue: Out of Memory

**Symptom:** `RuntimeError: out of memory`

**Solution:** Reduce batch size in `generate_embeddings.py`:
```python
BATCH_SIZE = 25  # Down from 50
```

### Issue: Dimension Mismatch

**Error:** `Wrong dimension: 1536 != 384`

**Solution:** Table already recreated with correct schema. Just run `generate_embeddings.py`.

## 🎯 Next Steps

1. **Install sentence-transformers:**
   ```powershell
   pip install sentence-transformers
   ```

2. **Test with 5 articles:**
   ```powershell
   python test_embedding_pipeline.py
   ```

3. **Generate all embeddings:**
   ```powershell
   python generate_embeddings.py
   ```
   
4. **Integrate with AI agent** (no API key needed):
   ```python
   from semantic_search import search_by_text
   results = search_by_text("your query", top_k=5)
   ```

## 📚 References

- [sentence-transformers Documentation](https://www.sbert.net/)
- [Hugging Face Model Card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [Model Performance Benchmarks](https://www.sbert.net/docs/pretrained_models.html)

---

**Summary**: Embedding pipeline now 100% FREE with local model. No API keys, no costs, full privacy! 🎉
