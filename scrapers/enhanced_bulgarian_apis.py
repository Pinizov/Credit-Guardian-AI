"""
Enhanced Bulgarian Financial APIs Integration
Интеграция с реални API и бази данни за български кредитори
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import time
import json
from datetime import datetime
import re
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EnhancedBulgarianAPIs:
    """Enhanced integration with Bulgarian financial data APIs and databases"""
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize API client with real endpoints
        
        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8',
            'Accept-Language': 'bg-BG,bg;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        
        # Real API endpoints
        self.endpoints = {
            'bnb_banks': 'https://www.bnb.bg/RegistersAndServices/Registers/Banks/index.htm',
            'bnb_credit_institutions': 'https://www.bnb.bg/RegistersAndServices/Registers/CreditInstitutions/index.htm',
            'fsc_nonbank': 'https://www.fsc.bg/bg/registri',
            'trade_register': 'https://portal.registryagency.bg',
            'apis_violations': 'https://www.apis.bg',
            'registry_agency': 'https://portal.registryagency.bg/CR/api/Deeds',
        }
    
    def fetch_bnb_banks_real(self) -> List[Dict[str, Any]]:
        """
        Fetch banks from BNB register (real endpoint)
        Source: https://www.bnb.bg/RegistersAndServices/Registers/Banks/
        
        Returns:
            List of bank records
        """
        banks = []
        
        try:
            logger.info("Fetching BNB banks register from real API...")
            
            url = self.endpoints['bnb_banks']
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for BNB page structure
            tables = soup.find_all('table')
            if not tables:
                # Try finding list items or divs
                entries = soup.find_all(['li', 'div'], class_=lambda x: x and ('bank' in str(x).lower() or 'institution' in str(x).lower()))
                
                for entry in entries:
                    text = entry.get_text(strip=True)
                    if text and len(text) > 5:
                        bank_data = self._parse_bank_entry(text)
                        if bank_data:
                            banks.append(bank_data)
            else:
                # Parse table
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            bank_data = {
                                'name': cells[0].get_text(strip=True),
                                'license_number': cells[1].get_text(strip=True) if len(cells) > 1 else None,
                                'type': 'bank',
                                'source': 'bnb',
                                'bulstat': self._extract_bulstat(cells[0].get_text(strip=True)),
                                'address': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                                'status': 'active',
                                'fetched_at': datetime.utcnow().isoformat(),
                            }
                            
                            if bank_data['name'] and bank_data['name'] not in ['Име', 'Name', '']:
                                banks.append(bank_data)
            
            logger.info(f"✅ Fetched {len(banks)} banks from BNB")
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"❌ Error fetching BNB banks: {e}")
            # Fallback: return empty list, will use local files
        
        return banks
    
    def fetch_fsc_nonbank_real(self) -> List[Dict[str, Any]]:
        """
        Fetch non-bank financial institutions from FSC (real endpoint)
        Source: https://www.fsc.bg/bg/registri
        
        Returns:
            List of non-bank financial institution records
        """
        institutions = []
        
        try:
            logger.info("Fetching FSC non-bank register from real API...")
            
            url = self.endpoints['fsc_nonbank']
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # FSC typically uses tables or lists
            tables = soup.find_all('table')
            entries = soup.find_all(['tr', 'div', 'li'], class_=lambda x: x and ('institution' in str(x).lower() or 'register' in str(x).lower()))
            
            if tables:
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            inst_data = {
                                'name': cells[0].get_text(strip=True),
                                'type': 'non-bank',
                                'source': 'fsc',
                                'license_number': cells[1].get_text(strip=True) if len(cells) > 1 else None,
                                'bulstat': self._extract_bulstat(cells[0].get_text(strip=True)),
                                'address': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                                'fetched_at': datetime.utcnow().isoformat(),
                            }
                            
                            if inst_data['name'] and inst_data['name'] not in ['Име', 'Name', '']:
                                institutions.append(inst_data)
            
            logger.info(f"✅ Fetched {len(institutions)} non-bank institutions from FSC")
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"❌ Error fetching FSC register: {e}")
        
        return institutions
    
    def fetch_trade_register_company(self, bulstat: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company information from Trade Register API
        Source: https://portal.registryagency.bg
        
        Args:
            bulstat: Company BULSTAT/EIK number
            
        Returns:
            Company information dictionary
        """
        try:
            # Trade Register API endpoint (may require authentication)
            # Note: This is a template - actual API structure may vary
            url = f"{self.endpoints['trade_register']}/api/Company/{bulstat}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', ''),
                    'bulstat': bulstat,
                    'address': data.get('address', ''),
                    'status': data.get('status', 'active'),
                    'source': 'trade_register',
                    'fetched_at': datetime.utcnow().isoformat(),
                }
            else:
                logger.warning(f"Trade Register API returned status {response.status_code} for {bulstat}")
                
        except Exception as e:
            logger.debug(f"Could not fetch Trade Register info for {bulstat}: {e}")
        
        return None
    
    def fetch_apis_violations(self, company_name: Optional[str] = None, 
                             bulstat: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch violations from APIS.bg (Consumer Protection Authority)
        Source: https://www.apis.bg
        
        Args:
            company_name: Optional company name to search
            bulstat: Optional BULSTAT to search
            
        Returns:
            List of violation records
        """
        violations = []
        
        try:
            logger.info("Fetching violations from APIS.bg...")
            
            # APIS.bg violations page
            url = f"{self.endpoints['apis_violations']}/violations"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find violation entries
            entries = soup.find_all(['tr', 'div'], class_=lambda x: x and ('violation' in str(x).lower() or 'case' in str(x).lower()))
            
            for entry in entries:
                text = entry.get_text(strip=True)
                if text and len(text) > 10:
                    violation_data = {
                        'company_name': company_name or self._extract_company_name(text),
                        'bulstat': bulstat or self._extract_bulstat(text),
                        'violation_description': text[:500],
                        'authority': 'APIS',
                        'source_url': url,
                        'fetched_at': datetime.utcnow().isoformat(),
                    }
                    violations.append(violation_data)
            
            logger.info(f"✅ Fetched {len(violations)} violations from APIS.bg")
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"❌ Error fetching APIS violations: {e}")
        
        return violations
    
    def sync_all_creditors(self) -> Dict[str, Any]:
        """
        Sync all creditors from all available sources
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'bnb_banks': 0,
            'fsc_nonbank': 0,
            'trade_register': 0,
            'apis_violations': 0,
            'total': 0
        }
        
        logger.info("=" * 70)
        logger.info("SYNCING CREDITORS FROM ALL SOURCES")
        logger.info("=" * 70)
        
        # 1. BNB Banks
        try:
            banks = self.fetch_bnb_banks_real()
            stats['bnb_banks'] = len(banks)
            logger.info(f"✓ BNB Banks: {len(banks)}")
        except Exception as e:
            logger.warning(f"⚠️ BNB sync failed: {e}")
        
        # 2. FSC Non-bank
        try:
            nonbank = self.fetch_fsc_nonbank_real()
            stats['fsc_nonbank'] = len(nonbank)
            logger.info(f"✓ FSC Non-bank: {len(nonbank)}")
        except Exception as e:
            logger.warning(f"⚠️ FSC sync failed: {e}")
        
        # 3. APIS Violations
        try:
            violations = self.fetch_apis_violations()
            stats['apis_violations'] = len(violations)
            logger.info(f"✓ APIS Violations: {len(violations)}")
        except Exception as e:
            logger.warning(f"⚠️ APIS sync failed: {e}")
        
        stats['total'] = stats['bnb_banks'] + stats['fsc_nonbank'] + stats['apis_violations']
        
        logger.info("=" * 70)
        logger.info(f"TOTAL SYNCED: {stats['total']} records")
        logger.info("=" * 70)
        
        return stats
    
    def _parse_bank_entry(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse bank entry from text"""
        if not text or len(text) < 5:
            return None
        
        return {
            'name': text.split('\n')[0].strip(),
            'type': 'bank',
            'source': 'bnb',
            'bulstat': self._extract_bulstat(text),
            'fetched_at': datetime.utcnow().isoformat(),
        }
    
    def _extract_bulstat(self, text: str) -> Optional[str]:
        """Extract BULSTAT/EIK number from text"""
        # BULSTAT is typically 9-13 digits
        match = re.search(r'\b(\d{9,13})\b', text)
        return match.group(1) if match else None
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        # Simple extraction - first line or first capitalized words
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and line[0].isupper():
                return line
        return None


def main():
    """Test the enhanced API integration"""
    api = EnhancedBulgarianAPIs()
    
    # Sync all sources
    stats = api.sync_all_creditors()
    
    print("\n" + "=" * 70)
    print("SYNC RESULTS")
    print("=" * 70)
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("=" * 70)


if __name__ == "__main__":
    main()

