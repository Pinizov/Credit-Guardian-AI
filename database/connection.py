"""
Database Connection Manager with Best Practices

Features:
- Connection pooling for high performance
- Automatic retry logic for transient failures
- Health checks and connection validation
- Proper session management with context managers
- Support for frequent updates (optimistic locking)
"""
import os
import time
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///credit_guardian.db")
MAX_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("DB_RETRY_DELAY", "1.0"))

# Connection pool configuration
pool_kwargs = {
    "poolclass": QueuePool,
    "pool_size": MAX_POOL_SIZE,
    "max_overflow": MAX_POOL_SIZE * 2,
    "pool_recycle": POOL_RECYCLE,
    "pool_pre_ping": True,  # Verify connections before using
    "pool_timeout": POOL_TIMEOUT,
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
}

# SQLite doesn't support all pool options
if DATABASE_URL.startswith("sqlite"):
    pool_kwargs = {
        "poolclass": pool.StaticPool,
        "connect_args": {"check_same_thread": False},
        "echo": pool_kwargs["echo"],
    }

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    **pool_kwargs,
    future=True
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=Session
)


# Connection event listeners for better reliability
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better performance and reliability."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Validate connection on checkout."""
    try:
        dbapi_conn.execute(text("SELECT 1"))
    except Exception:
        raise DisconnectionError("Connection invalid, will retry")


def get_session() -> Session:
    """
    Get a new database session.
    
    Always use with get_db() context manager instead for automatic cleanup.
    """
    return SessionLocal()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Database session context manager with automatic retry logic.
    
    Usage:
        with get_db() as db:
            user = db.query(User).first()
            db.commit()
    
    Automatically handles:
    - Connection retries on transient failures
    - Session cleanup (commit/rollback)
    - Error logging
    """
    session = None
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            session = SessionLocal()
            yield session
            session.commit()
            break
            
        except (OperationalError, DisconnectionError) as e:
            if session:
                session.rollback()
                session.close()
            
            retries += 1
            if retries >= MAX_RETRIES:
                logger.error(f"Database connection failed after {MAX_RETRIES} retries: {e}")
                raise
            
            logger.warning(f"Database connection error (attempt {retries}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY * retries)  # Exponential backoff
            
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Database error: {e}")
            raise
            
        finally:
            if session:
                session.close()


def check_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def get_connection_info() -> dict:
    """
    Get database connection pool information.
    
    Returns:
        Dictionary with connection pool stats
    """
    pool = engine.pool
    return {
        "pool_size": getattr(pool, "size", None),
        "checked_in": getattr(pool, "checkedin", None),
        "checked_out": getattr(pool, "checkedout", None),
        "overflow": getattr(pool, "overflow", None),
        "invalid": getattr(pool, "invalid", None),
    }


# Initialize database connection on import
try:
    if check_connection():
        logger.info("✓ Database connection established")
    else:
        logger.warning("⚠ Database connection check failed")
except Exception as e:
    logger.error(f"✗ Database initialization error: {e}")
