"""Check for documents from the local folder specifically."""
from database.models import SessionLocal
from database.legal_models import LegalDocument

def check_local_imports():
    session = SessionLocal()
    
    # Find documents from local folder
    local_docs = session.query(LegalDocument).filter(
        LegalDocument.source_url.like('file:///%')
    ).all()
    
    print(f"\nDocuments from local folder: {len(local_docs)}")
    
    if local_docs:
        print("\nLocal documents:")
        for doc in local_docs[:20]:
            print(f"  - {doc.title[:70]}")
            print(f"    Source: {doc.source_url[:80]}")
    else:
        print("No local folder documents found yet")
    
    session.close()

if __name__ == "__main__":
    check_local_imports()
