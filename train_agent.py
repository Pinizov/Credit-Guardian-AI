"""
Training orchestrator for Credit Guardian AI Agent
Imports data from lex.bg and apis.bg into the knowledge base
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Session, Creditor, Violation
from database.legal_models import LegalDocument, LegalArticle, ConsumerCase, TrainingExample, Base
from database.models import engine
from scrapers.lex_bg_scraper import LexBgScraper
from scrapers.apis_bg_scraper import ApisBgScraper
from scrapers.ciela_net_scraper import CielaNetScraper


class AgentTrainer:
    """Orchestrates AI agent training with Bulgarian legal data"""
    
    def __init__(self):
        self.session = Session()
        
        # Create tables for legal knowledge base
        print("📋 Creating legal knowledge base tables...")
        Base.metadata.create_all(engine)
        print("✅ Tables created")
    
    def scrape_legal_data(self, use_cached: bool = True) -> Dict:
        """
        Scrape data from ciela.net, lex.bg and apis.bg
        
        Args:
            use_cached: Use cached data if available
            
        Returns:
            Dictionary with all scraped data
        """
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        ciela_file = data_dir / "ciela_net_laws.json"
        lex_file = data_dir / "lex_bg_laws.json"
        apis_file = data_dir / "apis_bg_data.json"
        
        # Scrape ciela.net laws (PRIMARY SOURCE)
        if use_cached and ciela_file.exists():
            print(f"📂 Loading cached ciela.net data from {ciela_file}")
            with open(ciela_file, 'r', encoding='utf-8') as f:
                ciela_data = json.load(f)
        else:
            print("🚀 Scraping ciela.net (Svobodna Zona)...")
            scraper = CielaNetScraper(delay=2.0)
            ciela_data = scraper.scrape_priority_laws()
            scraper.save_to_json(ciela_data, str(ciela_file))
        
        # Scrape lex.bg laws
        if use_cached and lex_file.exists():
            print(f"📂 Loading cached lex.bg data from {lex_file}")
            with open(lex_file, 'r', encoding='utf-8') as f:
                lex_data = json.load(f)
        else:
            print("🚀 Scraping lex.bg...")
            scraper = LexBgScraper(delay=2.0)
            lex_data = scraper.scrape_priority_laws()
            scraper.save_to_json(lex_data, str(lex_file))
        
        # Scrape apis.bg violations
        if use_cached and apis_file.exists():
            print(f"📂 Loading cached apis.bg data from {apis_file}")
            with open(apis_file, 'r', encoding='utf-8') as f:
                apis_data = json.load(f)
        else:
            print("🚀 Scraping apis.bg...")
            scraper = ApisBgScraper(delay=2.0)
            apis_data = scraper.scrape_all(max_violation_pages=3)
            scraper.save_to_json(apis_data, str(apis_file))
        
        # Combine ciela.net and lex.bg legal documents
        all_legal_docs = ciela_data + lex_data
        
        return {
            'legal_docs': all_legal_docs,
            'violations': apis_data.get('violations', []),
            'blacklist': apis_data.get('blacklist', []),
        }
    
    def import_legal_documents(self, legal_docs: List[Dict]) -> int:
        """
        Import legal documents into database
        
        Args:
            legal_docs: List of legal document dictionaries
            
        Returns:
            Number of documents imported
        """
        print(f"\n📚 Importing {len(legal_docs)} legal documents...")
        
        imported = 0
        for doc_data in legal_docs:
            try:
                # Check if already exists
                existing = self.session.query(LegalDocument).filter_by(
                    title=doc_data.get('title')
                ).first()
                
                if existing:
                    print(f"  ⏭️ Skipping existing: {doc_data.get('title')}")
                    continue
                
                # Create legal document
                doc = LegalDocument(
                    title=doc_data.get('title', ''),
                    document_type='law',
                    full_text=doc_data.get('full_text', ''),
                    source_url=doc_data.get('url', ''),
                    is_active=True,
                )
                self.session.add(doc)
                self.session.flush()
                
                # Import articles
                articles = doc_data.get('articles', [])
                for i, article_text in enumerate(articles[:50]):  # Limit to first 50 articles
                    article = LegalArticle(
                        document_id=doc.id,
                        article_number=f"Art. {i+1}",
                        content=article_text,
                    )
                    self.session.add(article)
                
                self.session.commit()
                print(f"  ✅ Imported: {doc.title} ({len(articles)} articles)")
                imported += 1
                
            except Exception as e:
                print(f"  ❌ Error importing {doc_data.get('title')}: {e}")
                self.session.rollback()
        
        print(f"✅ Imported {imported} legal documents")
        return imported
    
    def import_violations(self, violations: List[Dict]) -> int:
        """
        Import violation records from apis.bg
        
        Args:
            violations: List of violation dictionaries
            
        Returns:
            Number of violations imported
        """
        print(f"\n⚖️ Importing {len(violations)} violation records...")
        
        imported = 0
        for viol_data in violations:
            try:
                company_name = viol_data.get('company', 'Unknown')
                
                # Find or create creditor
                creditor = self.session.query(Creditor).filter_by(name=company_name).first()
                if not creditor:
                    creditor = Creditor(
                        name=company_name,
                        type='non-bank',
                        violations_count=0,
                    )
                    self.session.add(creditor)
                    self.session.flush()
                
                # Create violation record
                violation = Violation(
                    creditor_id=creditor.id,
                    violation_type='consumer_protection',
                    description=viol_data.get('description', ''),
                    decision_number=viol_data.get('decision_number', ''),
                    authority='APIS',
                    penalty_amount=viol_data.get('penalty_amount'),
                    source_url=viol_data.get('url', ''),
                    severity='medium',
                )
                self.session.add(violation)
                
                # Update creditor stats
                creditor.violations_count += 1
                creditor.recalc_risk_score()
                
                self.session.commit()
                imported += 1
                
            except Exception as e:
                print(f"  ❌ Error importing violation: {e}")
                self.session.rollback()
        
        print(f"✅ Imported {imported} violations")
        return imported
    
    def import_blacklist(self, blacklist: List[Dict]) -> int:
        """
        Import blacklisted companies
        
        Args:
            blacklist: List of blacklisted entities
            
        Returns:
            Number of entities imported
        """
        print(f"\n🚫 Importing {len(blacklist)} blacklisted entities...")
        
        imported = 0
        for entity in blacklist:
            try:
                company_name = entity.get('name', 'Unknown')
                bulstat = entity.get('bulstat')
                
                # Find or create creditor
                creditor = self.session.query(Creditor).filter_by(name=company_name).first()
                if not creditor and bulstat:
                    creditor = self.session.query(Creditor).filter_by(bulstat=bulstat).first()
                
                if not creditor:
                    creditor = Creditor(
                        name=company_name,
                        bulstat=bulstat,
                        type='non-bank',
                        is_blacklisted=True,
                    )
                    self.session.add(creditor)
                else:
                    creditor.is_blacklisted = True
                
                self.session.commit()
                imported += 1
                
            except Exception as e:
                print(f"  ❌ Error importing blacklist entry: {e}")
                self.session.rollback()
        
        print(f"✅ Imported {imported} blacklisted entities")
        return imported
    
    def generate_training_examples(self) -> int:
        """
        Generate training examples from imported data
        
        Returns:
            Number of examples generated
        """
        print(f"\n🎓 Generating training examples...")
        
        generated = 0
        
        # Example 1: GPR calculation from legal text
        try:
            gpr_example = TrainingExample(
                category='gpr_calculation',
                input_text='Кредит от 1000 лв за 12 месеца, лихва 10% годишно, такса обработка 50 лв',
                expected_output='ГПР трябва да включва лихвата и всички такси. При тези параметри ГПР е приблизително 15.2%',
                source='synthetic',
                is_validated=True,
            )
            self.session.add(gpr_example)
            generated += 1
        except Exception as e:
            print(f"  ❌ Error generating example: {e}")
        
        # Example 2: Clause detection
        try:
            clause_example = TrainingExample(
                category='clause_detection',
                input_text='Кредиторът има право едностранно да променя лихвения процент без предизвестие',
                expected_output='НЕРАВНОПРАВНА КЛАУЗА: Едностранната промяна на договорни условия без предизвестие е забранена по ЗПК чл. 11',
                source='lex.bg',
                is_validated=True,
            )
            self.session.add(clause_example)
            generated += 1
        except Exception as e:
            print(f"  ❌ Error generating example: {e}")
        
        self.session.commit()
        print(f"✅ Generated {generated} training examples")
        return generated
    
    def train_agent(self, use_cached: bool = False):
        """
        Full training pipeline
        
        Args:
            use_cached: Use cached scraped data if available
        """
        print("\n" + "="*60)
        print("🎯 CREDIT GUARDIAN AI AGENT - TRAINING PIPELINE")
        print("="*60)
        
        # Step 1: Scrape data
        print("\n📥 STEP 1: Data Collection")
        data = self.scrape_legal_data(use_cached=use_cached)
        
        # Step 2: Import legal documents
        print("\n📥 STEP 2: Import Legal Knowledge Base")
        self.import_legal_documents(data['legal_docs'])
        
        # Step 3: Import violations
        print("\n📥 STEP 3: Import Violation Records")
        self.import_violations(data['violations'])
        
        # Step 4: Import blacklist
        print("\n📥 STEP 4: Import Blacklist")
        self.import_blacklist(data['blacklist'])
        
        # Step 5: Generate training examples
        print("\n📥 STEP 5: Generate Training Examples")
        self.generate_training_examples()
        
        # Summary
        print("\n" + "="*60)
        print("✅ TRAINING COMPLETE!")
        print("="*60)
        
        # Statistics
        legal_docs = self.session.query(LegalDocument).count()
        violations = self.session.query(Violation).count()
        creditors = self.session.query(Creditor).count()
        blacklisted = self.session.query(Creditor).filter_by(is_blacklisted=True).count()
        training_examples = self.session.query(TrainingExample).count()
        
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"  - Legal Documents: {legal_docs}")
        print(f"  - Violation Records: {violations}")
        print(f"  - Creditors Tracked: {creditors}")
        print(f"  - Blacklisted Entities: {blacklisted}")
        print(f"  - Training Examples: {training_examples}")
        print()


def main():
    """Main execution function"""
    trainer = AgentTrainer()
    
    # Run training pipeline
    trainer.train_agent(use_cached=False)  # Set to True to use cached data


if __name__ == "__main__":
    main()
