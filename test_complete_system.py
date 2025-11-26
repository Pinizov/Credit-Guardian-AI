#!/usr/bin/env python
"""
Complete System Test
Тества всички модули, бази данни, скриптове и функционалности
"""

import sys
import os
import logging
from pathlib import Path
import traceback

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Test results
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_result(name, success, error=None, warning=None):
    """Record test result"""
    if success:
        results['passed'].append(name)
        logger.info(f"✅ PASS: {name}")
    elif warning:
        results['warnings'].append((name, warning))
        logger.warning(f"⚠️ WARN: {name} - {warning}")
    else:
        results['failed'].append((name, error))
        logger.error(f"❌ FAIL: {name} - {error}")

def test_module_imports():
    """Test 1: Module imports"""
    logger.info("=" * 70)
    logger.info("TEST 1: Module Imports")
    logger.info("=" * 70)
    
    modules = [
        ('database.models', ['Base', 'engine', 'SessionLocal', 'Creditor', 'Violation']),
        ('database.legal_models', ['LegalDocument', 'LegalArticle']),
        ('database.virtual_db', ['VirtualDatabase']),
        ('database.data_optimizer', ['DataOptimizer']),
        ('scrapers.enhanced_bulgarian_apis', ['EnhancedBulgarianAPIs']),
        ('scrapers.bulgarian_financial_apis', ['BulgarianFinancialAPIs']),
        ('scrapers.local_folder_scraper', ['LocalFolderScraper']),
        ('import_all_legal_data_comprehensive', ['ComprehensiveLegalDataImporter']),
    ]
    
    for module_name, items in modules:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if not hasattr(module, item):
                    test_result(f"{module_name}.{item}", False, f"Missing attribute {item}")
                    return False
            test_result(f"Import {module_name}", True)
        except Exception as e:
            test_result(f"Import {module_name}", False, str(e))
            return False
    
    return True

def test_database_connection():
    """Test 2: Database connection"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Database Connection")
    logger.info("=" * 70)
    
    try:
        from database.models import SessionLocal, Creditor
        from database.legal_models import LegalDocument
        
        session = SessionLocal()
        
        # Test query
        creditor_count = session.query(Creditor).count()
        doc_count = session.query(LegalDocument).count()
        
        logger.info(f"  - Creditors: {creditor_count}")
        logger.info(f"  - Legal documents: {doc_count}")
        
        session.close()
        test_result("Database Connection", True)
        return True
    except Exception as e:
        test_result("Database Connection", False, str(e))
        traceback.print_exc()
        return False

def test_database_models():
    """Test 3: Database models structure"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Database Models")
    logger.info("=" * 70)
    
    try:
        from database.models import (
            Creditor, Violation, UnfairClause, CourtCase,
            CreditProduct, User, Contract, Fee, ContractViolation,
            Complaint, Payment
        )
        from database.legal_models import (
            LegalDocument, LegalArticle, ConsumerCase, TrainingExample, LegalArticleTag
        )
        
        # Check if tables exist
        from database.models import Base, engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'creditors', 'violations', 'unfair_clauses', 'court_cases',
            'credit_products', 'users', 'contracts', 'fees',
            'contract_violations', 'complaints', 'payments',
            'legal_documents', 'legal_articles', 'consumer_cases'
        ]
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            test_result("Database Models", False, f"Missing tables: {missing}")
            return False
        
        logger.info(f"  - Found {len(tables)} tables")
        test_result("Database Models", True)
        return True
    except Exception as e:
        test_result("Database Models", False, str(e))
        traceback.print_exc()
        return False

def test_virtual_database():
    """Test 4: Virtual database interface"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Virtual Database")
    logger.info("=" * 70)
    
    try:
        from database.virtual_db import VirtualDatabase
        
        db = VirtualDatabase()
        
        # Test search
        results = db.search_creditors(limit=5)
        logger.info(f"  - Search works: {results['total']} creditors")
        
        # Test statistics
        stats = db.get_statistics()
        logger.info(f"  - Statistics: {len(stats)} categories")
        
        # Test document search
        doc_results = db.search_legal_documents(limit=5)
        logger.info(f"  - Document search: {doc_results['total']} documents")
        
        db.close()
        test_result("Virtual Database", True)
        return True
    except Exception as e:
        test_result("Virtual Database", False, str(e))
        traceback.print_exc()
        return False

def test_api_modules():
    """Test 5: API modules"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: API Modules")
    logger.info("=" * 70)
    
    try:
        from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
        from scrapers.bulgarian_financial_apis import BulgarianFinancialAPIs
        
        # Test initialization
        enhanced = EnhancedBulgarianAPIs()
        logger.info(f"  - Enhanced APIs: {len(enhanced.endpoints)} endpoints")
        
        standard = BulgarianFinancialAPIs()
        logger.info("  - Standard APIs initialized")
        
        # Test helper methods
        test_text = "Банка Пример АД ЕИК: 123456789"
        bulstat = enhanced._extract_bulstat(test_text)
        if bulstat == "123456789":
            logger.info("  - BULSTAT extraction works")
        else:
            test_result("API Modules", False, f"BULSTAT extraction failed: got {bulstat}")
            return False
        
        test_result("API Modules", True)
        return True
    except Exception as e:
        test_result("API Modules", False, str(e))
        traceback.print_exc()
        return False

def test_data_optimizer():
    """Test 6: Data optimizer"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 6: Data Optimizer")
    logger.info("=" * 70)
    
    try:
        from database.data_optimizer import DataOptimizer
        
        optimizer = DataOptimizer()
        logger.info("  - Data optimizer initialized")
        
        # Don't run full optimization, just check it can be created
        test_result("Data Optimizer", True)
        return True
    except Exception as e:
        test_result("Data Optimizer", False, str(e))
        traceback.print_exc()
        return False

def test_import_scripts():
    """Test 7: Import scripts"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 7: Import Scripts")
    logger.info("=" * 70)
    
    scripts = [
        'import_all_legal_data_comprehensive',
        'import_creditors_from_apis',
        'import_local_legal_data',
    ]
    
    all_ok = True
    for script_name in scripts:
        try:
            script_path = PROJECT_ROOT / f"{script_name}.py"
            if not script_path.exists():
                test_result(f"Script {script_name}", False, "File not found")
                all_ok = False
                continue
            
            # Try to import
            module = __import__(script_name, fromlist=[])
            logger.info(f"  - {script_name}.py: OK")
            test_result(f"Script {script_name}", True)
        except Exception as e:
            test_result(f"Script {script_name}", False, str(e))
            all_ok = False
    
    return all_ok

def test_scrapers():
    """Test 8: Scrapers"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 8: Scrapers")
    logger.info("=" * 70)
    
    scrapers = [
        'scrapers.local_folder_scraper',
        'scrapers.enhanced_bulgarian_apis',
        'scrapers.bulgarian_financial_apis',
    ]
    
    all_ok = True
    for scraper_name in scrapers:
        try:
            module = __import__(scraper_name, fromlist=[])
            logger.info(f"  - {scraper_name}: OK")
            test_result(f"Scraper {scraper_name}", True)
        except Exception as e:
            test_result(f"Scraper {scraper_name}", False, str(e))
            all_ok = False
    
    return all_ok

def test_legal_data_folder():
    """Test 9: Legal data folder"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 9: Legal Data Folder")
    logger.info("=" * 70)
    
    legal_data_folder = PROJECT_ROOT / "legal data"
    
    if not legal_data_folder.exists():
        test_result("Legal Data Folder", False, "Folder not found")
        return False
    
    # Count files
    files = list(legal_data_folder.glob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    logger.info(f"  - Total files: {file_count}")
    
    if file_count == 0:
        test_result("Legal Data Folder", False, "No files found")
        return False
    
    # List file types
    extensions = {}
    for f in files:
        if f.is_file():
            ext = f.suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1
    
    logger.info(f"  - File types: {dict(extensions)}")
    test_result("Legal Data Folder", True)
    return True

def test_comprehensive_importer():
    """Test 10: Comprehensive importer initialization"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 10: Comprehensive Importer")
    logger.info("=" * 70)
    
    try:
        from import_all_legal_data_comprehensive import ComprehensiveLegalDataImporter
        
        legal_data_folder = PROJECT_ROOT / "legal data"
        if legal_data_folder.exists():
            importer = ComprehensiveLegalDataImporter(str(legal_data_folder))
            logger.info("  - Importer initialized")
            importer.close()
            test_result("Comprehensive Importer", True)
            return True
        else:
            test_result("Comprehensive Importer", False, "Legal data folder not found")
            return False
    except Exception as e:
        test_result("Comprehensive Importer", False, str(e))
        traceback.print_exc()
        return False

def test_local_folder_scraper():
    """Test 11: Local folder scraper"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 11: Local Folder Scraper")
    logger.info("=" * 70)
    
    try:
        from scrapers.local_folder_scraper import LocalFolderScraper
        
        legal_data_folder = PROJECT_ROOT / "legal data"
        if not legal_data_folder.exists():
            test_result("Local Folder Scraper", False, "Legal data folder not found")
            return False
        
        scraper = LocalFolderScraper(str(legal_data_folder))
        files = scraper.list_files()
        
        logger.info(f"  - Found {len(files)} files")
        if len(files) > 0:
            logger.info(f"  - Sample: {files[0].name}")
        
        test_result("Local Folder Scraper", True)
        return True
    except Exception as e:
        test_result("Local Folder Scraper", False, str(e))
        traceback.print_exc()
        return False

def test_database_file():
    """Test 12: Database file exists"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 12: Database File")
    logger.info("=" * 70)
    
    db_file = PROJECT_ROOT / "credit_guardian.db"
    
    if db_file.exists():
        size = db_file.stat().st_size
        logger.info(f"  - Database file exists: {size:,} bytes")
        test_result("Database File", True)
        return True
    else:
        test_result("Database File", False, "Database file not found")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("COMPLETE SYSTEM TEST")
    logger.info("=" * 70)
    
    # Run all tests
    tests = [
        ("Module Imports", test_module_imports),
        ("Database Connection", test_database_connection),
        ("Database Models", test_database_models),
        ("Virtual Database", test_virtual_database),
        ("API Modules", test_api_modules),
        ("Data Optimizer", test_data_optimizer),
        ("Import Scripts", test_import_scripts),
        ("Scrapers", test_scrapers),
        ("Legal Data Folder", test_legal_data_folder),
        ("Comprehensive Importer", test_comprehensive_importer),
        ("Local Folder Scraper", test_local_folder_scraper),
        ("Database File", test_database_file),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}")
            traceback.print_exc()
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    total = len(results['passed']) + len(results['failed']) + len(results['warnings'])
    passed = len(results['passed'])
    failed = len(results['failed'])
    warnings = len(results['warnings'])
    
    logger.info(f"Total Tests: {total}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"⚠️ Warnings: {warnings}")
    
    if failed > 0:
        logger.info("\nFailed Tests:")
        for name, error in results['failed']:
            logger.info(f"  - {name}: {error}")
    
    if warnings > 0:
        logger.info("\nWarnings:")
        for name, warning in results['warnings']:
            logger.info(f"  - {name}: {warning}")
    
    logger.info("=" * 70)
    
    if failed == 0:
        logger.info("✅ ALL TESTS PASSED!")
        return 0
    else:
        logger.error(f"❌ {failed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

