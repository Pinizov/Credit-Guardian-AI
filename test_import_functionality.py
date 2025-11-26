#!/usr/bin/env python
"""
Test Import Functionality
Тества функционалността на импорт скрипта (без пълен импорт)
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_importer_initialization():
    """Test if importer can be initialized"""
    logger.info("Testing importer initialization...")
    
    try:
        from import_all_legal_data_comprehensive import ComprehensiveLegalDataImporter
        
        legal_data_folder = PROJECT_ROOT / "legal data"
        if legal_data_folder.exists():
            importer = ComprehensiveLegalDataImporter(str(legal_data_folder))
            logger.info("✓ Importer initialized successfully")
            logger.info(f"  - Legal data folder: {importer.legal_data_folder}")
            importer.close()
            return True
        else:
            logger.warning("⚠ Legal data folder not found")
            return False
            
    except Exception as e:
        logger.error(f"✗ Importer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scraper_functionality():
    """Test if scraper can list files"""
    logger.info("Testing scraper functionality...")
    
    try:
        from scrapers.local_folder_scraper import LocalFolderScraper
        
        legal_data_folder = PROJECT_ROOT / "legal data"
        if not legal_data_folder.exists():
            logger.warning("⚠ Legal data folder not found")
            return False
        
        scraper = LocalFolderScraper(str(legal_data_folder))
        files = scraper.list_files()
        
        logger.info(f"✓ Scraper works: found {len(files)} files")
        logger.info(f"  - Sample files: {[f.name for f in files[:3]]}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test API integration (without network calls)"""
    logger.info("Testing API integration...")
    
    try:
        from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
        from scrapers.bulgarian_financial_apis import BulgarianFinancialAPIs
        
        # Test enhanced APIs
        enhanced = EnhancedBulgarianAPIs()
        logger.info(f"✓ Enhanced APIs: {len(enhanced.endpoints)} endpoints configured")
        
        # Test standard APIs
        standard = BulgarianFinancialAPIs()
        logger.info("✓ Standard APIs initialized")
        
        # Test helper methods
        test_text = "Банка Пример АД ЕИК: 123456789"
        bulstat = enhanced._extract_bulstat(test_text)
        if bulstat == "123456789":
            logger.info("✓ BULSTAT extraction works correctly")
        else:
            logger.warning(f"⚠ BULSTAT extraction: expected '123456789', got '{bulstat}'")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_virtual_db_queries():
    """Test virtual database queries"""
    logger.info("Testing virtual database queries...")
    
    try:
        from database.virtual_db import VirtualDatabase
        
        db = VirtualDatabase()
        
        # Test search
        results = db.search_creditors(limit=5)
        logger.info(f"✓ Search works: {results['total']} total creditors")
        
        # Test statistics
        stats = db.get_statistics()
        logger.info(f"✓ Statistics: {stats.get('creditors', {}).get('total', 0)} creditors")
        
        # Test document search
        doc_results = db.search_legal_documents(limit=5)
        logger.info(f"✓ Document search: {doc_results['total']} documents")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Virtual DB queries failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run functionality tests"""
    logger.info("=" * 70)
    logger.info("FUNCTIONALITY TESTS")
    logger.info("=" * 70)
    
    results = []
    
    results.append(("Importer Initialization", test_importer_initialization()))
    results.append(("Scraper Functionality", test_scraper_functionality()))
    results.append(("API Integration", test_api_integration()))
    results.append(("Virtual DB Queries", test_virtual_db_queries()))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("FUNCTIONALITY TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 70)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 70)
    
    if passed == total:
        logger.info("✅ ALL FUNCTIONALITY TESTS PASSED!")
        return 0
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

