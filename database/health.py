"""
Database Health Monitoring and Maintenance

Features:
- Automatic health checks
- Connection pool monitoring
- Database statistics
- Maintenance operations
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError

from .connection import engine, get_db, check_connection
from .models import (
    Creditor, Violation, Contract, User, Complaint
)
from .legal_models import LegalDocument, LegalArticle

logger = logging.getLogger(__name__)


class DatabaseHealthMonitor:
    """Monitor database health and performance."""
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """
        Get comprehensive database health status.
        
        Returns:
            Dictionary with health metrics
        """
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "connection": check_connection(),
            "pool": {},
            "statistics": {},
            "errors": []
        }
        
        try:
            # Connection pool info
            pool = engine.pool
            status["pool"] = {
                "size": getattr(pool, "size", 0),
                "checked_in": getattr(pool, "checkedin", 0),
                "checked_out": getattr(pool, "checkedout", 0),
                "overflow": getattr(pool, "overflow", 0),
            }
            
            # Database statistics
            with get_db() as db:
                status["statistics"] = {
                    "creditors": db.query(func.count(Creditor.id)).scalar() or 0,
                    "violations": db.query(func.count(Violation.id)).scalar() or 0,
                    "contracts": db.query(func.count(Contract.id)).scalar() or 0,
                    "users": db.query(func.count(User.id)).scalar() or 0,
                    "complaints": db.query(func.count(Complaint.id)).scalar() or 0,
                    "legal_documents": db.query(func.count(LegalDocument.id)).scalar() or 0,
                    "legal_articles": db.query(func.count(LegalArticle.id)).scalar() or 0,
                }
                
                # Check for recent activity
                recent_contracts = db.query(func.count(Contract.id)).filter(
                    Contract.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).scalar() or 0
                
                status["recent_activity"] = {
                    "contracts_last_24h": recent_contracts
                }
        
        except Exception as e:
            status["errors"].append(str(e))
            logger.error(f"Health check error: {e}")
        
        return status
    
    @staticmethod
    def optimize_database():
        """
        Run database optimization operations.
        
        For SQLite: VACUUM and ANALYZE
        For PostgreSQL: VACUUM ANALYZE
        """
        try:
            with engine.connect() as conn:
                if engine.url.drivername == "sqlite":
                    logger.info("Running SQLite VACUUM...")
                    conn.execute(text("VACUUM"))
                    conn.execute(text("ANALYZE"))
                    conn.commit()
                    logger.info("✓ SQLite optimization complete")
                    
                elif engine.url.drivername.startswith("postgresql"):
                    logger.info("Running PostgreSQL VACUUM ANALYZE...")
                    conn.execute(text("VACUUM ANALYZE"))
                    conn.commit()
                    logger.info("✓ PostgreSQL optimization complete")
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            raise
    
    @staticmethod
    def get_table_sizes() -> Dict[str, int]:
        """
        Get approximate table sizes.
        
        Returns:
            Dictionary mapping table names to row counts
        """
        sizes = {}
        try:
            with get_db() as db:
                tables = [
                    ("creditors", Creditor),
                    ("violations", Violation),
                    ("contracts", Contract),
                    ("users", User),
                    ("complaints", Complaint),
                ]
                
                for table_name, model in tables:
                    try:
                        count = db.query(func.count(model.id)).scalar() or 0
                        sizes[table_name] = count
                    except Exception as e:
                        logger.warning(f"Could not get size for {table_name}: {e}")
                        sizes[table_name] = -1
        
        except Exception as e:
            logger.error(f"Error getting table sizes: {e}")
        
        return sizes


# Global health monitor instance
health_monitor = DatabaseHealthMonitor()

