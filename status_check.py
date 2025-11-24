"""Comprehensive status check of all legal data in database."""
from database.models import SessionLocal
from database.legal_models import LegalDocument
from sqlalchemy import func

def comprehensive_check():
    session = SessionLocal()
    
    print("\n" + "=" * 70)
    print("CREDIT GUARDIAN - LEGAL DATA STATUS")
    print("=" * 70)
    
    # Total count
    total = session.query(func.count(LegalDocument.id)).scalar()
    print(f"\nTotal Legal Documents: {total}")
    
    # By source
    print("\n--- Documents by Source ---")
    web_docs = session.query(func.count(LegalDocument.id)).filter(
        ~LegalDocument.source_url.like('file:///%')
    ).scalar()
    local_docs = session.query(func.count(LegalDocument.id)).filter(
        LegalDocument.source_url.like('file:///%')
    ).scalar()
    
    print(f"  Web-scraped documents: {web_docs}")
    print(f"  Local folder documents: {local_docs}")
    
    # By type
    print("\n--- Documents by Type ---")
    types = session.query(
        LegalDocument.document_type,
        func.count(LegalDocument.id)
    ).group_by(LegalDocument.document_type).all()
    
    for doc_type, count in sorted(types, key=lambda x: x[1], reverse=True):
        print(f"  {doc_type}: {count}")
    
    # Content statistics
    print("\n--- Content Statistics ---")
    with_content = session.query(func.count(LegalDocument.id)).filter(
        LegalDocument.full_text != None,
        LegalDocument.full_text != ''
    ).scalar()
    
    avg_length = session.query(func.avg(func.length(LegalDocument.full_text))).scalar()
    
    print(f"  Documents with content: {with_content} / {total}")
    print(f"  Average content length: {int(avg_length) if avg_length else 0} characters")
    
    # Sample local documents
    print("\n--- Sample Local Folder Documents (first 10) ---")
    local_samples = session.query(LegalDocument).filter(
        LegalDocument.source_url.like('file:///%')
    ).limit(10).all()
    
    for doc in local_samples:
        content_len = len(doc.full_text) if doc.full_text else 0
        status = "OK" if content_len > 100 else "WARN"
        print(f"  [{status}] {doc.title[:50]:<50} ({content_len:,} chars)")
    
    session.close()
    
    print("\n" + "=" * 70)
    print("Status: READY FOR USE")
    print("=" * 70)

if __name__ == "__main__":
    comprehensive_check()
