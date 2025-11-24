"""
Scraper for apis.bg - Bulgarian consumer protection authority database
Extracts violation records, complaints, and enforcement actions
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import json
from datetime import datetime
import re


class ApisBgScraper:
    """Scraper for apis.bg consumer protection authority"""
    
    BASE_URL = "https://www.apis.bg"
    
    # Key sections to scrape
    SECTIONS = {
        'violations': '/bg/narushenia',  # Violations and penalties
        'complaints': '/bg/jalbi',  # Consumer complaints
        'blacklist': '/bg/cheren-spisak',  # Blacklisted companies
        'decisions': '/bg/reshenia',  # Administrative decisions
    }
    
    def __init__(self, delay: float = 2.0):
        """
        Initialize scraper
        
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
    
    def scrape_violations(self, max_pages: int = 5) -> List[Dict]:
        """
        Scrape violation records from apis.bg
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of violation records
        """
        violations = []
        
        print(f"\n🔍 Scraping violations from apis.bg...")
        
        try:
            for page in range(1, max_pages + 1):
                print(f"  Page {page}/{max_pages}...")
                
                url = f"{self.BASE_URL}{self.SECTIONS['violations']}?page={page}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find violation records
                violation_items = soup.find_all('div', class_=['violation-item', 'decision-item', 'record'])
                
                if not violation_items:
                    # Try alternative selectors
                    violation_items = soup.find_all('tr', class_='data-row')
                
                if not violation_items:
                    print(f"  ⚠️ No violations found on page {page}")
                    break
                
                for item in violation_items:
                    violation = self._parse_violation_item(item)
                    if violation:
                        violations.append(violation)
                
                print(f"  ✅ Found {len(violation_items)} records")
                time.sleep(self.delay)
        
        except Exception as e:
            print(f"❌ Error scraping violations: {e}")
        
        print(f"✅ Total violations scraped: {len(violations)}")
        return violations
    
    def _parse_violation_item(self, item) -> Optional[Dict]:
        """
        Parse a single violation record
        
        Args:
            item: BeautifulSoup element containing violation data
            
        Returns:
            Dictionary with violation details
        """
        try:
            violation = {
                'scraped_at': datetime.utcnow().isoformat(),
                'source': 'apis.bg',
            }
            
            # Extract company name
            company_elem = item.find(['a', 'span', 'td'], class_=lambda x: x and 'company' in str(x).lower())
            if company_elem:
                violation['company'] = company_elem.get_text(strip=True)
            
            # Extract decision number
            decision_elem = item.find(['span', 'td'], class_=lambda x: x and 'decision' in str(x).lower())
            if decision_elem:
                violation['decision_number'] = decision_elem.get_text(strip=True)
            
            # Extract penalty amount
            penalty_elem = item.find(['span', 'td'], class_=lambda x: x and 'penalty' in str(x).lower())
            if penalty_elem:
                penalty_text = penalty_elem.get_text(strip=True)
                # Extract numeric value
                amount_match = re.search(r'(\d+[\d\s,\.]*)', penalty_text)
                if amount_match:
                    violation['penalty_amount'] = float(amount_match.group(1).replace(' ', '').replace(',', ''))
            
            # Extract date
            date_elem = item.find(['span', 'td', 'time'], class_=lambda x: x and 'date' in str(x).lower())
            if date_elem:
                violation['decision_date'] = date_elem.get_text(strip=True)
            
            # Extract violation type/description
            desc_elem = item.find(['p', 'td', 'div'], class_=lambda x: x and 'description' in str(x).lower())
            if desc_elem:
                violation['description'] = desc_elem.get_text(strip=True)
            
            # Extract link to full decision
            link_elem = item.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    violation['url'] = self.BASE_URL + href
                else:
                    violation['url'] = href
            
            return violation if len(violation) > 2 else None
            
        except Exception as e:
            print(f"  ⚠️ Error parsing violation item: {e}")
            return None
    
    def scrape_blacklist(self) -> List[Dict]:
        """
        Scrape blacklisted companies
        
        Returns:
            List of blacklisted entities
        """
        blacklist = []
        
        print(f"\n🚫 Scraping blacklist from apis.bg...")
        
        try:
            url = f"{self.BASE_URL}{self.SECTIONS['blacklist']}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blacklist entries
            entries = soup.find_all(['tr', 'div'], class_=lambda x: x and 'blacklist' in str(x).lower())
            
            if not entries:
                entries = soup.find_all('tr')[1:]  # Skip header row
            
            for entry in entries:
                company_data = {
                    'scraped_at': datetime.utcnow().isoformat(),
                    'is_blacklisted': True,
                    'source': 'apis.bg',
                }
                
                # Extract company name
                cells = entry.find_all(['td', 'span'])
                if cells and len(cells) >= 2:
                    company_data['name'] = cells[0].get_text(strip=True)
                    company_data['reason'] = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                    company_data['bulstat'] = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                    
                    blacklist.append(company_data)
            
            print(f"✅ Blacklisted entities: {len(blacklist)}")
            
        except Exception as e:
            print(f"❌ Error scraping blacklist: {e}")
        
        return blacklist
    
    def scrape_all(self, max_violation_pages: int = 5) -> Dict:
        """
        Scrape all sections
        
        Args:
            max_violation_pages: Maximum pages to scrape from violations
            
        Returns:
            Dictionary with all scraped data
        """
        data = {
            'violations': [],
            'blacklist': [],
            'scraped_at': datetime.utcnow().isoformat(),
        }
        
        print(f"\n🚀 Starting comprehensive scrape of apis.bg...")
        
        # Scrape violations
        data['violations'] = self.scrape_violations(max_pages=max_violation_pages)
        
        # Scrape blacklist
        data['blacklist'] = self.scrape_blacklist()
        
        print(f"\n✅ Scraping complete:")
        print(f"  - Violations: {len(data['violations'])}")
        print(f"  - Blacklisted entities: {len(data['blacklist'])}")
        
        return data
    
    def save_to_json(self, data: Dict, output_file: str = "apis_bg_data.json"):
        """
        Save scraped data to JSON file
        
        Args:
            data: Dictionary with scraped data
            output_file: Output filename
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")


def main():
    """Main execution function"""
    scraper = ApisBgScraper(delay=2.0)
    
    # Scrape all data
    data = scraper.scrape_all(max_violation_pages=3)
    
    # Save results
    if data:
        scraper.save_to_json(data, "data/apis_bg_data.json")
    
    return data


if __name__ == "__main__":
    main()
