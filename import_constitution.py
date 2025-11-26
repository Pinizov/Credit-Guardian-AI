C:/credit-guardian/.venv/Scripts/python.exe advanced_tagging.py
C:/credit-guardian/.venv/Scripts/python.exe create_ingestion_view.py"""
Import Bulgarian Constitution from ciela.net
Special import script for the Constitution of the Republic of Bulgaria
"""

import time
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.legal_models import LegalDocument, LegalArticle
import re

class ConstitutionImporter:
    def __init__(self, db_path='credit_guardian.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_articles(self, text):
        """Extract individual articles from constitution text."""
        articles = []
        
        # Pattern for Bulgarian constitution articles: "Чл. 1." or "Член 1."
        pattern = r'(?:Чл\.|Член)\s*(\d+[а-я]?)\.'
        
        matches = list(re.finditer(pattern, text))
        
        for i, match in enumerate(matches):
            article_number = match.group(1)
            start = match.start()
            
            # Get text until next article or end
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = min(start + 5000, len(text))
            
            article_text = text[start:end].strip()
            
            # Only include substantial articles (more than 50 chars)
            if len(article_text) > 50:
                articles.append({
                    'number': article_number,
                    'text': article_text
                })
        
        return articles
    
    def fetch_constitution(self):
        """Fetch Bulgarian Constitution from ciela.net."""
        url = "https://www.ciela.net/svobodna-zona-normativi/view/521957377/konstitutsiya-na-republika-balgariya"
        
        print("=" * 70)
        print("🇧🇬 IMPORTING BULGARIAN CONSTITUTION")
        print("=" * 70)
        print(f"\n📜 Конституция на Република България")
        print(f"🔗 URL: {url}")
        
        # Check if already exists
        existing = self.session.query(LegalDocument).filter_by(
            title='КОНСТИТУЦИЯ НА РЕПУБЛИКА БЪЛГАРИЯ'
        ).first()
        
        if existing:
            print("✅ Constitution already in database")
            print(f"   Document ID: {existing.id}")
            article_count = self.session.query(LegalArticle).filter_by(
                document_id=existing.id
            ).count()
            print(f"   Articles: {article_count}")
            return existing
        
        print("\n📥 Fetching constitution content...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main content
            content_div = soup.find('div', class_='law-content') or \
                         soup.find('div', class_='document-content') or \
                         soup.find('div', id='content') or \
                         soup.find('article') or \
                         soup.find('main') or \
                         soup.find('body')
            
            if not content_div:
                print("⚠️ No content found")
                return None
            
            # Extract text content
            text = content_div.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            
            print(f"✅ Content fetched: {len(text)} characters")
            
            # Extract articles
            print("📖 Extracting articles...")
            articles = self.extract_articles(text)
            print(f"✅ Found {len(articles)} articles")
            
            # Create legal document
            print("\n💾 Saving to database...")
            doc = LegalDocument(
                title='КОНСТИТУЦИЯ НА РЕПУБЛИКА БЪЛГАРИЯ',
                document_type='constitution',
                source_url=url,
                full_text=text[:50000],  # Limit to 50k chars
                is_active=True
            )
            
            self.session.add(doc)
            self.session.flush()
            
            print(f"✅ Document saved (ID: {doc.id})")
            
            # Import articles
            article_count = 0
            for article_data in articles[:200]:  # Limit to 200 articles
                article = LegalArticle(
                    document_id=doc.id,
                    article_number=article_data['number'],
                    title=f"Член {article_data['number']}",
                    content=article_data['text']
                )
                self.session.add(article)
                article_count += 1
            
            self.session.commit()
            print(f"✅ {article_count} articles saved")
            
            print("\n" + "=" * 70)
            print("✅ CONSTITUTION IMPORT COMPLETE")
            print("=" * 70)
            print(f"Document ID: {doc.id}")
            print(f"Articles: {article_count}")
            print(f"Text length: {len(text)} characters")
            
            return doc
            
        except requests.exceptions.Timeout:
            print("⏱️ Request timeout")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.session.rollback()
            return None
    
    def show_sample(self):
        """Display sample articles from the constitution."""
        doc = self.session.query(LegalDocument).filter_by(
            title='КОНСТИТУЦИЯ НА РЕПУБЛИКА БЪЛГАРИЯ'
        ).first()
        
        if not doc:
            print("⚠️ Constitution not found in database")
            return
        
        print("\n" + "=" * 70)
        print("📖 SAMPLE CONSTITUTIONAL ARTICLES")
        print("=" * 70)
        
        articles = self.session.query(LegalArticle).filter_by(
            document_id=doc.id
        ).limit(5).all()
        
        for article in articles:
            print(f"\n{'=' * 70}")
            print(f"🔹 ЧЛЕН {article.article_number}")
            print(f"{'=' * 70}")
            preview = article.content[:500] + "..." if len(article.content) > 500 else article.content
            print(preview)
    
    def close(self):
        """Close database session."""
        self.session.close()


if __name__ == '__main__':
    importer = ConstitutionImporter()
    
    try:
        result = importer.fetch_constitution()
        
        if result:
            importer.show_sample()
            
            # Summary statistics
            print("\n" + "=" * 70)
            print("📊 DATABASE STATISTICS")
            print("=" * 70)
            
            total_docs = importer.session.query(LegalDocument).count()
            total_articles = importer.session.query(LegalArticle).count()
            
            print(f"Total Legal Documents: {total_docs}")
            print(f"Total Legal Articles: {total_articles}")
            
    finally:
        importer.close()
    
    print("\n✅ Import complete!")
