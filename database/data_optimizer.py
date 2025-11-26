"""
Data Structure Optimizer
Оптимизация на структурата на данните и индексиране
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from sqlalchemy import Index, text
from database.models import Base, engine, Creditor, Violation
from database.legal_models import LegalDocument as LegalDoc

logger = logging.getLogger(__name__)


class DataOptimizer:
    """Optimize database structure and create indexes"""
    
    def __init__(self):
        self.engine = engine
    
    def create_indexes(self):
        """Create optimized indexes for better query performance"""
        logger.info("Creating database indexes...")
        
        try:
            with self.engine.connect() as conn:
                # Indexes for Creditor table
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_creditor_name_lower 
                        ON creditors(LOWER(name))
                    """))
                    logger.info("✓ Created index on creditor name (lowercase)")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_creditor_bulstat_lower 
                        ON creditors(LOWER(bulstat))
                    """))
                    logger.info("✓ Created index on creditor bulstat (lowercase)")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_creditor_type_risk 
                        ON creditors(type, risk_score DESC)
                    """))
                    logger.info("✓ Created composite index on creditor type and risk_score")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                # Indexes for Violation table
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_violation_creditor_severity 
                        ON violations(creditor_id, severity)
                    """))
                    logger.info("✓ Created composite index on violation creditor and severity")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                # Indexes for LegalDocument table
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_legal_doc_title_lower 
                        ON legal_documents(LOWER(title))
                    """))
                    logger.info("✓ Created index on legal document title (lowercase)")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_legal_doc_type_active 
                        ON legal_documents(document_type, is_active)
                    """))
                    logger.info("✓ Created composite index on legal document type and active status")
                except Exception as e:
                    logger.debug(f"Index already exists or error: {e}")
                
                # Full-text search index (if supported)
                try:
                    conn.execute(text("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS legal_documents_fts USING fts5(
                            title, full_text, document_type
                        )
                    """))
                    logger.info("✓ Created FTS5 virtual table for full-text search")
                except Exception as e:
                    logger.debug(f"FTS5 not available or error: {e}")
                
                conn.commit()
                logger.info("✅ All indexes created successfully")
                
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    def optimize_tables(self):
        """Optimize database tables (VACUUM, ANALYZE)"""
        logger.info("Optimizing database tables...")
        
        try:
            with self.engine.connect() as conn:
                # SQLite specific optimizations
                conn.execute(text("VACUUM"))
                logger.info("✓ VACUUM completed")
                
                conn.execute(text("ANALYZE"))
                logger.info("✓ ANALYZE completed")
                
                conn.commit()
                logger.info("✅ Database optimization completed")
                
        except Exception as e:
            logger.error(f"❌ Error optimizing tables: {e}")
    
    def deduplicate_creditors(self):
        """Remove duplicate creditors based on BULSTAT"""
        logger.info("Deduplicating creditors...")
        
        try:
            from database.models import SessionLocal
            session = SessionLocal()
            
            # Find duplicates by BULSTAT
            duplicates = session.query(Creditor.bulstat).filter(
                Creditor.bulstat.isnot(None)
            ).group_by(Creditor.bulstat).having(
                text("COUNT(*) > 1")
            ).all()
            
            removed = 0
            for (bulstat,) in duplicates:
                # Keep the first one, remove others
                creditors = session.query(Creditor).filter_by(bulstat=bulstat).order_by(
                    Creditor.created_at
                ).all()
                
                if len(creditors) > 1:
                    # Merge data from duplicates into first
                    first = creditors[0]
                    for dup in creditors[1:]:
                        # Merge violations, clauses, etc.
                        for violation in dup.violations:
                            violation.creditor_id = first.id
                        for clause in dup.clauses:
                            clause.creditor_id = first.id
                        
                        session.delete(dup)
                        removed += 1
            
            session.commit()
            logger.info(f"✅ Removed {removed} duplicate creditors")
            session.close()
            
        except Exception as e:
            logger.error(f"❌ Error deduplicating: {e}")
    
    def update_statistics(self):
        """Update database statistics for query optimizer"""
        logger.info("Updating database statistics...")
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("ANALYZE"))
                conn.commit()
                logger.info("✅ Statistics updated")
                
        except Exception as e:
            logger.error(f"❌ Error updating statistics: {e}")
    
    def optimize_all(self):
        """Run all optimization steps"""
        logger.info("=" * 70)
        logger.info("DATABASE OPTIMIZATION")
        logger.info("=" * 70)
        
        self.create_indexes()
        self.deduplicate_creditors()
        self.optimize_tables()
        self.update_statistics()
        
        logger.info("=" * 70)
        logger.info("✅ OPTIMIZATION COMPLETE")
        logger.info("=" * 70)


def main():
    """Run optimization"""
    optimizer = DataOptimizer()
    optimizer.optimize_all()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

