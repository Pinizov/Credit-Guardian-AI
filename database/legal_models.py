"""
Additional database models for Bulgarian legal knowledge base
Tables for laws, regulations, and training data
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime, Boolean, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import Base, TimestampMixin


class LegalDocument(Base, TimestampMixin):
    """Bulgarian laws and regulations scraped from lex.bg"""
    __tablename__ = "legal_documents"
    __table_args__ = (
        Index("ix_legal_doc_title", "title"),
        Index("ix_legal_doc_type", "document_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # law | regulation | decree
    document_number: Mapped[Optional[str]] = mapped_column(String(100))
    promulgation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    full_text: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    articles: Mapped[List[LegalArticle]] = relationship("LegalArticle", back_populates="document", cascade="all, delete-orphan")


class LegalArticle(Base, TimestampMixin):
    """Individual articles from legal documents"""
    __tablename__ = "legal_articles"
    __table_args__ = (
        Index("ix_article_doc_id", "document_id"),
        Index("ix_article_number", "article_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False)
    article_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chapter: Mapped[Optional[str]] = mapped_column(String(200))  # raw heading text
    section: Mapped[Optional[str]] = mapped_column(String(200))  # raw heading text
    chapter_number: Mapped[Optional[str]] = mapped_column(String(50))  # normalized numeral (e.g. "I", "1")
    chapter_title: Mapped[Optional[str]] = mapped_column(String(300))  # heading title sans number
    section_number: Mapped[Optional[str]] = mapped_column(String(50))
    section_title: Mapped[Optional[str]] = mapped_column(String(300))

    # Relationship
    document: Mapped[LegalDocument] = relationship("LegalDocument", back_populates="articles")


class ConsumerCase(Base, TimestampMixin):
    """Consumer protection cases and precedents"""
    __tablename__ = "consumer_cases"
    __table_args__ = (
        Index("ix_case_date", "case_date"),
        Index("ix_case_type", "case_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_number: Mapped[Optional[str]] = mapped_column(String(100))
    case_type: Mapped[str] = mapped_column(String(100), nullable=False)  # violation | complaint | lawsuit
    authority: Mapped[str] = mapped_column(String(100), nullable=False)  # APIS | KZP | BNB | Court
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    company_bulstat: Mapped[Optional[str]] = mapped_column(String(15))
    violation_description: Mapped[Optional[str]] = mapped_column(Text)
    decision: Mapped[Optional[str]] = mapped_column(Text)
    penalty_amount: Mapped[Optional[float]] = mapped_column(Integer)
    case_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    law_references: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of article references


class TrainingExample(Base, TimestampMixin):
    """Training examples for AI agent evaluation"""
    __tablename__ = "training_examples"
    __table_args__ = (
        Index("ix_training_category", "category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # gpr_calculation | clause_detection | violation_check
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    example_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON with additional context
    source: Mapped[str] = mapped_column(String(50), default='manual')  # manual | lex.bg | apis.bg | synthetic
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)


class LegalArticleTag(Base, TimestampMixin):
    """Tags assigned to legal articles for thematic classification."""
    __tablename__ = "legal_article_tags"
    __table_args__ = (
        Index("ix_tag_article_id", "article_id"),
        Index("ix_tag_value", "tag"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("legal_articles.id", ondelete="CASCADE"), nullable=False)
    tag: Mapped[str] = mapped_column(String(120), nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Integer)  # TF-IDF or relevance score

    # Relationship back to article
    article: Mapped[LegalArticle] = relationship("LegalArticle", backref="tags")
