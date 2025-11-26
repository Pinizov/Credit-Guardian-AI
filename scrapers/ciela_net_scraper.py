"""
Scraper for ciela.net - Bulgarian legal database (Svobodna Zona)
Extracts laws, regulations, and normative acts for AI agent training
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import json
from datetime import datetime
import re


class CielaNetScraper:
    """Scraper for ciela.net legal database - Svobodna Zona (Free Zone)"""
    
    BASE_URL = "https://www.ciela.net"
    MAIN_PAGE_URL = "https://www.ciela.net/svobodna-zona-normativi"
    
    # Direct law URLs (since category browsing requires different approach)
    PRIORITY_LAWS = [
        {
            'title': 'Закон за потребителския кредит',
            'url': 'https://www.ciela.net/svobodna-zona-normativi/view/2135540562/zakon-za-potrebitelskiya-kredit',
        },
        {
            'title': 'Закон за защита на потребителите',
            'url': 'https://www.ciela.net/svobodna-zona-normativi/view/2135540563/zakon-za-zashtita-na-potrebitelite',
        },
        {
            'title': 'Закон за кредитните институции',
            'url': 'https://www.ciela.net/svobodna-zona-normativi/view/2135540564/zakon-za-kreditnite-institucii',
        },
        {
            'title': 'Закон за задълженията и договорите',
            'url': 'https://www.ciela.net/svobodna-zona-normativi/view/2135418484/zakon-za-zadylzheniyata-i-dogovorite',
        },
        {
            'title': 'Граждански процесуален кодекс',
            'url': 'https://www.ciela.net/svobodna-zona-normativi/view/2135540569/grazhdanski-protsesualen-kodeks',
        },
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'bg,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def get_category_laws(self, category_slug: str) -> List[Dict]:
        """
        Get all laws from a specific category
        
        Args:
            category_slug: URL slug for the category
            
        Returns:
            List of law metadata dictionaries
        """
        laws = []
        
        try:
            url = f"{self.CATEGORY_URL}{category_slug}"
            print(f"📂 Fetching category: {category_slug}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find law listings
            law_items = soup.find_all('div', class_=['document-item', 'law-item', 'norm-item'])
            
            if not law_items:
                # Try alternative selectors
                law_items = soup.find_all('a', href=re.compile(r'/svobodna-zona-normativi/view/'))
                
            if not law_items:
                # Try finding all links in main content
                main_content = soup.find('div', class_=['main-content', 'content', 'category-content'])
                if main_content:
                    law_items = main_content.find_all('a', href=True)
            
            print(f"  Found {len(law_items)} items")
            
            for item in law_items:
                try:
                    # Extract title and URL
                    if item.name == 'a':
                        title_elem = item
                    else:
                        title_elem = item.find('a')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    
                    if not href or not title:
                        continue
                    
                    # Build full URL
                    if href.startswith('/'):
                        full_url = self.BASE_URL + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Only process normative documents
                    if 'svobodna-zona-normativi' not in full_url:
                        continue
                    
                    law_data = {
                        'title': title,
                        'url': full_url,
                        'category': category_slug,
                        'scraped_at': datetime.utcnow().isoformat(),
                    }
                    
                    laws.append(law_data)
                    print(f"  ✅ {title[:60]}...")
                    
                except Exception as e:
                    print(f"  ⚠️ Error parsing item: {e}")
                    continue
            
            time.sleep(self.delay)
            
        except Exception as e:
            print(f"❌ Error fetching category {category_slug}: {e}")
        
        return laws
    
    def get_law_content(self, law_url: str) -> Optional[Dict]:
        """
        Fetch full content of a law document
        
        Args:
            law_url: URL of the law document
            
        Returns:
            Dictionary with law content and structure
        """
        try:
            print(f"📄 Fetching: {law_url}")
            
            response = self.session.get(law_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = {
                'url': law_url,
                'full_text': '',
                'articles': [],
                'chapters': [],
                'metadata': {},
            }
            
            # Extract metadata
            meta_section = soup.find('div', class_=['document-meta', 'law-meta', 'metadata'])
            if meta_section:
                # Extract document number, date, etc.
                doc_number = meta_section.find(text=re.compile(r'ДВ|№'))
                if doc_number:
                    content['metadata']['document_number'] = doc_number.strip()
            
            # Find main content
            main_content = soup.find('div', class_=['document-content', 'law-content', 'norm-content', 'main-text'])
            
            if not main_content:
                # Try alternative selectors
                main_content = soup.find('div', {'id': ['content', 'main-content', 'document']})
            
            if not main_content:
                # Last resort - find largest text block
                all_divs = soup.find_all('div')
                main_content = max(all_divs, key=lambda d: len(d.get_text()), default=None)
            
            if main_content:
                content['full_text'] = main_content.get_text(separator='\n', strip=True)
                
                # Extract articles
                articles = main_content.find_all(['div', 'p', 'section'], 
                                                class_=lambda x: x and ('article' in x.lower() or 'чл' in x.lower()))
                
                if not articles:
                    # Try finding by text pattern
                    article_pattern = re.compile(r'Чл\.?\s*\d+')
                    articles = main_content.find_all(text=article_pattern)
                
                for article in articles[:50]:  # Limit to first 50 articles
                    if hasattr(article, 'get_text'):
                        article_text = article.get_text(strip=True)
                    else:
                        article_text = str(article).strip()
                    
                    if article_text and len(article_text) > 10:
                        content['articles'].append(article_text)
                
                # Extract chapters
                chapters = main_content.find_all(['h1', 'h2', 'h3', 'div'], 
                                               class_=lambda x: x and ('chapter' in x.lower() or 'глава' in x.lower()))
                
                if not chapters:
                    # Try finding by text pattern
                    chapter_pattern = re.compile(r'Глава\s+[IVX]+|РАЗДЕЛ\s+[IVX]+', re.IGNORECASE)
                    chapters = main_content.find_all(text=chapter_pattern)
                
                for chapter in chapters:
                    if hasattr(chapter, 'get_text'):
                        chapter_text = chapter.get_text(strip=True)
                    else:
                        chapter_text = str(chapter).strip()
                    
                    if chapter_text:
                        content['chapters'].append(chapter_text)
            
            print(f"  ✅ Content: {len(content['full_text'])} chars, {len(content['articles'])} articles, {len(content['chapters'])} chapters")
            time.sleep(self.delay)
            
            return content
            
        except Exception as e:
            print(f"❌ Error fetching content from {law_url}: {e}")
            return None
    
    def scrape_priority_laws(self) -> List[Dict]:
        """
        Scrape all priority consumer protection laws directly
        
        Returns:
            List of dictionaries with law data
        """
        all_laws = []
        
        print(f"\n🚀 Starting scrape of {len(self.PRIORITY_LAWS)} priority laws from ciela.net...")
        print(f"📍 Base URL: {self.BASE_URL}")
        
        for i, law_info in enumerate(self.PRIORITY_LAWS, 1):
            print(f"\n[{i}/{len(self.PRIORITY_LAWS)}] {law_info['title']}")
            
            try:
                law_data = {
                    'title': law_info['title'],
                    'url': law_info['url'],
                    'source': 'ciela.net',
                    'scraped_at': datetime.utcnow().isoformat(),
                }
                
                # Fetch content
                law_content = self.get_law_content(law_info['url'])
                if law_content:
                    law_data.update(law_content)
                    all_laws.append(law_data)
                    print(f"  ✅ Success")
                else:
                    print(f"  ⚠️ No content retrieved")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        print(f"\n✅ Scraping complete. Collected {len(all_laws)} laws.")
        return all_laws
    
    def save_to_json(self, data: List[Dict], output_file: str = "ciela_net_laws.json"):
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
    scraper = CielaNetScraper(delay=2.0)
    
    # Scrape priority laws
    laws_data = scraper.scrape_priority_laws()
    
    # Save results
    if laws_data:
        scraper.save_to_json(laws_data, "data/ciela_net_laws.json")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"  Total laws: {len(laws_data)}")
        print(f"  Total articles: {sum(len(law.get('articles', [])) for law in laws_data)}")
        print(f"  Total text: {sum(len(law.get('full_text', '')) for law in laws_data):,} characters")
    
    return laws_data


if __name__ == "__main__":
    main()
