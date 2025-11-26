#!/usr/bin/env python
"""
Test Script for Integration
Тества всички компоненти на интеграцията
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all modules can be imported"""
    logger.info("=" * 70)
    logger.info("TEST 1: Testing Imports")
    logger.info("=" * 70)
    
    tests = []
    
    # Test database models
    try:
        from database.models import Base, engine, SessionLocal, Creditor
        logger.info("✓ Database models imported")
        tests.append(("Database Models", True))
    except Exception as e:
        logger.error(f"✗ Database models import failed: {e}")
        tests.append(("Database Models", False))
    
    # Test legal models
    try:
        from database.legal_models import LegalDocument, LegalArticle
        logger.info("✓ Legal models imported")
        tests.append(("Legal Models", True))
    except Exception as e:
        logger.error(f"✗ Legal models import failed: {e}")
        tests.append(("Legal Models", False))
    
    # Test enhanced APIs
    try:
        from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
        logger.info("✓ Enhanced APIs imported")
        tests.append(("Enhanced APIs", True))
    except Exception as e:
        logger.error(f"✗ Enhanced APIs import failed: {e}")
        tests.append(("Enhanced APIs", False))
    
    # Test virtual database
    try:
        from database.virtual_db import VirtualDatabase
        logger.info("✓ Virtual database imported")
        tests.append(("Virtual Database", True))
    except Exception as e:
        logger.error(f"✗ Virtual database import failed: {e}")
        tests.append(("Virtual Database", False))
    
    # Test data optimizer
    try:
        from database.data_optimizer import DataOptimizer
        logger.info("✓ Data optimizer imported")
        tests.append(("Data Optimizer", True))
    except Exception as e:
        logger.error(f"✗ Data optimizer import failed: {e}")
        tests.append(("Data Optimizer", False))
    
    # Test comprehensive importer
    try:
        from import_all_legal_data_comprehensive import ComprehensiveLegalDataImporter
        logger.info("✓ Comprehensive importer imported")
        tests.append(("Comprehensive Importer", True))
    except Exception as e:
        logger.error(f"✗ Comprehensive importer import failed: {e}")
        tests.append(("Comprehensive Importer", False))
    
    # Summary
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Import Tests: {passed}/{total} passed")
    logger.info("=" * 70)
    
    return passed == total

def test_database_connection():
    """Test database connection"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Testing Database Connection")
    logger.info("=" * 70)
    
    try:
        from database.models import SessionLocal, Creditor
        from database.legal_models import LegalDocument
        
        session = SessionLocal()
        
        # Test query
        creditor_count = session.query(Creditor).count()
        doc_count = session.query(LegalDocument).count()
        
        logger.info(f"✓ Database connection successful")
        logger.info(f"  - Creditors in database: {creditor_count}")
        logger.info(f"  - Legal documents in database: {doc_count}")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False

def test_virtual_database():
    """Test virtual database interface"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Testing Virtual Database")
    logger.info("=" * 70)
    
    try:
        from database.virtual_db import VirtualDatabase
        
        db = VirtualDatabase()
        
        # Test search
        results = db.search_creditors(limit=5)
        logger.info(f"✓ Search creditors: {results['total']} total, {results['count']} returned")
        
        # Test statistics
        stats = db.get_statistics()
        logger.info(f"✓ Get statistics: {len(stats)} categories")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Virtual database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_apis():
    """Test enhanced APIs (without actual network calls)"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Testing Enhanced APIs (Initialization)")
    logger.info("=" * 70)
    
    try:
        from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
        
        api = EnhancedBulgarianAPIs()
        logger.info(f"✓ Enhanced APIs initialized")
        logger.info(f"  - Endpoints configured: {len(api.endpoints)}")
        
        # Test helper methods
        bulstat = api._extract_bulstat("Test Company ЕИК: 123456789")
        if bulstat == "123456789":
            logger.info("✓ BULSTAT extraction works")
        else:
            logger.warning(f"⚠ BULSTAT extraction returned: {bulstat}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced APIs test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_optimizer():
    """Test data optimizer (initialization only)"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Testing Data Optimizer")
    logger.info("=" * 70)
    
    try:
        from database.data_optimizer import DataOptimizer
        
        optimizer = DataOptimizer()
        logger.info("✓ Data optimizer initialized")
        
        # Don't run full optimization in test, just check it can be created
        return True
        
    except Exception as e:
        logger.error(f"✗ Data optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legal_data_folder():
    """Test if legal data folder exists and has files"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 6: Testing Legal Data Folder")
    logger.info("=" * 70)
    
    legal_data_folder = PROJECT_ROOT / "legal data"
    
    if not legal_data_folder.exists():
        logger.warning(f"⚠ Legal data folder not found: {legal_data_folder}")
        return False
    
    # Count files
    files = list(legal_data_folder.glob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    logger.info(f"✓ Legal data folder exists")
    logger.info(f"  - Total files: {file_count}")
    
    # List file types
    extensions = {}
    for f in files:
        if f.is_file():
            ext = f.suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1
    
    logger.info(f"  - File types: {dict(extensions)}")
    
    return True

def main():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("INTEGRATION TESTS")
    logger.info("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Virtual Database", test_virtual_database()))
    results.append(("Enhanced APIs", test_enhanced_apis()))
    results.append(("Data Optimizer", test_data_optimizer()))
    results.append(("Legal Data Folder", test_legal_data_folder()))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
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
        logger.info("✅ ALL TESTS PASSED!")
        return 0
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

