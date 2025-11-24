from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON,
    create_engine, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column

# Base declarative class
Base = declarative_base()

# Engine & Session factory (default SQLite, override via DATABASE_URL env var)
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///credit_guardian.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Creditor(Base, TimestampMixin):
    __tablename__ = "creditors"
    __table_args__ = (
        UniqueConstraint("bulstat", name="uq_creditor_bulstat"),
        Index("ix_creditor_name", "name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))  # bank | non-bank | unknown
    bulstat: Mapped[Optional[str]] = mapped_column(String(15))
    license_number: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)
    violations_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)

    violations: Mapped[List[Violation]] = relationship("Violation", back_populates="creditor", cascade="all, delete-orphan")
    clauses: Mapped[List[UnfairClause]] = relationship("UnfairClause", back_populates="creditor", cascade="all, delete-orphan")
    court_cases: Mapped[List[CourtCase]] = relationship("CourtCase", back_populates="creditor", cascade="all, delete-orphan")
    products: Mapped[List[CreditProduct]] = relationship("CreditProduct", back_populates="creditor", cascade="all, delete-orphan")

    def recalc_risk_score(self):
        # Simple heuristic: base on violations severity + unfair clauses
        score = 0
        for v in self.violations:
            if v.severity == "critical":
                score += 3
            elif v.severity == "high":
                score += 2
            elif v.severity == "medium":
                score += 1
        score += len([c for c in self.clauses if c.is_confirmed_illegal]) * 1.5
        self.risk_score = round(score, 2)
        self.violations_count = len(self.violations)


class Violation(Base, TimestampMixin):
    __tablename__ = "violations"
    __table_args__ = (
        Index("ix_violation_creditor", "creditor_id"),
        Index("ix_violation_severity", "severity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creditor_id: Mapped[int] = mapped_column(ForeignKey("creditors.id", ondelete="CASCADE"), nullable=False)
    violation_type: Mapped[Optional[str]] = mapped_column(String(120))
    description: Mapped[Optional[str]] = mapped_column(Text)
    law_reference: Mapped[Optional[str]] = mapped_column(String(255))
    decision_number: Mapped[Optional[str]] = mapped_column(String(120))
    authority: Mapped[Optional[str]] = mapped_column(String(60))  # KZP | BNB | Court
    penalty_amount: Mapped[Optional[float]] = mapped_column(Float)
    decision_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    document_text: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="low")  # low | medium | high | critical

    creditor: Mapped[Creditor] = relationship("Creditor", back_populates="violations")


class UnfairClause(Base, TimestampMixin):
    __tablename__ = "unfair_clauses"
    __table_args__ = (
        Index("ix_clause_creditor", "creditor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creditor_id: Mapped[int] = mapped_column(ForeignKey("creditors.id", ondelete="CASCADE"), nullable=False)
    clause_text: Mapped[str] = mapped_column(Text, nullable=False)
    clause_type: Mapped[Optional[str]] = mapped_column(String(120))
    legal_basis: Mapped[Optional[str]] = mapped_column(String(255))
    court_decision: Mapped[Optional[str]] = mapped_column(String(120))
    is_confirmed_illegal: Mapped[bool] = mapped_column(Boolean, default=False)
    examples: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    creditor: Mapped[Creditor] = relationship("Creditor", back_populates="clauses")


class CourtCase(Base, TimestampMixin):
    __tablename__ = "court_cases"
    __table_args__ = (
        UniqueConstraint("case_number", name="uq_case_number"),
        Index("ix_case_creditor", "creditor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_number: Mapped[Optional[str]] = mapped_column(String(120))
    court_name: Mapped[Optional[str]] = mapped_column(String(255))
    creditor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("creditors.id", ondelete="SET NULL"))
    case_type: Mapped[Optional[str]] = mapped_column(String(100))
    plaintiff: Mapped[Optional[str]] = mapped_column(String(255))
    defendant: Mapped[Optional[str]] = mapped_column(String(255))
    subject: Mapped[Optional[str]] = mapped_column(Text)
    decision: Mapped[Optional[str]] = mapped_column(Text)
    decision_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    document_path: Mapped[Optional[str]] = mapped_column(String(500))

    creditor: Mapped[Optional[Creditor]] = relationship("Creditor", back_populates="court_cases")


class CreditProduct(Base, TimestampMixin):
    __tablename__ = "credit_products"
    __table_args__ = (
        Index("ix_product_creditor", "creditor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creditor_id: Mapped[int] = mapped_column(ForeignKey("creditors.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[Optional[str]] = mapped_column(String(255))
    interest_rate: Mapped[Optional[float]] = mapped_column(Float)
    gpr: Mapped[Optional[float]] = mapped_column(Float)
    gpr_calculated: Mapped[Optional[float]] = mapped_column(Float)
    gpr_mismatch: Mapped[bool] = mapped_column(Boolean, default=False)
    fees: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    illegal_fees: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    min_amount: Mapped[Optional[float]] = mapped_column(Float)
    max_amount: Mapped[Optional[float]] = mapped_column(Float)
    term_months: Mapped[Optional[int]] = mapped_column(Integer)
    analyzed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)

    creditor: Mapped[Creditor] = relationship("Creditor", back_populates="products")


def init_database() -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
