#!/usr/bin/env python
"""
Unified Integration Script
Обединява всички източници данни в една система
- Импортира данни от legal data папката
- Синхронизира с реални API
- Оптимизира структурата на данните
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from import_all_legal_data_comprehensive import ComprehensiveLegalDataImporter
from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
from database.data_optimizer import DataOptimizer
from database.virtual_db import VirtualDatabase

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main integration function"""
    logger.info("=" * 70)
    logger.info("COMPREHENSIVE DATA INTEGRATION")
    logger.info("=" * 70)
    
    # Step 1: Import all legal data from local folder
    logger.info("\n📁 STEP 1: Importing legal data from local folder...")
    legal_data_folder = PROJECT_ROOT / "legal data"
    
    if legal_data_folder.exists():
        importer = ComprehensiveLegalDataImporter(str(legal_data_folder))
        try:
            stats = importer.import_all_files()
            logger.info(f"✅ Imported {stats['imported_documents']} documents and {stats['imported_creditors']} creditors")
        except Exception as e:
            logger.error(f"❌ Error importing legal data: {e}")
        finally:
            importer.close()
    else:
        logger.warning(f"⚠️ Legal data folder not found: {legal_data_folder}")
    
    # Step 2: Sync with real APIs
    logger.info("\n🌐 STEP 2: Syncing with real APIs...")
    try:
        api = EnhancedBulgarianAPIs()
        api_stats = api.sync_all_creditors()
        logger.info(f"✅ Synced {api_stats['total']} records from APIs")
    except Exception as e:
        logger.error(f"❌ Error syncing APIs: {e}")
    
    # Step 3: Optimize database structure
    logger.info("\n⚡ STEP 3: Optimizing database structure...")
    try:
        optimizer = DataOptimizer()
        optimizer.optimize_all()
        logger.info("✅ Database optimization completed")
    except Exception as e:
        logger.error(f"❌ Error optimizing database: {e}")
    
    # Step 4: Display statistics
    logger.info("\n📊 STEP 4: Database Statistics...")
    try:
        db = VirtualDatabase()
        stats = db.get_statistics()
        
        logger.info("\n" + "=" * 70)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 70)
        logger.info(f"Creditors: {stats.get('creditors', {}).get('total', 0)}")
        logger.info(f"  - Banks: {stats.get('creditors', {}).get('banks', 0)}")
        logger.info(f"  - Non-bank: {stats.get('creditors', {}).get('non_bank', 0)}")
        logger.info(f"  - Blacklisted: {stats.get('creditors', {}).get('blacklisted', 0)}")
        logger.info(f"Violations: {stats.get('violations', {}).get('total', 0)}")
        logger.info(f"Legal Documents: {stats.get('legal_documents', {}).get('total', 0)}")
        logger.info(f"  - Laws: {stats.get('legal_documents', {}).get('laws', 0)}")
        logger.info(f"  - Regulations: {stats.get('legal_documents', {}).get('regulations', 0)}")
        logger.info(f"  - Registers: {stats.get('legal_documents', {}).get('registers', 0)}")
        logger.info("=" * 70)
        
        db.close()
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {e}")
    
    logger.info("\n✅ INTEGRATION COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()

