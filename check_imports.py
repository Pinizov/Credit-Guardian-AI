"""Check what was imported into the database."""
from database.models import SessionLocal
from database.legal_models import LegalDocument
from sqlalchemy import func

def check_imports():
    session = SessionLocal()
    
    # Count documents
    total = session.query(func.count(LegalDocument.id)).scalar()
    print(f"\n📊 Database Status")
    print("=" * 60)
    print(f"Total Legal Documents: {total}")
    
    if total > 0:
        # Get sample documents
        docs = session.query(LegalDocument).limit(10).all()
        
        print(f"\n📄 Sample Documents (showing first 10):")
        print("-" * 60)
        
        for doc in docs:
            content_preview = doc.full_text[:100] if doc.full_text else "[no content]"
            print(f"\nID: {doc.id}")
            print(f"Title: {doc.title}")
            print(f"Type: {doc.document_type}")
            print(f"Content preview: {content_preview}...")
            print(f"Source: {doc.source_url}")
        
        # Count by type
        print(f"\n📈 Documents by Type:")
        print("-" * 60)
        types = session.query(
            LegalDocument.document_type,
            func.count(LegalDocument.id)
        ).group_by(LegalDocument.document_type).all()
        
        for doc_type, count in types:
            print(f"  {doc_type}: {count}")
    
    session.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_imports()
