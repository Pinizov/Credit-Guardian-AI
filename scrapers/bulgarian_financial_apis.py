"""
Bulgarian Financial Registers API Integration
Integrates with official Bulgarian financial data sources:
- BNB (Bulgarian National Bank) registers
- Trade Register (registryagency.bg)
- FSC (Financial Supervision Commission)
- APIS.bg (Consumer Protection)
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


class BulgarianFinancialAPIs:
    """Integration with Bulgarian financial data APIs"""
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize API client
        
        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'bg,en;q=0.9',
        })
    
    def fetch_bnb_banks_register(self) -> List[Dict[str, Any]]:
        """
        Fetch banks from BNB register
        Source: https://www.bnb.bg
        
        Returns:
            List of bank records with standardized format
        """
        banks = []
        
        try:
            logger.info("Fetching BNB banks register...")
            
            # BNB typically publishes registers as HTML tables or downloadable files
            # This is a template - actual URL structure may vary
            url = "https://www.bnb.bg/RegistersAndServices/Registers/Banks/index.htm"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find bank table/list - try multiple selectors
            bank_rows = soup.find_all('tr', class_=lambda x: x and ('bank' in str(x).lower() or 'row' in str(x).lower()))
            
            if not bank_rows:
                # Try alternative selectors
                bank_rows = soup.find_all('tr')[1:]  # Skip header
            
            # Also try divs and lists
            if not bank_rows:
                entries = soup.find_all(['div', 'li'], class_=lambda x: x and 'bank' in str(x).lower())
                for entry in entries:
                    text = entry.get_text(strip=True)
                    if text and len(text) > 5:
                        bank_data = {
                            'name': text.split('\n')[0].strip(),
                            'type': 'bank',
                            'source': 'bnb',
                            'bulstat': self._extract_bulstat(text),
                            'fetched_at': datetime.utcnow().isoformat(),
                        }
                        if bank_data['name']:
                            banks.append(bank_data)
            
            for row in bank_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    bank_data = {
                        'name': cells[0].get_text(strip=True),
                        'license_number': cells[1].get_text(strip=True) if len(cells) > 1 else None,
                        'type': 'bank',
                        'source': 'bnb',
                        'bulstat': self._extract_bulstat(cells[0].get_text(strip=True)),
                        'address': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                        'status': cells[-1].get_text(strip=True) if len(cells) > 3 else 'active',
                        'fetched_at': datetime.utcnow().isoformat(),
                    }
                    
                    if bank_data['name'] and bank_data['name'] not in ['Име', 'Name', '']:
                        banks.append(bank_data)
            
            logger.info(f"Fetched {len(banks)} banks from BNB")
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Error fetching BNB banks: {e}")
            # Fallback: try enhanced API if available
            try:
                from scrapers.enhanced_bulgarian_apis import EnhancedBulgarianAPIs
                enhanced = EnhancedBulgarianAPIs()
                banks = enhanced.fetch_bnb_banks_real()
            except:
                pass
        
        return banks
    
    def fetch_fsc_nonbank_register(self) -> List[Dict[str, Any]]:
        """
        Fetch non-bank financial institutions from FSC register
        Source: https://www.fsc.bg
        
        Returns:
            List of non-bank financial institution records
        """
        institutions = []
        
        try:
            logger.info("Fetching FSC non-bank financial institutions register...")
            
            # FSC register URL (adjust based on actual structure)
            url = "https://www.fsc.bg/en/registers"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find institution entries
            entries = soup.find_all(['tr', 'div'], class_=lambda x: x and 'institution' in str(x).lower())
            
            if not entries:
                entries = soup.find_all('tr')[1:]
            
            for entry in entries:
                cells = entry.find_all(['td', 'span'])
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
                    
                    if inst_data['name']:
                        institutions.append(inst_data)
            
            logger.info(f"Fetched {len(institutions)} non-bank institutions from FSC")
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Error fetching FSC register: {e}")
        
        return institutions
    
    def fetch_trade_register_info(self, bulstat: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company information from Trade Register
        Source: https://registryagency.bg
        
        Args:
            bulstat: Company BULSTAT/EIK number
            
        Returns:
            Company information dictionary
        """
        try:
            # Trade Register API or web scraping
            # Note: May require authentication or have rate limits
            url = f"https://registryagency.bg/api/company/{bulstat}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name'),
                    'bulstat': bulstat,
                    'address': data.get('address'),
                    'status': data.get('status'),
                    'source': 'trade_register',
                    'fetched_at': datetime.utcnow().isoformat(),
                }
            
        except Exception as e:
            logger.warning(f"Could not fetch Trade Register info for {bulstat}: {e}")
        
        return None
    
    def parse_local_registers(self, file_paths: Dict[str, Path]) -> List[Dict[str, Any]]:
        """
        Parse local register files (XLS, DOC, XLSX)
        
        Args:
            file_paths: Dictionary mapping register type to file path
            
        Returns:
            List of standardized creditor records
        """
        all_creditors = []
        
        for register_type, path in file_paths.items():
            if not path.exists():
                logger.warning(f"File not found: {path}")
                continue
            
            logger.info(f"Parsing {register_type} from {path.name}...")
            
            try:
                if path.suffix.lower() == '.xls':
                    creditors = self._parse_xls_file(path, register_type)
                elif path.suffix.lower() == '.xlsx':
                    creditors = self._parse_xlsx_file(path, register_type)
                elif path.suffix.lower() in ['.doc', '.docx']:
                    creditors = self._parse_doc_file(path, register_type)
                else:
                    logger.warning(f"Unsupported file type: {path.suffix}")
                    continue
                
                all_creditors.extend(creditors)
                logger.info(f"Parsed {len(creditors)} creditors from {path.name}")
                
            except Exception as e:
                logger.error(f"Error parsing {path}: {e}")
        
        return all_creditors
    
    def _parse_xls_file(self, path: Path, register_type: str) -> List[Dict[str, Any]]:
        """Parse XLS file"""
        creditors = []
        
        try:
            # Use xlrd for .xls files
            import xlrd
            workbook = xlrd.open_workbook(str(path))
            
            for sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(sheet_name)
                
                # Skip header row
                for row_idx in range(1, sheet.nrows):
                    row = sheet.row_values(row_idx)
                    
                    if len(row) >= 2:
                        creditor = {
                            'name': str(row[0]).strip() if row[0] else None,
                            'type': self._determine_type(register_type),
                            'source': register_type,
                            'bulstat': self._extract_bulstat(str(row[0]) if row[0] else '') or (str(row[1]).strip() if len(row) > 1 and row[1] else None),
                            'license_number': str(row[1]).strip() if len(row) > 1 and row[1] else None,
                            'address': str(row[2]).strip() if len(row) > 2 and row[2] else None,
                            'fetched_at': datetime.utcnow().isoformat(),
                        }
                        
                        if creditor['name']:
                            creditors.append(creditor)
        
        except Exception as e:
            logger.error(f"Error parsing XLS {path}: {e}")
        
        return creditors
    
    def _parse_xlsx_file(self, path: Path, register_type: str) -> List[Dict[str, Any]]:
        """Parse XLSX file using pandas"""
        creditors = []
        
        try:
            df = pd.read_excel(path, engine='openpyxl')
            
            # Standardize column names (handle different languages/formats)
            name_col = self._find_column(df, ['name', 'име', 'наименование', 'фирма', 'company'])
            bulstat_col = self._find_column(df, ['bulstat', 'еик', 'бълстат', 'eik'])
            license_col = self._find_column(df, ['license', 'лиценз', 'номер', 'number'])
            address_col = self._find_column(df, ['address', 'адрес', 'седалище'])
            
            for _, row in df.iterrows():
                name = str(row[name_col]).strip() if name_col and pd.notna(row.get(name_col)) else None
                
                if name and name.lower() not in ['nan', 'none', '']:
                    creditor = {
                        'name': name,
                        'type': self._determine_type(register_type),
                        'source': register_type,
                        'bulstat': str(row[bulstat_col]).strip() if bulstat_col and pd.notna(row.get(bulstat_col)) else self._extract_bulstat(name),
                        'license_number': str(row[license_col]).strip() if license_col and pd.notna(row.get(license_col)) else None,
                        'address': str(row[address_col]).strip() if address_col and pd.notna(row.get(address_col)) else None,
                        'fetched_at': datetime.utcnow().isoformat(),
                    }
                    
                    creditors.append(creditor)
        
        except Exception as e:
            logger.error(f"Error parsing XLSX {path}: {e}")
        
        return creditors
    
    def _parse_doc_file(self, path: Path, register_type: str) -> List[Dict[str, Any]]:
        """Parse DOC/DOCX file"""
        creditors = []
        
        try:
            if path.suffix.lower() == '.docx':
                from docx import Document
                doc = Document(str(path))
                
                for para in doc.paragraphs:
                    text = para.text.strip()
                    if text and len(text) > 5:
                        # Try to extract creditor info from paragraph
                        creditor = {
                            'name': text.split('\n')[0].strip(),
                            'type': self._determine_type(register_type),
                            'source': register_type,
                            'bulstat': self._extract_bulstat(text),
                            'fetched_at': datetime.utcnow().isoformat(),
                        }
                        
                        if creditor['name']:
                            creditors.append(creditor)
            else:
                # For .doc files, use text extraction
                logger.warning(f"Binary .doc files require special handling: {path}")
        
        except Exception as e:
            logger.error(f"Error parsing DOC {path}: {e}")
        
        return creditors
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names (case-insensitive)"""
        df_lower = df.columns.str.lower()
        for name in possible_names:
            matches = [col for col in df.columns if name.lower() in col.lower()]
            if matches:
                return matches[0]
        return None
    
    def _extract_bulstat(self, text: str) -> Optional[str]:
        """Extract BULSTAT/EIK number from text"""
        # BULSTAT is typically 9-13 digits
        match = re.search(r'\b(\d{9,13})\b', text)
        return match.group(1) if match else None
    
    def _determine_type(self, register_type: str) -> str:
        """Determine creditor type from register type"""
        register_lower = register_type.lower()
        
        if 'bank' in register_lower:
            return 'bank'
        elif 'non' in register_lower or 'fi' in register_lower:
            return 'non-bank'
        elif 'credit' in register_lower:
            return 'non-bank'
        else:
            return 'unknown'
    
    def standardize_creditor_data(self, creditors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize and deduplicate creditor data
        
        Args:
            creditors: List of creditor dictionaries
            
        Returns:
            Standardized and deduplicated list
        """
        # Group by BULSTAT or name
        by_bulstat = {}
        by_name = {}
        
        for creditor in creditors:
            # Normalize name
            name = creditor.get('name', '').strip()
            if not name:
                continue
            
            bulstat = creditor.get('bulstat')
            
            # Use BULSTAT as primary key if available
            if bulstat:
                if bulstat not in by_bulstat:
                    by_bulstat[bulstat] = creditor
                else:
                    # Merge data
                    existing = by_bulstat[bulstat]
                    for key, value in creditor.items():
                        if value and not existing.get(key):
                            existing[key] = value
            else:
                # Use normalized name as key
                name_key = name.lower().strip()
                if name_key not in by_name:
                    by_name[name_key] = creditor
                else:
                    existing = by_name[name_key]
                    for key, value in creditor.items():
                        if value and not existing.get(key):
                            existing[key] = value
        
        # Combine results
        standardized = list(by_bulstat.values()) + [
            c for c in by_name.values() if not c.get('bulstat') or c.get('bulstat') not in by_bulstat
        ]
        
        # Ensure all required fields
        for creditor in standardized:
            creditor.setdefault('type', 'unknown')
            creditor.setdefault('violations_count', 0)
            creditor.setdefault('risk_score', 0.0)
            creditor.setdefault('is_blacklisted', False)
        
        return standardized


def main():
    """Main function for testing"""
    api = BulgarianFinancialAPIs()
    
    # Parse local files
    legal_data_dir = Path("legal data")
    file_paths = {
        'bnb_banks': legal_data_dir / "bs_ci_reg_bankslist_bg.doc",
        'fsc_nonbank': legal_data_dir / "bs_fi_regintro_register_bg.xls",
    }
    
    creditors = api.parse_local_registers(file_paths)
    
    # Standardize
    standardized = api.standardize_creditor_data(creditors)
    
    print(f"\n✅ Parsed {len(creditors)} raw records")
    print(f"✅ Standardized to {len(standardized)} unique creditors")
    
    # Save to JSON
    output_file = "data/bulgarian_creditors.json"
    Path("data").mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(standardized, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to {output_file}")
    
    return standardized


if __name__ == "__main__":
    main()

