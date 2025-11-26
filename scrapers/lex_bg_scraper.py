"""
Scraper for lex.bg - Bulgarian legal database
Extracts laws, regulations, and legal documents for AI agent training
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import json
from datetime import datetime


class LexBgScraper:
    """Scraper for lex.bg legal database"""
    
    BASE_URL = "https://www.lex.bg"
    
    # Key consumer protection laws in Bulgaria
    PRIORITY_LAWS = [
        "Закон за потребителския кредит",  # Consumer Credit Act
        "Закон за защита на потребителите",  # Consumer Protection Act
        "Закон за кредитните институции",  # Credit Institutions Act
        "Наредба № 8 за лихвите по влогове и кредити",  # Interest Rates Regulation
        "Закон за задълженията и договорите",  # Obligations and Contracts Act
    ]
    
    def __init__(self, delay: float = 2.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds (respect rate limits)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'bg,en;q=0.9',
        })
    
    def search_law(self, law_name: str) -> Optional[Dict]:
        """
        Search for a specific law by name
        
        Args:
            law_name: Name of the law to search for
            
        Returns:
            Dictionary with law metadata and URL, or None if not found
        """
        try:
            # Search endpoint on lex.bg
            search_url = f"{self.BASE_URL}/bg/laws/ldoc"
            params = {'search': law_name}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first result (most relevant)
            result = soup.find('div', class_='search-result')
            if not result:
                print(f"⚠️ Law not found: {law_name}")
                return None
            
            # Extract metadata
            title_tag = result.find('a', class_='law-title')
            if not title_tag:
                return None
            
            law_data = {
                'title': title_tag.get_text(strip=True),
                'url': self.BASE_URL + title_tag.get('href', ''),
                'search_query': law_name,
                'scraped_at': datetime.utcnow().isoformat(),
            }
            
            print(f"✅ Found: {law_data['title']}")
            time.sleep(self.delay)
            
            return law_data
            
        except Exception as e:
            print(f"❌ Error searching law '{law_name}': {e}")
            return None
    
    def get_law_content(self, law_url: str) -> Optional[Dict]:
        """
        Fetch full content of a law document
        
        Args:
            law_url: URL of the law document
            
        Returns:
            Dictionary with law content and structure
        """
        try:
            response = self.session.get(law_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract document structure
            content = {
                'url': law_url,
                'full_text': '',
                'articles': [],
                'chapters': [],
                'paragraphs': [],
            }
            
            # Find main content container
            main_content = soup.find('div', class_='law-content')
            if not main_content:
                main_content = soup.find('div', {'id': 'content'})
            
            if main_content:
                content['full_text'] = main_content.get_text(separator='\n', strip=True)
                
                # Extract articles
                articles = main_content.find_all(['div', 'p'], class_=lambda x: x and 'article' in x.lower())
                for article in articles:
                    article_text = article.get_text(strip=True)
                    if article_text:
                        content['articles'].append(article_text)
                
                # Extract chapters
                chapters = main_content.find_all(['h2', 'h3', 'div'], class_=lambda x: x and 'chapter' in x.lower())
                for chapter in chapters:
                    chapter_text = chapter.get_text(strip=True)
                    if chapter_text:
                        content['chapters'].append(chapter_text)
            
            print(f"✅ Fetched content: {len(content['full_text'])} chars, {len(content['articles'])} articles")
            time.sleep(self.delay)
            
            return content
            
        except Exception as e:
            print(f"❌ Error fetching law content from {law_url}: {e}")
            return None
    
    def scrape_priority_laws(self) -> List[Dict]:
        """
        Scrape all priority consumer protection laws
        
        Returns:
            List of dictionaries with law data
        """
        results = []
        
        print(f"\n🚀 Starting scrape of {len(self.PRIORITY_LAWS)} priority laws from lex.bg...")
        
        for i, law_name in enumerate(self.PRIORITY_LAWS, 1):
            print(f"\n[{i}/{len(self.PRIORITY_LAWS)}] Searching: {law_name}")
            
            # Search for law
            law_metadata = self.search_law(law_name)
            if not law_metadata:
                continue
            
            # Get full content
            law_content = self.get_law_content(law_metadata['url'])
            if law_content:
                law_metadata.update(law_content)
                results.append(law_metadata)
        
        print(f"\n✅ Scraping complete. Collected {len(results)} laws.")
        return results
    
    def save_to_json(self, data: List[Dict], output_file: str = "lex_bg_laws.json"):
        """
        Save scraped data to JSON file
        
        Args:
            data: List of law dictionaries
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
    scraper = LexBgScraper(delay=2.0)
    
    # Scrape priority laws
    laws_data = scraper.scrape_priority_laws()
    
    # Save results
    if laws_data:
        scraper.save_to_json(laws_data, "data/lex_bg_laws.json")
    
    return laws_data


if __name__ == "__main__":
    main()
