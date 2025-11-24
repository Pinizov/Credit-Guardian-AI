"""Streamlined import with progress tracking."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

from pathlib import Path
from database.models import Base, engine, SessionLocal
from database.legal_models import LegalDocument
from local_folder_scraper import LocalFolderScraper

def quick_import():
    folder_path = r"C:\Users\User\Downloads\Legal Data"
    
    print(f"Starting quick import from: {folder_path}\n")
    
    # Initialize database
    Base.metadata.create_all(engine)
    session = SessionLocal()
    
    # Scan files
    scraper = LocalFolderScraper(folder_path)
    print("Scanning folder...")
    data = scraper.scrape_all()
    
    print(f"\nFound {data['total_files']} files\n")
    
    # Import to database
    success = 0
    skipped = 0
    errors = 0
    
    for i, file_data in enumerate(data['files'], 1):
        filename = file_data['filename']
        print(f"[{i}/{data['total_files']}] Processing: {filename[:50]}...")
        
        try:
            # Skip if content is too small or error message
            content = file_data.get('content', '')
            if len(content) < 20 or 'extraction failed' in content.lower():
                print("  Skipped (no content)")
                skipped += 1
                continue
            
            # Determine document type
            fn_lower = filename.lower()
            if 'law' in fn_lower or 'zakon' in fn_lower:
                doc_type = 'law'
            elif 'ordinance' in fn_lower or 'naredba' in fn_lower:
                doc_type = 'regulation'
            elif 'register' in fn_lower or 'list' in fn_lower:
                doc_type = 'registry'
            else:
                doc_type = 'other'
            
            # Create document
            doc = LegalDocument(
                title=filename,
                document_type=doc_type,
                full_text=content[:50000],  # Limit to 50k chars
                source_url=f"file:///{file_data['path']}",
                is_active=True
            )
            
            session.add(doc)
            session.commit()
            print(f"  Saved as ID {doc.id}")
            success += 1
            
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
            session.rollback()
            errors += 1
    
    session.close()
    
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"  Total files: {data['total_files']}")
    print(f"  Successfully imported: {success}")
    print(f"  Skipped (no content): {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 60)

if __name__ == "__main__":
    quick_import()
