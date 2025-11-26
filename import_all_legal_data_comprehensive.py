#!/usr/bin/env python
"""
Comprehensive Legal Data Import Script
Импортира всички данни от legal data папката в базата данни
Поддържа: PDF, DOCX, DOC, RTF, XLS, XLSX, CSV
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Base, engine, SessionLocal
from database.legal_models import LegalDocument, LegalArticle, ConsumerCase
from database.models import Creditor
from scrapers.local_folder_scraper import LocalFolderScraper
from scrapers.bulgarian_financial_apis import BulgarianFinancialAPIs

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveLegalDataImporter:
    """Comprehensive importer for all legal data files"""
    
    def __init__(self, legal_data_folder: str = "legal data"):
        self.legal_data_folder = Path(legal_data_folder)
        self.session = SessionLocal()
        self.api = BulgarianFinancialAPIs()
        self.stats = {
            'total_files': 0,
            'imported_documents': 0,
            'imported_creditors': 0,
            'imported_articles': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def extract_document_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from filename"""
        filename_lower = filename.lower()
        metadata = {
            'document_type': 'other',
            'document_number': None,
            'is_law': False,
            'is_register': False,
            'is_ordinance': False
        }
        
        # Determine document type
        if 'zakon' in filename_lower:
            metadata['document_type'] = 'law'
            metadata['is_law'] = True
        elif 'naredba' in filename_lower or 'ordinance' in filename_lower:
            metadata['document_type'] = 'regulation'
            metadata['is_ordinance'] = True
        elif 'register' in filename_lower or 'list' in filename_lower or 'bs_' in filename_lower or 'rs_' in filename_lower:
            metadata['document_type'] = 'registry'
            metadata['is_register'] = True
        elif 'kodeks' in filename_lower or 'codex' in filename_lower:
            metadata['document_type'] = 'codex'
        elif 'ciela' in filename_lower:
            metadata['document_type'] = 'reference'
        
        # Extract document number if present
        import re
        number_match = re.search(r'(\d+)', filename)
        if number_match:
            metadata['document_number'] = number_match.group(1)
        
        return metadata
    
    def import_legal_document(self, file_data: Dict[str, Any]) -> Optional[int]:
        """Import a legal document file into database"""
        try:
            filename = file_data['filename']
            content = file_data.get('content', '')
            file_path = file_data.get('path', '')
            
            # Skip if content is too short or indicates extraction failure
            if not content or len(content) < 50 or '[PDF file' in content or '[Excel file' in content:
                logger.warning(f"⚠️ Skipping {filename}: insufficient content")
                self.stats['skipped'] += 1
                return None
            
            # Extract metadata
            metadata = self.extract_document_metadata(filename)
            
            # Check if document already exists
            existing = self.session.query(LegalDocument).filter_by(
                title=filename,
                source_url=f"file:///{file_path}"
            ).first()
            
            if existing:
                logger.info(f"⏭️ Already exists: {filename}")
                return existing.id
            
            # Create document
            doc = LegalDocument(
                title=filename,
                document_type=metadata['document_type'],
                document_number=metadata['document_number'],
                full_text=content[:50000] if len(content) > 50000 else content,  # Limit text size
                source_url=f"file:///{file_path}",
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self.session.add(doc)
            self.session.commit()
            
            logger.info(f"✅ Imported document: {filename} (ID: {doc.id})")
            self.stats['imported_documents'] += 1
            return doc.id
            
        except Exception as e:
            logger.error(f"❌ Error importing {file_data.get('filename', 'unknown')}: {e}")
            self.session.rollback()
            self.stats['errors'] += 1
            return None
    
    def import_register_files(self, file_data: Dict[str, Any]) -> int:
        """Import register files (XLS, XLSX, DOC) and extract creditors"""
        try:
            filename = file_data['filename']
            file_path = Path(file_data.get('path', ''))
            
            # Only process register files
            if not any(x in filename.lower() for x in ['register', 'list', 'bs_', 'rs_']):
                return 0
            
            logger.info(f"📋 Processing register file: {filename}")
            
            # Use BulgarianFinancialAPIs to parse register
            file_paths = {filename: file_path}
            creditors = self.api.parse_local_registers(file_paths)
            
            if not creditors:
                return 0
            
            # Standardize and deduplicate
            standardized = self.api.standardize_creditor_data(creditors)
            
            # Import creditors
            from database.models import Creditor
            imported_count = 0
            
            for creditor_data in standardized:
                try:
                    # Check if exists
                    bulstat = creditor_data.get('bulstat')
                    name = creditor_data.get('name', '').strip()
                    
                    if not name:
                        continue
                    
                    existing = None
                    if bulstat:
                        existing = self.session.query(Creditor).filter_by(bulstat=bulstat).first()
                    else:
                        existing = self.session.query(Creditor).filter_by(name=name).first()
                    
                    if existing:
                        # Update existing
                        for key, value in creditor_data.items():
                            if value and not getattr(existing, key, None):
                                setattr(existing, key, value)
                        imported_count += 1
                    else:
                        # Create new
                        creditor = Creditor(
                            name=name,
                            type=creditor_data.get('type', 'unknown'),
                            bulstat=bulstat,
                            license_number=creditor_data.get('license_number'),
                            address=creditor_data.get('address'),
                            violations_count=0,
                            risk_score=0.0,
                            is_blacklisted=False
                        )
                        self.session.add(creditor)
                        imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error importing creditor {creditor_data.get('name')}: {e}")
                    continue
            
            self.session.commit()
            logger.info(f"✅ Imported {imported_count} creditors from {filename}")
            self.stats['imported_creditors'] += imported_count
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Error processing register {file_data.get('filename')}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def import_all_files(self) -> Dict[str, Any]:
        """Import all files from legal data folder"""
        logger.info("=" * 70)
        logger.info("COMPREHENSIVE LEGAL DATA IMPORT")
        logger.info("=" * 70)
        
        # Initialize database
        Base.metadata.create_all(engine)
        logger.info("✓ Database initialized")
        
        # Initialize scraper
        if not self.legal_data_folder.exists():
            logger.error(f"❌ Folder does not exist: {self.legal_data_folder}")
            return self.stats
        
        scraper = LocalFolderScraper(str(self.legal_data_folder))
        
        # Get all files
        logger.info(f"\n📁 Scanning folder: {self.legal_data_folder}")
        data = scraper.scrape_all()
        self.stats['total_files'] = data['total_files']
        
        logger.info(f"✓ Found {self.stats['total_files']} files\n")
        
        # Process each file
        for i, file_data in enumerate(data['files'], 1):
            filename = file_data.get('filename', 'unknown')
            logger.info(f"[{i}/{self.stats['total_files']}] Processing: {filename}")
            
            # Import as legal document
            doc_id = self.import_legal_document(file_data)
            
            # If it's a register file, also extract creditors
            if any(x in filename.lower() for x in ['register', 'list', 'bs_', 'rs_']):
                self.import_register_files(file_data)
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total files processed: {self.stats['total_files']}")
        logger.info(f"Documents imported: {self.stats['imported_documents']}")
        logger.info(f"Creditors imported: {self.stats['imported_creditors']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info("=" * 70)
        
        return self.stats
    
    def close(self):
        """Close database session"""
        self.session.close()


def main():
    """Main entry point"""
    # Use current directory's legal data folder
    legal_data_folder = PROJECT_ROOT / "legal data"
    
    if not legal_data_folder.exists():
        logger.error(f"Legal data folder not found: {legal_data_folder}")
        logger.info("Please ensure the 'legal data' folder exists in the project root")
        return
    
    importer = ComprehensiveLegalDataImporter(str(legal_data_folder))
    
    try:
        stats = importer.import_all_files()
        
        # Save statistics
        stats_file = PROJECT_ROOT / "data" / "import_stats.json"
        stats_file.parent.mkdir(exist_ok=True)
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        
        logger.info(f"\n✓ Statistics saved to: {stats_file}")
        
    finally:
        importer.close()


if __name__ == "__main__":
    main()

