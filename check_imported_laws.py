"""
Check the imported legal documents from ciela.net
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.legal_models import LegalDocument, LegalArticle

# Database setup
engine = create_engine('sqlite:///credit_guardian.db')
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 70)
print("📊 IMPORTED BULGARIAN LAWS - DATABASE STATUS")
print("=" * 70)

# Get all legal documents
docs = session.query(LegalDocument).all()

print(f"\n✅ Total Legal Documents: {len(docs)}")
print(f"✅ Total Legal Articles: {session.query(LegalArticle).count()}")

print("\n" + "=" * 70)
print("📚 IMPORTED LAWS:")
print("=" * 70)

for doc in docs:
    article_count = session.query(LegalArticle).filter_by(document_id=doc.id).count()
    print(f"\n🔹 {doc.title}")
    print(f"   ID: {doc.id}")
    print(f"   Type: {doc.document_type}")
    print(f"   Articles: {article_count}")
    print(f"   Text Length: {len(doc.full_text) if doc.full_text else 0} chars")
    print(f"   URL: {doc.source_url[:80]}...")
    print(f"   Created: {doc.created_at}")

# Show sample articles from Consumer Credit Law
print("\n" + "=" * 70)
print("📖 SAMPLE ARTICLES FROM CONSUMER CREDIT LAW")
print("=" * 70)

consumer_credit_doc = session.query(LegalDocument).filter(
    LegalDocument.title.like('%ПОТРЕБИТЕЛСКИЯ КРЕДИТ%')
).first()

if consumer_credit_doc:
    sample_articles = session.query(LegalArticle).filter_by(
        document_id=consumer_credit_doc.id
    ).limit(5).all()
    
    for article in sample_articles:
        print(f"\n{'=' * 70}")
        print(f"Член {article.article_number}: {article.title}")
        print(f"{'=' * 70}")
        print(article.content[:500] + "..." if len(article.content) > 500 else article.content)

session.close()

print("\n" + "=" * 70)
print("✅ DATABASE CHECK COMPLETE")
print("=" * 70)
