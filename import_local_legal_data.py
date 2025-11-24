"""Import legal data from local folder into the database.
Processes files from the Legal Data folder and stores them in the database.
Supports: PDF, CSV, XLS/XLSX, DOC files.
"""
import os
import sys
import logging
from pathlib import Path

# Import database models
from database.models import Base, engine
from database.legal_models import LegalDocument

# Add scrapers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))
from local_folder_scraper import LocalFolderScraper  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_session():
    """Create database session using existing engine."""
    from database.models import SessionLocal
    return SessionLocal()

def get_db_session():
    """Create database session using existing engine."""
    from database.models import SessionLocal
    return SessionLocal()


def import_file_to_db(session, file_data: dict) -> bool:
    """Import a single file's data into the database as LegalDocument.
    
    Args:
        session: Database session
        file_data: Dictionary with file metadata and content
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine document type based on filename patterns
        filename_lower = file_data['filename'].lower()
        if 'law' in filename_lower or 'zakon' in filename_lower:
            doc_type = 'law'
        elif 'ordinance' in filename_lower or 'naredba' in filename_lower:
            doc_type = 'regulation'
        elif 'register' in filename_lower or 'list' in filename_lower:
            doc_type = 'registry'
        else:
            doc_type = 'other'
        
        # Create LegalDocument
        doc = LegalDocument(
            title=file_data['filename'],
            document_type=doc_type,
            full_text=file_data.get('content', ''),
            source_url=f"file:///{file_data['path']}",
            is_active=True
        )
        
        session.add(doc)
        session.commit()
        logger.info(f"✅ Imported: {file_data['filename']} (ID: {doc.id})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing {file_data['filename']}: {e}")
        session.rollback()
        return False


def import_local_legal_data(folder_path: str = r"C:\Users\User\Downloads\Legal Data"):
    """Import all legal data from the specified folder into the database.
    
    Args:
        folder_path: Path to the folder containing legal data
    """
    logger.info("Starting import from: %s", folder_path)
    
    # Check if folder exists
    if not Path(folder_path).exists():
        logger.error("Folder does not exist: %s", folder_path)
        return
    
    # Initialize database tables
    Base.metadata.create_all(engine)
    
    # Initialize scraper
    try:
        scraper = LocalFolderScraper(folder_path)
    except ValueError as e:
        logger.error("Failed to initialize scraper: %s", e)
        return
    
    # Get database session
    session = get_db_session()
    
    # Scrape all files
    logger.info("Scanning folder for legal documents...")
    data = scraper.scrape_all()
    
    # Import each file
    success_count = 0
    error_count = 0
    
    for file_data in data['files']:
        if import_file_to_db(session, file_data):
            success_count += 1
        else:
            error_count += 1
    
    session.close()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Import completed")
    logger.info("  Folder: %s", folder_path)
    logger.info("  Total files found: %d", data['total_files'])
    logger.info("  Successfully imported: %d", success_count)
    logger.info("  Errors: %d", error_count)
    logger.info("=" * 60)


if __name__ == "__main__":
    import_local_legal_data()
