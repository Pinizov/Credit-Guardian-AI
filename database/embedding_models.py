"""
SQLAlchemy models for article embeddings.

Note: These models define schema but actual DB operations use raw sqlite3
due to greenlet build issues on Windows.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ArticleEmbedding(Base):
    """
    Stores vector embeddings for legal articles.
    
    Vector format: JSON array of floats (1536 dims for text-embedding-3-small)
    Enables semantic search via cosine similarity.
    """
    __tablename__ = 'article_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('legal_articles.id'), nullable=False, unique=True)
    document_id = Column(Integer, nullable=False)  # Denormalized for faster filtering
    
    # Embedding metadata
    model_name = Column(String(100), nullable=False)  # e.g., "text-embedding-3-small"
    embedding_dim = Column(Integer, nullable=False)  # e.g., 1536
    
    # Vector storage (JSON array of floats)
    vector = Column(Text, nullable=False)  # JSON serialized: "[0.123, -0.456, ...]"
    
    # Pre-computed L2 norm for cosine similarity optimization
    norm = Column(Float, nullable=False)
    
    # Content hash for change detection
    content_hash = Column(String(64), nullable=False)  # SHA256 of article content
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for fast retrieval
    __table_args__ = (
        Index('idx_article_embeddings_article_id', 'article_id'),
        Index('idx_article_embeddings_document_id', 'document_id'),
        Index('idx_article_embeddings_model', 'model_name'),
        Index('idx_article_embeddings_content_hash', 'content_hash'),
    )
