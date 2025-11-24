# Enhanced Training Data - Ciela.net Alternative

## 🔒 Ciela.net Access Limitation

The ciela.net website (https://www.ciela.net/svobodna-zona-normativi/category/) uses:
- **Dynamic JavaScript rendering** - Content loads via AJAX after page load
- **Possible authentication** - May require login to access full legal texts
- **Anti-scraping protection** - Standard HTTP requests return empty content

## ✅ Current Solution

Since direct web scraping is limited, we have:

### 1. Sample Training Data Created
- ✅ 1 Legal Document (Закон за потребителския кредит)
- ✅ 3 Legal Articles with key consumer credit provisions
- ✅ 3 Creditors with 9 violation records
- ✅ 3 Training examples for AI evaluation

### 2. Manual Data Enhancement Options

**Option A: Manual Entry from Ciela.net**
```python
# Run this to add laws manually:
python enhance_legal_data.py
```

**Option B: Import from PDF/Text Files**
- Download laws from ciela.net as PDF
- Place in `data/legal_pdfs/` folder
- Run PDF import tool

**Option C: API Integration** (if available)
- Ciela.net may offer paid API access
- Contact: info@ciela.net
- Pricing: Enterprise plans available

## 📚 Key Bulgarian Consumer Laws (for Manual Entry)

### Закон за потребителския кредит (Consumer Credit Act)
- **Key Articles for Database:**
  - Чл. 10: ГПР calculation requirements
  - Чл. 11: Prohibition of unilateral contract changes
  - Чл. 12: Mandatory fee disclosures
  - Чл. 15: Early repayment rights

### Закон за защита на потребителите (Consumer Protection Act)
- **Key Articles:**
  - Чл. 143-147: Unfair commercial practices
  - Чл. 148-149: Misleading actions/omissions
  - Чл. 150: Aggressive practices

### Закон за кредитните институции (Credit Institutions Act)
- **Key Articles:**
  - Чл. 62: Licensing requirements
  - Чл. 87: Interest rate limits
  - Чл. 99: Supervision by BNB

## 🔧 Enhanced Data Collection Script

```python
# File: enhance_legal_data.py
from database.models import Session
from database.legal_models import LegalDocument, LegalArticle

session = Session()

# Add more articles manually
new_articles = [
    {
        'title': 'Закон за потребителския кредит',
        'article': 'Чл. 15',
        'content': 'Потребителят има право на предсрочно погасяване на кредита без такси...'
    },
    # Add more...
]

for article_data in new_articles:
    # Find document
    doc = session.query(LegalDocument).filter_by(title=article_data['title']).first()
    if doc:
        article = LegalArticle(
            document_id=doc.id,
            article_number=article_data['article'],
            content=article_data['content']
        )
        session.add(article)

session.commit()
print("✅ Enhanced data added")
```

## 🌐 Alternative Legal Data Sources

### Free Bulgarian Legal Databases:
1. **lex.bg** - https://www.lex.bg (Government official)
2. **parliament.bg** - https://www.parliament.bg/bg/laws (National Assembly)
3. **apis.bg** - https://www.apis.bg (Consumer Protection Commission)
4. **bnb.bg** - https://www.bnb.bg (Bulgarian National Bank regulations)

### Commercial Sources:
1. **Ciela.net** - Paid access to complete database
2. **Apis.bg Premium** - Enhanced violation data
3. **Legal databases** - Sibi, Norma Plus

## 📊 Current AI Agent Capabilities

Despite limited web scraping, the agent can still:
- ✅ Analyze contracts for unfair clauses
- ✅ Calculate and verify GPR
- ✅ Check creditor violation history
- ✅ Generate consumer complaints
- ✅ Reference existing legal articles

## 🚀 Next Steps

1. **Use existing data** - Train with sample data (already working)
2. **Manual enhancement** - Add more articles as needed
3. **PDF import** - Download laws as PDF, extract text
4. **API integration** - Explore paid API options
5. **Hybrid approach** - Combine multiple sources

---

**Current Status:** ✅ **System operational with sample data**  
**Database:** `C:\credit-guardian\credit_guardian.db` (56 KB + new tables)  
**Training Data:** Ready for AI agent evaluation
