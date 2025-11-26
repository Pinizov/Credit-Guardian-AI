#!/usr/bin/env python
"""
Test Commands and Scripts
Тества всички команди и скриптове дали работят
"""

import sys
import subprocess
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_command(command, description):
    """Test a command"""
    logger.info(f"Testing: {description}")
    logger.info(f"  Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode == 0:
            logger.info(f"  ✅ PASS: {description}")
            return True
        else:
            logger.error(f"  ❌ FAIL: {description}")
            logger.error(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"  ❌ FAIL: {description} (timeout)")
        return False
    except Exception as e:
        logger.error(f"  ❌ FAIL: {description}: {e}")
        return False

def main():
    """Test all commands"""
    logger.info("=" * 70)
    logger.info("TESTING COMMANDS AND SCRIPTS")
    logger.info("=" * 70)
    
    results = []
    
    # Test Python imports
    logger.info("\n" + "=" * 70)
    logger.info("Testing Python Scripts (Import Check)")
    logger.info("=" * 70)
    
    scripts = [
        ("python -c \"import sys; sys.path.insert(0, '.'); from database.models import Base, engine; print('OK')\"", 
         "Database models import"),
        ("python -c \"import sys; sys.path.insert(0, '.'); from database.virtual_db import VirtualDatabase; print('OK')\"", 
         "Virtual database import"),
        ("python -c \"import sys; sys.path.insert(0, '.'); from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs; print('OK')\"", 
         "Enhanced APIs import"),
        ("python -c \"import sys; sys.path.insert(0, '.'); from import_all_legal_data_comprehensive import ComprehensiveLegalDataImporter; print('OK')\"", 
         "Comprehensive importer import"),
    ]
    
    for cmd, desc in scripts:
        results.append((desc, test_command(cmd, desc)))
    
    # Test script files exist and are valid Python
    logger.info("\n" + "=" * 70)
    logger.info("Testing Script Files (Syntax Check)")
    logger.info("=" * 70)
    
    script_files = [
        "import_all_legal_data_comprehensive.py",
        "import_creditors_from_apis.py",
        "import_local_legal_data.py",
        "integrate_all_sources.py",
        "database/data_optimizer.py",
    ]
    
    for script_file in script_files:
        script_path = PROJECT_ROOT / script_file
        if script_path.exists():
            cmd = f"python -m py_compile {script_file}"
            results.append((f"Syntax check: {script_file}", test_command(cmd, f"Syntax: {script_file}")))
        else:
            logger.warning(f"  ⚠️ Script not found: {script_file}")
            results.append((f"Syntax check: {script_file}", False))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("COMMAND TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"Total: {total}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {total - passed}")
    logger.info("=" * 70)
    
    if passed == total:
        logger.info("✅ ALL COMMAND TESTS PASSED!")
        return 0
    else:
        logger.error(f"❌ {total - passed} COMMAND TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

