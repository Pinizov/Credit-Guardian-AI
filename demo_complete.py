"""
Credit Guardian Platform - Complete Demo
Shows all features working together.
"""

import sqlite3
from pathlib import Path


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_database_stats():
    """Show database statistics."""
    print_header("📊 DATABASE STATUS")
    
    conn = sqlite3.connect("credit_guardian.db")
    cursor = conn.cursor()
    
    # Documents
    cursor.execute("SELECT COUNT(*) FROM legal_documents")
    docs = cursor.fetchone()[0]
    print(f"✓ Legal Documents: {docs} Bulgarian codes")
    
    # Articles
    cursor.execute("SELECT COUNT(*) FROM legal_articles")
    articles = cursor.fetchone()[0]
    print(f"✓ Legal Articles: {articles:,} articles")
    
    # Tags
    cursor.execute("SELECT COUNT(*) FROM legal_article_tags")
    tags = cursor.fetchone()[0]
    print(f"✓ Article Tags: {tags:,} scored tags")
    
    # Embeddings
    cursor.execute("SELECT COUNT(*) FROM article_embeddings")
    embeddings = cursor.fetchone()[0]
    print(f"✓ Embeddings: {embeddings:,} vectors (384-dim)")
    
    # Top documents by article count
    print("\n📚 Top Documents:")
    cursor.execute("""
        SELECT ld.title, COUNT(la.id) as count
        FROM legal_documents ld
        JOIN legal_articles la ON ld.id = la.document_id
        GROUP BY ld.id
        ORDER BY count DESC
        LIMIT 5
    """)
    
    for i, (title, count) in enumerate(cursor.fetchall(), 1):
        print(f"  {i}. {title}: {count} articles")
    
    conn.close()


def demo_tagging_system():
    """Show tagging system with scores."""
    print_header("🏷️  ADVANCED TAGGING SYSTEM")
    
    conn = sqlite3.connect("credit_guardian.db")
    cursor = conn.cursor()
    
    # Tag distribution
    cursor.execute("""
        SELECT tag, COUNT(*) as count
        FROM legal_article_tags
        GROUP BY tag
        ORDER BY count DESC
    """)
    
    print("Tag Distribution (TF-IDF scored):")
    for tag, count in cursor.fetchall():
        print(f"  {tag:30s}: {count:4d} articles")
    
    # Top scored tags
    print("\n🎯 Highest Scored Tags:")
    cursor.execute("""
        SELECT lat.article_id, lat.tag, lat.score, la.article_number, ld.title
        FROM legal_article_tags lat
        JOIN legal_articles la ON lat.article_id = la.id
        JOIN legal_documents ld ON la.document_id = ld.id
        ORDER BY lat.score DESC
        LIMIT 5
    """)
    
    for article_id, tag, score, art_num, doc_title in cursor.fetchall():
        print(f"  Article {art_num} ({doc_title[:40]}...)")
        print(f"    → {tag}: {score:.2f}")
    
    conn.close()


def demo_ingestion_view():
    """Show AI ingestion table."""
    print_header("🤖 AI INGESTION LAYER")
    
    conn = sqlite3.connect("credit_guardian.db")
    cursor = conn.cursor()
    
    # Sample articles with tags
    cursor.execute("""
        SELECT article_id, article_number, tag_primary, tags
        FROM article_ingestion
        WHERE tag_primary IS NOT NULL
        LIMIT 3
    """)
    
    print("Sample Articles Ready for AI:")
    for article_id, art_num, primary_tag, tags_json in cursor.fetchall():
        print(f"\n  Article {art_num} (ID: {article_id})")
        print(f"    Primary Tag: {primary_tag}")
        if tags_json:
            import json
            try:
                tags = json.loads(tags_json)
                print(f"    All Tags: {', '.join([t['tag'] for t in tags[:3]])}")
            except:
                pass
    
    conn.close()


def demo_semantic_search():
    """Show semantic search capabilities."""
    print_header("🔍 SEMANTIC SEARCH (FREE)")
    
    print("Model: paraphrase-multilingual-MiniLM-L12-v2")
    print("Dimensions: 384")
    print("Language: Bulgarian (+ 50+ languages)")
    print("Cost: FREE (local)")
    
    conn = sqlite3.connect("credit_guardian.db")
    cursor = conn.cursor()
    
    # Check embeddings
    cursor.execute("SELECT COUNT(*) FROM article_embeddings")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"\n✓ {count:,} articles embedded and ready for search")
        
        # Sample embedding
        cursor.execute("""
            SELECT ae.article_id, la.article_number, ld.title
            FROM article_embeddings ae
            JOIN legal_articles la ON ae.article_id = la.id
            JOIN legal_documents ld ON la.document_id = ld.id
            LIMIT 1
        """)
        article_id, art_num, doc_title = cursor.fetchone()
        print(f"  Sample: Article {art_num} from {doc_title}")
        
        print("\n💡 Usage:")
        print("  from semantic_search import search_by_text")
        print("  results = search_by_text('трудови отношения', top_k=5)")
    else:
        print(f"\n⚠ No embeddings yet. Run: python generate_embeddings.py")
    
    conn.close()


def demo_code_structure():
    """Show project structure."""
    print_header("📁 PROJECT STRUCTURE")
    
    structure = """
credit-guardian/
├── Core API
│   ├── app.py                    Flask REST API
│   ├── start_server.py          Server launcher
│   └── requirements.txt         Dependencies
│
├── AI & Analysis
│   ├── ai_agent/                LLM integration
│   ├── analyzers/               Contract analysis, GPR calc
│   └── utils/                   Helpers, reports
│
├── Database (SQLite)
│   ├── database/                Models & migrations
│   ├── credit_guardian.db       8.5 MB, 5,763 articles
│   └── Legal Data:
│       ├── legal_documents      24 codes
│       ├── legal_articles       5,763 articles
│       ├── legal_article_tags   7,980 tags
│       └── article_embeddings   5,763 vectors
│
├── Bulgarian Legal Import
│   ├── import_codexes.py        Import 16 codes
│   ├── enrich_metadata.py       Add chapters/sections
│   ├── advanced_tagging.py      TF-IDF scoring
│   └── create_ingestion_view.py Materialize for AI
│
├── FREE Embedding Pipeline
│   ├── generate_embeddings.py   Local model (no API)
│   ├── semantic_search.py       Cosine similarity
│   └── test_embedding_pipeline.py Tests
│
├── Frontend (React)
│   ├── frontend/src/            React components
│   ├── frontend/package.json    Dependencies
│   └── Runs on: http://localhost:5173
│
└── Documentation
    ├── README.md                 Main guide
    ├── README_EMBEDDINGS_FREE.md Embedding guide
    ├── GITHUB_PUBLISHING_GUIDE.md Publishing guide
    └── Tests: tests/
    """
    
    print(structure)


def demo_features():
    """Show key features."""
    print_header("✨ KEY FEATURES")
    
    features = [
        ("🇧🇬 Bulgarian Legal Database", "5,763 articles from 16 official codes"),
        ("🏷️  Advanced Tagging", "TF-IDF scoring with Bulgarian stemmer"),
        ("🔍 Semantic Search", "FREE local model (sentence-transformers)"),
        ("🤖 AI-Ready Data", "Materialized ingestion view with JSON tags"),
        ("📊 Analytics", "Contract analysis, GPR calculator, clause detection"),
        ("🌐 REST API", "Flask backend with full CRUD operations"),
        ("⚛️  Modern UI", "React frontend with charts and dashboards"),
        ("🆓 Zero Cost", "Local embeddings, no API fees"),
        ("🔒 Privacy", "All data stays on your machine"),
        ("🚀 Production-Ready", "Docker support, tests, CI/CD examples"),
    ]
    
    for feature, description in features:
        print(f"{feature:30s} {description}")


def demo_quick_start():
    """Show quick start commands."""
    print_header("🚀 QUICK START")
    
    print("""
1. Clone & Setup:
   git clone https://github.com/YOUR_USERNAME/credit-guardian.git
   cd credit-guardian
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt

2. Database (Option A - Use Existing):
   # Database already populated with 5,763 articles
   # Ready to use immediately

   Database (Option B - Rebuild from Scratch):
   python import_codexes.py          # ~10 minutes
   python enrich_metadata.py         # ~2 minutes
   python advanced_tagging.py        # ~1 minute
   python create_ingestion_view.py   # ~30 seconds

3. Generate Embeddings (FREE):
   pip install sentence-transformers
   python generate_embeddings.py     # ~15 minutes first time

4. Start Backend:
   python start_server.py
   # API: http://localhost:5000

5. Start Frontend:
   cd frontend
   npm install
   npm run dev
   # UI: http://localhost:5173

6. Test Semantic Search:
   python -c "from semantic_search import search_by_text; \\
              results = search_by_text('трудови отношения', top_k=3); \\
              print(results[0]['article_number'])"
    """)


def demo_api_examples():
    """Show API usage examples."""
    print_header("📡 API EXAMPLES")
    
    print("""
# Search creditors
GET http://localhost:5000/api/creditors?search=банка

# Get creditor details
GET http://localhost:5000/api/creditors/1

# Analyze contract
POST http://localhost:5000/api/analyze-contract
{
  "contract_text": "Договор за кредит...",
  "amount": 10000,
  "term": 12
}

# Calculate GPR
POST http://localhost:5000/api/calculate-gpr
{
  "amount": 10000,
  "term": 12,
  "interest_rate": 15.5,
  "fees": {"admin_fee": 100}
}

# Semantic search (NEW)
POST http://localhost:5000/api/semantic-search
{
  "query": "трудови отношения и заплата",
  "top_k": 5
}
    """)


def demo_tech_stack():
    """Show technology stack."""
    print_header("🛠️  TECHNOLOGY STACK")
    
    stack = {
        "Backend": [
            "Python 3.13",
            "Flask - REST API",
            "SQLite - Database",
            "SQLAlchemy - ORM (models only)",
            "Alembic - Migrations"
        ],
        "AI & NLP": [
            "sentence-transformers - FREE embeddings",
            "BeautifulSoup4 - Web scraping",
            "Custom Bulgarian stemmer",
            "TF-IDF scoring",
            "Cosine similarity search"
        ],
        "Frontend": [
            "React 18",
            "Vite - Build tool",
            "Recharts - Visualization",
            "Axios - HTTP client"
        ],
        "DevOps": [
            "Docker & Docker Compose",
            "Pytest - Testing",
            "GitHub Actions - CI/CD (optional)",
            "PowerShell - Automation"
        ],
        "Data": [
            "16 Bulgarian legal codes",
            "5,763 articles",
            "7,980 scored tags",
            "5,763 embeddings (384-dim)"
        ]
    }
    
    for category, items in stack.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")


def main():
    """Run complete demo."""
    print("\n" + "█" * 70)
    print("  CREDIT GUARDIAN - Complete Platform Demo")
    print("  Bulgarian Legal Analysis with AI Semantic Search")
    print("█" * 70)
    
    try:
        demo_database_stats()
        demo_tagging_system()
        demo_ingestion_view()
        demo_semantic_search()
        demo_features()
        demo_tech_stack()
        demo_code_structure()
        demo_api_examples()
        demo_quick_start()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("  1. Review GITHUB_PUBLISHING_GUIDE.md")
        print("  2. Test semantic search: python test_embedding_pipeline.py")
        print("  3. Start server: python start_server.py")
        print("  4. Publish to GitHub: git push origin main")
        print()
        print("Documentation:")
        print("  • README_EMBEDDINGS_FREE.md - Embedding pipeline")
        print("  • GITHUB_PUBLISHING_GUIDE.md - Publishing guide")
        print("  • README.md - Main documentation")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Ensure credit_guardian.db exists in current directory")


if __name__ == "__main__":
    main()
