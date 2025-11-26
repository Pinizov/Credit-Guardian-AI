#!/usr/bin/env python
"""
Import creditors from Bulgarian financial registers and APIs
Optimized data format for fast and easy handling
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.models import Creditor, Session, Base, engine
from scrapers.bulgarian_financial_apis import BulgarianFinancialAPIs
from scrapers.apis_bg_scraper import ApisBgScraper
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_creditors_to_database(creditors: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
    """
    Import creditors to database with optimized batch processing
    
    Args:
        creditors: List of standardized creditor dictionaries
        batch_size: Number of records to process per batch
        
    Returns:
        Statistics dictionary
    """
    stats = {
        'total': len(creditors),
        'imported': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    session = Session()
    
    try:
        # Process in batches for performance
        for i in range(0, len(creditors), batch_size):
            batch = creditors[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(creditors)-1)//batch_size + 1} ({len(batch)} records)")
            
            for creditor_data in batch:
                try:
                    # Check if creditor exists by BULSTAT or name
                    existing = None
                    
                    if creditor_data.get('bulstat'):
                        existing = session.query(Creditor).filter(
                            Creditor.bulstat == creditor_data['bulstat']
                        ).first()
                    
                    if not existing and creditor_data.get('name'):
                        existing = session.query(Creditor).filter(
                            Creditor.name.ilike(creditor_data['name'].strip())
                        ).first()
                    
                    if existing:
                        # Update existing record
                        for key, value in creditor_data.items():
                            if key not in ['id', 'created_at'] and value is not None:
                                if hasattr(existing, key):
                                    setattr(existing, key, value)
                        stats['updated'] += 1
                    else:
                        # Create new record
                        new_creditor = Creditor(
                            name=creditor_data['name'],
                            type=creditor_data.get('type', 'unknown'),
                            bulstat=creditor_data.get('bulstat'),
                            license_number=creditor_data.get('license_number'),
                            address=creditor_data.get('address'),
                            violations_count=creditor_data.get('violations_count', 0),
                            risk_score=creditor_data.get('risk_score', 0.0),
                            is_blacklisted=creditor_data.get('is_blacklisted', False),
                        )
                        session.add(new_creditor)
                        stats['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing creditor {creditor_data.get('name')}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Commit batch
            try:
                session.commit()
                logger.info(f"✅ Committed batch {i//batch_size + 1}")
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error committing batch: {e}")
                stats['errors'] += len(batch)
        
    finally:
        session.close()
    
    return stats


def enrich_with_violations(creditors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich creditors with violation data from APIS.bg
    
    Args:
        creditors: List of creditor dictionaries
        
    Returns:
        Enriched creditor list
    """
    logger.info("Enriching creditors with violation data...")
    
    try:
        scraper = ApisBgScraper()
        violations_data = scraper.scrape_violations(max_pages=3)
        blacklist_data = scraper.scrape_blacklist()
        
        # Create lookup by company name
        violations_by_company = {}
        for violation in violations_data:
            company = violation.get('company', '').strip()
            if company:
                if company not in violations_by_company:
                    violations_by_company[company] = []
                violations_by_company[company].append(violation)
        
        blacklisted_companies = {item.get('name', '').strip().lower() for item in blacklist_data}
        
        # Enrich creditors
        for creditor in creditors:
            name = creditor.get('name', '').strip().lower()
            
            # Check for violations
            if name in violations_by_company:
                creditor['violations_count'] = len(violations_by_company[name])
                creditor['has_violations'] = True
            
            # Check blacklist
            if name in blacklisted_companies:
                creditor['is_blacklisted'] = True
                creditor['risk_score'] = max(creditor.get('risk_score', 0.0), 8.0)
        
        logger.info(f"✅ Enriched {len([c for c in creditors if c.get('has_violations')])} creditors with violations")
        
    except Exception as e:
        logger.error(f"Error enriching with violations: {e}")
    
    return creditors


def main():
    """Main import function"""
    logger.info("=" * 70)
    logger.info("CREDITOR IMPORT FROM BULGARIAN FINANCIAL REGISTERS")
    logger.info("=" * 70)
    
    # Initialize API client
    api = BulgarianFinancialAPIs()
    
    all_creditors = []
    
    # 1. Parse local register files
    logger.info("\n📁 Step 1: Parsing local register files...")
    legal_data_dir = Path("legal data")
    
    file_paths = {}
    
    # Banks list
    banks_file = legal_data_dir / "bs_ci_reg_bankslist_bg.doc"
    if banks_file.exists():
        file_paths['bnb_banks'] = banks_file
    
    # Non-bank financial institutions
    fsc_file = legal_data_dir / "bs_fi_regintro_register_bg.xls"
    if fsc_file.exists():
        file_paths['fsc_nonbank'] = fsc_file
    
    # Additional register files
    for pattern in ["bs_ci_register_bg.xls", "rs_lcbregisters_*.xlsx", "rs_csrcreditservregister_bg.xlsx"]:
        for file_path in legal_data_dir.glob(pattern):
            file_paths[f"register_{file_path.stem}"] = file_path
    
    if file_paths:
        local_creditors = api.parse_local_registers(file_paths)
        all_creditors.extend(local_creditors)
        logger.info(f"✅ Parsed {len(local_creditors)} creditors from local files")
    else:
        logger.warning("⚠️ No local register files found")
    
    # 2. Try to fetch from online APIs (optional, may fail)
    logger.info("\n🌐 Step 2: Fetching from online APIs...")
    try:
        online_banks = api.fetch_bnb_banks_register()
        if online_banks:
            all_creditors.extend(online_banks)
            logger.info(f"✅ Fetched {len(online_banks)} banks from BNB")
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch from BNB API: {e}")
    
    try:
        online_nonbank = api.fetch_fsc_nonbank_register()
        if online_nonbank:
            all_creditors.extend(online_nonbank)
            logger.info(f"✅ Fetched {len(online_nonbank)} institutions from FSC")
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch from FSC API: {e}")
    
    # 3. Standardize and deduplicate
    logger.info("\n🔄 Step 3: Standardizing and deduplicating data...")
    standardized = api.standardize_creditor_data(all_creditors)
    logger.info(f"✅ Standardized to {len(standardized)} unique creditors")
    
    # 4. Enrich with violation data
    logger.info("\n🔍 Step 4: Enriching with violation data...")
    enriched = enrich_with_violations(standardized)
    
    # 5. Import to database
    logger.info("\n💾 Step 5: Importing to database...")
    stats = import_creditors_to_database(enriched)
    
    # 6. Print summary
    logger.info("\n" + "=" * 70)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total records processed: {stats['total']}")
    logger.info(f"✅ New creditors imported: {stats['imported']}")
    logger.info(f"🔄 Existing creditors updated: {stats['updated']}")
    logger.info(f"⏭️ Skipped: {stats['skipped']}")
    logger.info(f"❌ Errors: {stats['errors']}")
    logger.info("=" * 70)
    
    # 7. Save to JSON backup
    output_file = Path("data/bulgarian_creditors_imported.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n💾 Backup saved to {output_file}")
    
    return stats


if __name__ == "__main__":
    main()

