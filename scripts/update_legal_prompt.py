#!/usr/bin/env python
# scripts/update_legal_prompt.py
"""
Script to regenerate the legal_prompt.txt from database content.

This script queries the legal_documents, legal_articles, and article_ingestion tables
to build a comprehensive system prompt with the most relevant and up-to-date legal
information for credit contract analysis.

Usage:
    python scripts/update_legal_prompt.py
    python scripts/update_legal_prompt.py --output custom_prompt.txt
    python scripts/update_legal_prompt.py --max-articles 100
"""

import argparse
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output paths
DEFAULT_OUTPUT = PROJECT_ROOT / "ai_agent" / "legal_prompt.txt"
DB_PATH = PROJECT_ROOT / "credit_guardian.db"


def get_db_connection() -> sqlite3.Connection:
    """Open database connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    return sqlite3.connect(str(DB_PATH))


def get_key_documents(conn: sqlite3.Connection) -> List[Dict]:
    """Get key legal documents relevant to consumer credit protection."""
    cursor = conn.cursor()
    
    # Priority keywords for credit-related laws
    keywords = [
        '%потребителски кредит%',
        '%защита на потребител%',
        '%задължения и договори%',
        '%кредитни институции%',
        '%ЗПК%',
        '%ЗЗП%',
        '%ЗЗД%',
    ]
    
    documents = []
    seen_ids = set()
    
    for keyword in keywords:
        cursor.execute("""
            SELECT id, title, document_type, full_text
            FROM legal_documents
            WHERE (title LIKE ? OR full_text LIKE ?)
            AND is_active = 1
            ORDER BY id
            LIMIT 10
        """, (keyword, keyword))
        
        for row in cursor.fetchall():
            doc_id, title, doc_type, full_text = row
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                documents.append({
                    'id': doc_id,
                    'title': title,
                    'document_type': doc_type,
                    'full_text': full_text or '',
                })
    
    return documents


def get_key_articles(conn: sqlite3.Connection, max_articles: int = 50) -> List[Dict]:
    """Get most important articles from article_ingestion table."""
    cursor = conn.cursor()
    
    # Try article_ingestion first (has tags and better structure)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='article_ingestion'
    """)
    
    if cursor.fetchone():
        # Use article_ingestion table
        cursor.execute("""
            SELECT 
                ai.article_id,
                ai.document_id,
                ai.article_number,
                ai.content,
                ai.chapter_title,
                ai.section_title,
                ai.tag_primary,
                ld.title as document_title
            FROM article_ingestion ai
            LEFT JOIN legal_documents ld ON ai.document_id = ld.id
            WHERE ai.tag_primary IN (
                'ГПР', 'такси', 'лихви', 'неустойки', 'потребител', 
                'кредит', 'договор', 'нарушения', 'забрани', 'права'
            )
            ORDER BY 
                CASE ai.tag_primary
                    WHEN 'ГПР' THEN 1
                    WHEN 'такси' THEN 2
                    WHEN 'забрани' THEN 3
                    WHEN 'нарушения' THEN 4
                    WHEN 'права' THEN 5
                    ELSE 10
                END,
                ai.article_id
            LIMIT ?
        """, (max_articles,))
    else:
        # Fallback to legal_articles
        cursor.execute("""
            SELECT 
                la.id as article_id,
                la.document_id,
                la.article_number,
                la.content,
                la.chapter_title,
                la.section_title,
                NULL as tag_primary,
                ld.title as document_title
            FROM legal_articles la
            LEFT JOIN legal_documents ld ON la.document_id = ld.id
            WHERE la.content LIKE '%ГПР%'
               OR la.content LIKE '%такс%'
               OR la.content LIKE '%потребител%'
               OR la.content LIKE '%забран%'
            ORDER BY la.id
            LIMIT ?
        """, (max_articles,))
    
    articles = []
    for row in cursor.fetchall():
        (article_id, document_id, article_number, content, 
         chapter_title, section_title, tag_primary, document_title) = row
        articles.append({
            'article_id': article_id,
            'document_id': document_id,
            'article_number': article_number or '',
            'content': content or '',
            'chapter_title': chapter_title or '',
            'section_title': section_title or '',
            'tag_primary': tag_primary or '',
            'document_title': document_title or '',
        })
    
    return articles


def get_bnb_rate(conn: sqlite3.Connection) -> Tuple[float, str]:
    """Get current BNB base interest rate if available."""
    cursor = conn.cursor()
    
    # Check if we have BNB rates data
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='bnb_rates'
    """)
    
    if cursor.fetchone():
        cursor.execute("""
            SELECT rate, effective_date 
            FROM bnb_rates 
            ORDER BY effective_date DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
    
    # Default BNB rate for 2025
    return 5.75, "2025-01-01"


def build_prompt(documents: List[Dict], articles: List[Dict], 
                 bnb_rate: float, bnb_date: str) -> str:
    """Build the comprehensive legal prompt."""
    
    # Calculate max APR
    max_apr = min(5 * bnb_rate, 50.0)
    
    prompt = f"""Вие сте експерт по защита на потребителските права при кредити в България.

============================================================
АКТУАЛНА ИНФОРМАЦИЯ (към {datetime.now().strftime('%d.%m.%Y')})
============================================================

МАКСИМАЛЕН ГПР (чл. 19, ал. 4 ЗПК):
- Базов лихвен процент на БНБ: {bnb_rate:.2f}% (от {bnb_date})
- Максимален ГПР = 5 × {bnb_rate:.2f}% = {5 * bnb_rate:.2f}%
- ЗАКОНОВ ТАВАН: {max_apr:.2f}%
- Всеки ГПР над {max_apr:.2f}% е НЕЗАКОНЕН!

============================================================
КЛЮЧОВИ ЗАКОНИ
============================================================

1. ЗАКОН ЗА ПОТРЕБИТЕЛСКИЯ КРЕДИТ (ЗПК):
   - чл. 10а: ЗАБРАНА за такси "бързо разглеждане", "управление на кредита", "усвояване"
   - чл. 11, ал. 1: Задължителна информация (ГПР, общ размер, график)
   - чл. 19, ал. 4: Максимален ГПР = петкратен размер на законната лихва
   - чл. 22: Недействителност на договор при нарушение на ЗПК
   
2. ЗАКОН ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ (ЗЗП):
   - чл. 143-146: Неравноправни клаузи
   - чл. 147: Последици от неравноправност
   
3. ЗАКОН ЗА ЗАДЪЛЖЕНИЯТА И ДОГОВОРИТЕ (ЗЗД):
   - чл. 9: Добросъвестност и честност
   - чл. 26: Недействителност при противоречие със закона

============================================================
ВАШАТА ЗАДАЧА
============================================================

При анализ на договор:
1. Идентифицирайте ВСИЧКИ нарушения с точни законови цитати
2. Изчислете РЕАЛНИЯ ГПР (включващ всички такси)
3. Оценете ФИНАНСОВОТО ВЛИЯНИЕ на всяко нарушение
4. Класифицирайте тежестта: critical | high | medium | low

ВИНАГИ:
- Отговаряйте на БЪЛГАРСКИ език
- Връщайте ВАЛИДЕН JSON
- Използвайте ТОЧНИ цитати (чл. X, ал. Y, т. Z)

"""
    
    # Add key articles from database
    if articles:
        prompt += """
============================================================
РЕЛЕВАНТНИ ЗАКОНОВИ ТЕКСТОВЕ (от базата данни)
============================================================

"""
        for art in articles[:30]:  # Limit to 30 most relevant
            doc_title = art['document_title'] or 'Неизвестен документ'
            art_num = art['article_number']
            content = art['content'][:500]  # Truncate long articles
            
            if content.strip():
                prompt += f"[{doc_title}] {art_num}:\n{content}\n\n"
    
    # Add output structure
    prompt += """
============================================================
СТРУКТУРА НА АНАЛИЗА (JSON)
============================================================

{
  "contract_number": "номер от текста или UNKNOWN",
  "creditor": "име на кредитора",
  "creditor_eik": "ЕИК/БУЛСТАТ номер",
  "principal": число (главница в лева),
  "stated_apr": число (обявен ГПР %),
  "stated_interest_amount": число (обявена лихва),
  "contract_date": "YYYY-MM-DD",
  "term_months": число,
  "fees": [
    {
      "type": "пълно име на таксата",
      "amount": число,
      "is_illegal": true/false,
      "basis": "чл. X, ал. Y ЗАКОН"
    }
  ],
  "total_disclosed_cost": число (обща декларирана сума),
  "total_actual_cost": число (реална обща цена),
  "calculated_real_apr": число (реален ГПР %),
  "violations": [
    {
      "type": "illegal_fee | apr_exceeded | incorrect_disclosure | unfair_clause",
      "description": "Подробно описание",
      "severity": "critical | high | medium | low",
      "legal_basis": "чл. X, ал. Y ЗАКОН",
      "financial_impact": число (загуба в лева)
    }
  ],
  "recommendations": ["препоръка 1", "препоръка 2"],
  "summary": "Кратко резюме (2-3 изречения)"
}
"""
    
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate legal_prompt.txt from database content"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help=f"Output file path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--max-articles", "-m",
        type=int,
        default=50,
        help="Maximum number of articles to include (default: 50)"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Legal Prompt Generator")
    print("=" * 60)
    
    # Connect to database
    try:
        conn = get_db_connection()
        print(f"✓ Connected to database: {DB_PATH}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        print("  Run the import scripts first to create the database.")
        sys.exit(1)
    
    # Get documents and articles
    print("\nFetching legal content from database...")
    
    documents = get_key_documents(conn)
    print(f"  Found {len(documents)} key documents")
    
    articles = get_key_articles(conn, max_articles=args.max_articles)
    print(f"  Found {len(articles)} relevant articles")
    
    bnb_rate, bnb_date = get_bnb_rate(conn)
    print(f"  BNB base rate: {bnb_rate}% (from {bnb_date})")
    
    conn.close()
    
    # Build prompt
    print("\nBuilding legal prompt...")
    prompt = build_prompt(documents, articles, bnb_rate, bnb_date)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"\n✓ Prompt written to: {output_path}")
    print(f"  Size: {len(prompt):,} characters")
    print(f"  Lines: {prompt.count(chr(10)):,}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUCCESS")
    print("=" * 60)
    print(f"  Max APR (ноември 2025): {min(5 * bnb_rate, 50.0):.2f}%")
    print(f"  Articles included: {min(len(articles), 30)}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()

