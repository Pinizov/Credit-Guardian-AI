"""
Initialize Credit Guardian database with all tables including new User/Contract models
Run this after Alembic migrations to ensure all tables are created
"""
from database.models import init_database, engine, Base
from database.legal_models import LegalDocument, LegalArticle, LegalArticleTag
from database.embedding_models import ArticleEmbedding
import sys

def main():
    """Initialize all database tables"""
    try:
        print("🗄️  Initializing Credit Guardian database...")
        print(f"   Database: {engine.url}")
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("✅ All tables created successfully!")
        print("\n📊 Available tables:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
