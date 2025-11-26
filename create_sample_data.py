"""
Demo script with synthetic training data
Creates sample legal and violation data without web scraping
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.models import Session, Creditor, Violation, engine
from database.legal_models import LegalDocument, LegalArticle, TrainingExample, Base


def create_sample_data():
    """Create sample training data without web scraping"""
    
    print("\n" + "="*60)
    print("🎯 CREATING SAMPLE TRAINING DATA")
    print("="*60)
    
    # Create tables
    print("\n📋 Creating database tables...")
    Base.metadata.create_all(engine)
    print("✅ Tables created")
    
    session = Session()
    
    # Create sample legal document
    print("\n📚 Creating sample legal document...")
    try:
        doc = LegalDocument(
            title="Закон за потребителския кредит",
            document_type="law",
            document_number="ДВ. бр. 18 от 2010г.",
            full_text="Закон за потребителския кредит - регулира отношенията при предоставяне на потребителски кредит",
            source_url="https://lex.bg/laws/ldoc/2135540562",
            is_active=True,
        )
        session.add(doc)
        session.flush()
        
        # Add articles
        articles_text = [
            "Чл. 10. Годишният процент на разходите включва лихвата и всички такси и разходи",
            "Чл. 11. Забранено е едностранното изменение на договорни условия без предизвестие",
            "Чл. 12. Кредиторът е длъжен да предостави пълна информация за всички разходи",
        ]
        
        for i, text in enumerate(articles_text, 1):
            article = LegalArticle(
                document_id=doc.id,
                article_number=f"Чл. {i+9}",
                content=text,
            )
            session.add(article)
        
        session.commit()
        print("✅ Created legal document with 3 articles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    
    # Create sample creditors and violations
    print("\n⚖️ Creating sample violations...")
    try:
        creditors_data = [
            {"name": "Бързи Пари ЕООД", "bulstat": "12345678", "violations": 3},
            {"name": "Експрес Финанси АД", "bulstat": "87654321", "violations": 1},
            {"name": "Лесен Кредит ООД", "bulstat": "11223344", "violations": 5},
        ]
        
        for cred_data in creditors_data:
            creditor = Creditor(
                name=cred_data["name"],
                bulstat=cred_data["bulstat"],
                type="non-bank",
                violations_count=cred_data["violations"],
                risk_score=cred_data["violations"] * 1.5,
            )
            session.add(creditor)
            session.flush()
            
            # Add violations
            for i in range(cred_data["violations"]):
                violation = Violation(
                    creditor_id=creditor.id,
                    violation_type="unfair_practice",
                    description=f"Неправомерно начисляване на такси и лихви",
                    authority="КЗП",
                    penalty_amount=5000.0 * (i + 1),
                    severity="high" if i == 0 else "medium",
                )
                session.add(violation)
        
        session.commit()
        print("✅ Created 3 creditors with violations")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    
    # Create training examples
    print("\n🎓 Creating training examples...")
    try:
        examples = [
            {
                "category": "gpr_calculation",
                "input": "Кредит 1000 лв за 12 месеца, лихва 10%, такса обработка 50 лв",
                "output": "ГПР = 15.2% (включва лихва и такси)",
            },
            {
                "category": "clause_detection",
                "input": "Кредиторът може да промени лихвата без предизвестие",
                "output": "НЕРАВНОПРАВНА КЛАУЗА: Нарушава чл. 11 ЗПК",
            },
            {
                "category": "violation_check",
                "input": "Такса за предсрочно погасяване 5%",
                "output": "НАРУШЕНИЕ: Забранено по ЗПК чл. 15",
            },
        ]
        
        for ex in examples:
            example = TrainingExample(
                category=ex["category"],
                input_text=ex["input"],
                expected_output=ex["output"],
                source="synthetic",
                is_validated=True,
            )
            session.add(example)
        
        session.commit()
        print("✅ Created 3 training examples")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    
    # Print statistics
    print("\n" + "="*60)
    print("✅ SAMPLE DATA CREATION COMPLETE!")
    print("="*60)
    
    legal_docs = session.query(LegalDocument).count()
    articles = session.query(LegalArticle).count()
    violations = session.query(Violation).count()
    creditors = session.query(Creditor).count()
    training_examples = session.query(TrainingExample).count()
    
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"  - Legal Documents: {legal_docs}")
    print(f"  - Legal Articles: {articles}")
    print(f"  - Violation Records: {violations}")
    print(f"  - Creditors Tracked: {creditors}")
    print(f"  - Training Examples: {training_examples}")
    print()
    
    session.close()


if __name__ == "__main__":
    create_sample_data()
