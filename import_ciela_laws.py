"""
Import Bulgarian laws from ciela.csv into the database.
Fetches actual law content from ciela.net and populates legal_documents and legal_articles tables.
"""

import csv
import time
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.legal_models import LegalDocument, LegalArticle
import re
from datetime import datetime

# Priority laws for consumer credit protection
PRIORITY_LAWS = [
    "ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ",  # Consumer Credit Law - HIGHEST PRIORITY
    "ЗАКОН ЗА КРЕДИТИТЕ ЗА НЕДВИЖИМИ ИМОТИ НА ПОТРЕБИТЕЛИ",  # Real Estate Credit Law
    "ЗАКОН ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ",  # Consumer Protection Law
    "ЗАКОН ЗА КРЕДИТНИТЕ ИНСТИТУЦИИ",  # Credit Institutions Law
    "ЗАКОН ЗА ЗАДЪЛЖЕНИЯТА И ДОГОВОРИТЕ",  # Obligations and Contracts Law
    "ЗАКОН ЗА НЕСЪСТОЯТЕЛНОСТ НА ФИЗИЧЕСКИТЕ ЛИЦА",  # Personal Insolvency Law
    "ЗАКОН ЗА ИПОТЕЧНИТЕ ОБЛИГАЦИИ",  # Mortgage Bonds Law
    "ЗАКОН ЗА ЗАЩИТА ОТ ДИСКРИМИНАЦИЯ",  # Anti-Discrimination Law
    "ЗАКОН ЗА КОМИСИЯТА ЗА ФИНАНСОВ НАДЗОР",  # Financial Supervision Commission Law
]

class CielaLawImporter:
    def __init__(self, db_path='credit_guardian.db', csv_path='ciela.csv'):
        self.db_path = db_path
        self.csv_path = csv_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def read_csv(self):
        """Read the ciela.csv file and return list of laws."""
        laws = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                laws.append({
                    'title': row['ttl'],
                    'url': row['ttl href']
                })
        return laws
    
    def fetch_law_content(self, url):
        """Fetch law content from ciela.net URL."""
        try:
            print(f"  Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main law content
            # Ciela.net typically has law content in specific divs
            content_div = soup.find('div', class_='law-content') or \
                         soup.find('div', class_='document-content') or \
                         soup.find('div', id='content') or \
                         soup.find('article') or \
                         soup.find('main')
            
            if not content_div:
                # Fallback: get all text content
                content_div = soup.find('body')
            
            if content_div:
                # Extract text content
                text = content_div.get_text(separator='\n', strip=True)
                
                # Clean up excessive whitespace
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = re.sub(r' +', ' ', text)
                
                # Extract articles (Bulgarian law articles typically start with "Чл." or "Член")
                articles = self.extract_articles(text)
                
                return {
                    'full_text': text[:50000],  # Limit to 50k chars
                    'articles': articles,
                    'summary': text[:1000]  # First 1000 chars as summary
                }
            
            print("  ⚠️ No content found")
            return None
            
        except requests.exceptions.Timeout:
            print(f"  ⏱️ Timeout")
            return None
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return None
    
    def extract_articles(self, text):
        """Extract individual articles from law text."""
        articles = []
        
        # Pattern for Bulgarian law articles: "Чл. 1." or "Член 1."
        pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.'
        
        matches = list(re.finditer(pattern, text))
        
        for i, match in enumerate(matches):
            article_number = match.group(1)
            start = match.start()
            
            # Get text until next article or end
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = min(start + 5000, len(text))  # Max 5000 chars per article
            
            article_text = text[start:end].strip()
            
            # Only include substantial articles (more than 50 chars)
            if len(article_text) > 50:
                articles.append({
                    'number': article_number,
                    'text': article_text
                })
        
        return articles
    
    def import_law(self, law_data, priority=False):
        """Import a single law into the database."""
        title = law_data['title']
        url = law_data['url']
        
        print(f"\n{'🔥' if priority else '📄'} {title}")
        
        # Check if already exists
        existing = self.session.query(LegalDocument).filter_by(title=title).first()
        if existing:
            print("  ✅ Already in database")
            return existing
        
        # Fetch content
        content = self.fetch_law_content(url)
        
        if not content:
            print("  ⚠️ Skipping - no content retrieved")
            return None
        
        # Create legal document
        doc = LegalDocument(
            title=title,
            document_type='law',
            source_url=url,
            full_text=content['full_text'],
            effective_date=None,  # Would need to parse from content
            is_active=True
        )
        
        self.session.add(doc)
        self.session.flush()  # Get the doc.id
        
        print(f"  ✅ Document imported (ID: {doc.id})")
        
        # Import articles
        article_count = 0
        for article_data in content['articles'][:100]:  # Limit to 100 articles per law
            article = LegalArticle(
                document_id=doc.id,
                article_number=article_data['number'],
                title=f"Член {article_data['number']}",
                content=article_data['text']
            )
            self.session.add(article)
            article_count += 1
        
        if article_count > 0:
            print(f"  ✅ {article_count} articles imported")
        
        self.session.commit()
        return doc
    
    def import_all(self, priority_only=False, max_laws=None):
        """Import laws from CSV file."""
        print("=" * 70)
        print("🇧🇬 BULGARIAN LAW IMPORT FROM CIELA.NET")
        print("=" * 70)
        
        laws = self.read_csv()
        print(f"\n📊 Total laws in CSV: {len(laws)}")
        
        # Separate priority and other laws
        priority_laws = []
        other_laws = []
        
        for law in laws:
            if any(priority in law['title'] for priority in PRIORITY_LAWS):
                priority_laws.append(law)
            else:
                other_laws.append(law)
        
        print(f"🔥 Priority laws: {len(priority_laws)}")
        print(f"📄 Other laws: {len(other_laws)}")
        
        # Import priority laws first
        print("\n" + "=" * 70)
        print("PHASE 1: PRIORITY CONSUMER CREDIT LAWS")
        print("=" * 70)
        
        imported_count = 0
        for law in priority_laws:
            try:
                result = self.import_law(law, priority=True)
                if result:
                    imported_count += 1
                time.sleep(2)  # Be respectful to the server
            except Exception as e:
                print(f"  ❌ Error importing {law['title']}: {str(e)}")
                self.session.rollback()
        
        print(f"\n✅ Priority laws imported: {imported_count}/{len(priority_laws)}")
        
        # Import other laws if requested
        if not priority_only and len(other_laws) > 0:
            print("\n" + "=" * 70)
            print("PHASE 2: OTHER LAWS")
            print("=" * 70)
            
            laws_to_import = other_laws[:max_laws] if max_laws else other_laws
            
            for i, law in enumerate(laws_to_import, 1):
                try:
                    result = self.import_law(law, priority=False)
                    if result:
                        imported_count += 1
                    
                    if i % 10 == 0:
                        print(f"\n📊 Progress: {i}/{len(laws_to_import)} laws processed")
                    
                    time.sleep(3)  # Be even more respectful for bulk imports
                except Exception as e:
                    print(f"  ❌ Error importing {law['title']}: {str(e)}")
                    self.session.rollback()
        
        print("\n" + "=" * 70)
        print("✅ IMPORT COMPLETE")
        print("=" * 70)
        print(f"Total laws imported: {imported_count}")
        
        # Summary statistics
        total_docs = self.session.query(LegalDocument).count()
        total_articles = self.session.query(LegalArticle).count()
        
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"  Legal Documents: {total_docs}")
        print(f"  Legal Articles: {total_articles}")
        
    def close(self):
        """Close database session."""
        self.session.close()


if __name__ == '__main__':
    print("🚀 Starting Bulgarian Law Import")
    print()
    
    importer = CielaLawImporter()
    
    try:
        # Import priority laws only by default
        # Change priority_only=False to import all laws (will take much longer)
        importer.import_all(priority_only=True)
    finally:
        importer.close()
    
    print("\n✅ Import script completed!")
    print("You can now use the imported data for AI agent training and contract analysis.")
