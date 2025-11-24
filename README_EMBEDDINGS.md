# Embedding Pipeline for Bulgarian Legal Codes

This pipeline converts Bulgarian legal articles into vector embeddings for semantic search and AI-powered retrieval (RAG).

## 📋 Overview

The embedding pipeline consists of:

1. **Vector Storage**: `article_embeddings` table with 1536-dimensional vectors
2. **Batch Processor**: `generate_embeddings.py` to generate embeddings via OpenAI API
3. **Semantic Search**: `semantic_search.py` for cosine similarity-based retrieval
4. **Testing Suite**: `test_embedding_pipeline.py` to validate the workflow

## 🗄️ Database Schema

### `article_embeddings` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `article_id` | INTEGER | Foreign key to `legal_articles.id` (unique) |
| `document_id` | INTEGER | Denormalized document ID for faster filtering |
| `model_name` | TEXT | Embedding model (e.g., "text-embedding-3-small") |
| `embedding_dim` | INTEGER | Vector dimension (1536 for text-embedding-3-small) |
| `vector` | TEXT | JSON array of floats: `[0.123, -0.456, ...]` |
| `norm` | REAL | Pre-computed L2 norm for cosine similarity optimization |
| `content_hash` | TEXT | SHA256 hash of article content for change detection |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Indexes**: `article_id`, `document_id`, `model_name`, `content_hash`

## 🚀 Setup

### 1. Install Dependencies

```powershell
pip install requests
```

### 2. Configure OpenAI API Key

```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

### 3. Create Embeddings Table

```powershell
python create_embeddings_table.py
```

**Output:**
```
✓ Table 'article_embeddings' created successfully
  Columns: 10
    - id (INTEGER)
    - article_id (INTEGER)
    ...
  Indexes: 5
```

## 📦 Usage

### Generate Embeddings (Batch Processing)

Process all articles that don't have embeddings or have changed content:

```powershell
python generate_embeddings.py
```

**Features:**
- Batch size: 100 articles per batch
- Rate limiting: 0.1s delay between API calls
- Retry logic: 3 attempts with exponential backoff
- Progress tracking: Real-time feedback per article
- Cost estimation: ~$0.13 per 1M tokens (text-embedding-3-small)

**Example Output:**
```
Embedding Pipeline
Model: text-embedding-3-small (1536 dims)
Batch size: 100

Scanning for articles needing embeddings...
Found 5763 articles to process

Batch 1/58 (100 articles)
  [1/100] Article 1... ✓
  [2/100] Article 2... ✓
  ...
  Batch result: 98 success, 2 failed

...

SUMMARY
  Total processed: 5763
  Success: 5721
  Failed: 42
  Success rate: 99.3%
```

**Cost Estimate:**
- 5,763 articles × ~500 tokens avg = ~2.9M tokens
- Cost: ~$0.38 total (at $0.13 per 1M tokens)

### Semantic Search (Vector Similarity)

#### Option A: Direct Vector Search

Use when you already have an embedding vector:

```python
from semantic_search import search_similar_articles

# Your query vector (1536 dims)
query_vector = [0.123, -0.456, ...]

# Find top 10 similar articles
results = search_similar_articles(
    query_vector=query_vector,
    top_k=10,
    document_id=None,  # Optional: filter by specific document
    min_similarity=0.5  # Optional: minimum cosine similarity threshold
)

for result in results:
    print(f"Article {result['article_id']}: {result['similarity']:.4f}")
    print(f"  Document: {result['document_title']}")
    print(f"  Content: {result['content']}")
    print(f"  Tag: {result['tag_primary']}")
```

#### Option B: Natural Language Search

Use when searching with text query:

```python
from semantic_search import search_by_text
import os

api_key = os.getenv("OPENAI_API_KEY")

# Bulgarian query
results = search_by_text(
    query_text="трудови отношения и заплата",
    api_key=api_key,
    top_k=10,
    document_id=None,
    min_similarity=0.5
)

for result in results:
    print(f"{result['article_number']}: {result['similarity']:.4f}")
```

#### Get Embedding Statistics

```python
from semantic_search import get_embedding_stats

stats = get_embedding_stats()
print(f"Total embeddings: {stats['total_embeddings']}")
print(f"By document: {stats['by_document']}")
```

### Testing

Run the full test suite to validate the pipeline:

```powershell
python test_embedding_pipeline.py
```

**Tests:**
1. **Embedding Generation**: Generates embeddings for 5 sample articles
2. **Similarity Search**: Validates cosine similarity calculation
3. **Natural Language Search**: Tests end-to-end query workflow

**Example Output:**
```
TEST 1: Embedding Generation
✓ API key configured (sk-proj-ab...)
Selected 5 sample articles:
  Article 1 (doc 9): Чл. 1. (1) Корабоплаването...
Processing article 1... ✓
Processing article 2... ✓
...
Generated 5/5 embeddings

TEST 2: Similarity Search
✓ Found 5 embeddings in database
Top 3 similar articles:
1. Article 1 (similarity: 1.0000)
   Document: КОДЕКС НА ТЪРГОВСКОТО КОРАБОПЛАВАНЕ
   ...
✓ Similarity search working correctly

TEST 3: Natural Language Search
Query: 'трудови отношения и заплата'
Found 3 results:
1. Article 3042 (similarity: 0.7234)
   Document: КОДЕКС НА ТРУДА
   ...
✓ Text search working

TEST SUMMARY
  ✓ PASS: Embedding Generation
  ✓ PASS: Similarity Search
  ✓ PASS: Natural Language Search

Total: 3/3 tests passed
🎉 All tests passed! Embedding pipeline is ready.
```

## 🔧 Integration with AI Agent

### RAG Pattern (Retrieval-Augmented Generation)

```python
from semantic_search import search_by_text
import os

def answer_legal_question(question: str) -> str:
    """Answer legal question using RAG pattern."""
    
    # Step 1: Retrieve relevant articles
    api_key = os.getenv("OPENAI_API_KEY")
    articles = search_by_text(
        query_text=question,
        api_key=api_key,
        top_k=5,
        min_similarity=0.6
    )
    
    if not articles:
        return "Не са намерени релевантни статии."
    
    # Step 2: Build context from retrieved articles
    context = "\n\n".join([
        f"[{a['document_title']}, {a['article_number']}]\n{a['full_content']}"
        for a in articles
    ])
    
    # Step 3: Generate answer with LLM
    prompt = f"""Въз основа на следните правни текстове, отговори на въпроса:

{context}

Въпрос: {question}

Отговор:"""
    
    # Call your LLM (OpenAI, Anthropic, etc.)
    # response = llm_client.generate(prompt)
    
    return response
```

### Example Usage in API

```python
from flask import Flask, request, jsonify
from semantic_search import search_by_text

app = Flask(__name__)

@app.route('/api/search', methods=['POST'])
def api_search():
    """Semantic search endpoint."""
    data = request.json
    query = data.get('query')
    top_k = data.get('top_k', 10)
    
    api_key = os.getenv("OPENAI_API_KEY")
    results = search_by_text(query, api_key, top_k=top_k)
    
    return jsonify({
        'query': query,
        'results': results
    })
```

## 📊 Performance Characteristics

### Embedding Generation
- **Throughput**: ~10 articles/second (with 0.1s rate limit)
- **Latency**: ~100ms per API call
- **Cost**: $0.13 per 1M tokens (text-embedding-3-small)
- **Full corpus time**: ~10 minutes for 5,763 articles

### Search Performance
- **Algorithm**: Brute-force cosine similarity (O(n) where n = total embeddings)
- **Latency**: ~50-200ms for 5,763 articles (single-threaded)
- **Memory**: ~44MB for 5,763 × 1536 × 4 bytes (float32)

**Optimization Options** (future):
- FAISS index for approximate nearest neighbor (ANN)
- Quantization to reduce vector size (1536 → 512 dims)
- Pre-filtering by document or tag before similarity computation

## 🐛 Troubleshooting

### Issue: `OPENAI_API_KEY` not set

**Error:**
```
✗ Error: OPENAI_API_KEY environment variable not set
```

**Solution:**
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key"
```

### Issue: Rate limit errors (429)

**Error:**
```
Rate limited. Waiting 2s...
```

**Solutions:**
1. Reduce `BATCH_SIZE` in `generate_embeddings.py` (default: 100)
2. Increase `RETRY_DELAY` for longer backoff
3. Upgrade OpenAI plan for higher rate limits

### Issue: Wrong embedding dimension

**Error:**
```
✗ Wrong dimension: 512 != 1536
```

**Solution:**
Ensure `EMBEDDING_MODEL` in `generate_embeddings.py` is set to `"text-embedding-3-small"` (1536 dims). If using `text-embedding-3-large`, update `EMBEDDING_DIM` to 3072.

### Issue: Slow search performance

**Symptom:** Search takes >1s for large datasets

**Solutions:**
1. Add document filter: `search_similar_articles(..., document_id=9)`
2. Raise `min_similarity` threshold to reduce candidates
3. Implement FAISS index for ANN search (future optimization)

## 📈 Monitoring

### Check Embedding Coverage

```python
import sqlite3
from pathlib import Path

conn = sqlite3.connect("credit_guardian.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        COUNT(DISTINCT ai.article_id) as total_articles,
        COUNT(DISTINCT ae.article_id) as embedded_articles,
        CAST(COUNT(DISTINCT ae.article_id) AS FLOAT) / COUNT(DISTINCT ai.article_id) * 100 as coverage_pct
    FROM article_ingestion ai
    LEFT JOIN article_embeddings ae ON ai.article_id = ae.article_id
""")

row = cursor.fetchone()
print(f"Coverage: {row[1]}/{row[0]} articles ({row[2]:.1f}%)")
```

### Identify Articles Needing Re-embedding

```sql
SELECT 
    ai.article_id,
    ai.document_id,
    ld.title
FROM article_ingestion ai
LEFT JOIN article_embeddings ae ON ai.article_id = ae.article_id
JOIN legal_documents ld ON ai.document_id = ld.id
WHERE ae.id IS NULL
ORDER BY ai.article_id
LIMIT 20;
```

## 🔐 Security Notes

- **API Key Storage**: Never commit `OPENAI_API_KEY` to version control
- **Cost Control**: Monitor OpenAI usage dashboard to avoid unexpected charges
- **Data Privacy**: Embeddings are derived from text but don't expose original content directly

## 📚 References

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [RAG Pattern](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [FAISS (Future Optimization)](https://github.com/facebookresearch/faiss)

## 🎯 Next Steps

1. **Generate embeddings for full corpus**:
   ```powershell
   python generate_embeddings.py
   ```

2. **Integrate with AI agent** (`ai_agent/agent_executor.py`):
   - Add semantic search as tool
   - Use RAG pattern for legal Q&A

3. **Optimize search performance** (optional):
   - Implement FAISS index
   - Add document-level filtering UI
   - Cache frequent queries

4. **Monitor and maintain**:
   - Track embedding coverage
   - Re-embed articles when content changes
   - Archive old embeddings for model upgrades
