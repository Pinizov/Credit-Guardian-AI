from __future__ import annotations
import os
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
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///credit_guardian.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Session = SessionLocal  # compatibility alias for existing imports


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


class User(Base, TimestampMixin):
    """User/consumer who analyzes contracts"""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_user_email", "email"),
        Index("ix_user_egn", "egn"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    egn: Mapped[Optional[str]] = mapped_column(String(10))  # Bulgarian personal ID
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)

    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="user", cascade="all, delete-orphan")
    complaints: Mapped[List["Complaint"]] = relationship("Complaint", back_populates="user", cascade="all, delete-orphan")


class Contract(Base, TimestampMixin):
    """Analyzed credit contract"""
    __tablename__ = "contracts"
    __table_args__ = (
        Index("ix_contract_user", "user_id"),
        Index("ix_contract_creditor", "creditor_id"),
        Index("ix_contract_number", "contract_number"),
        Index("ix_contract_status", "analysis_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creditor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("creditors.id", ondelete="SET NULL"))
    
    contract_number: Mapped[Optional[str]] = mapped_column(String(50))
    creditor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    creditor_eik: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Financial details
    principal: Mapped[float] = mapped_column(Float, default=0.0)
    interest_rate: Mapped[Optional[float]] = mapped_column(Float)
    stated_apr: Mapped[Optional[float]] = mapped_column(Float)
    calculated_apr: Mapped[Optional[float]] = mapped_column(Float)
    
    contract_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    maturity_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    term_months: Mapped[Optional[int]] = mapped_column(Integer)
    
    total_owed: Mapped[Optional[float]] = mapped_column(Float)
    total_paid: Mapped[Optional[float]] = mapped_column(Float)
    
    # Document storage
    document_url: Mapped[Optional[str]] = mapped_column(String(500))
    document_text: Mapped[Optional[str]] = mapped_column(Text)
    document_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Analysis results
    analysis_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending | processing | completed | failed
    analysis_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(50))
    
    user: Mapped[Optional[User]] = relationship("User", back_populates="contracts")
    creditor: Mapped[Optional[Creditor]] = relationship("Creditor")
    fees: Mapped[List["Fee"]] = relationship("Fee", back_populates="contract", cascade="all, delete-orphan")
    violations: Mapped[List["ContractViolation"]] = relationship("ContractViolation", back_populates="contract", cascade="all, delete-orphan")
    complaints: Mapped[List["Complaint"]] = relationship("Complaint", back_populates="contract", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")


class Fee(Base, TimestampMixin):
    """Individual fees in a contract"""
    __tablename__ = "fees"
    __table_args__ = (
        Index("ix_fee_contract", "contract_id"),
        Index("ix_fee_illegal", "is_illegal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    fee_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "бързо разглеждане", "управление", etc.
    fee_amount: Mapped[float] = mapped_column(Float, nullable=False)
    fee_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    is_illegal: Mapped[bool] = mapped_column(Boolean, default=False)
    legal_basis: Mapped[Optional[str]] = mapped_column(String(255))  # "чл. 10а ЗПК"
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    contract: Mapped[Contract] = relationship("Contract", back_populates="fees")


class ContractViolation(Base, TimestampMixin):
    """Legal violations found in a contract"""
    __tablename__ = "contract_violations"
    __table_args__ = (
        Index("ix_contract_violation_contract", "contract_id"),
        Index("ix_contract_violation_severity", "severity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    violation_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "illegal_fee", "apr_exceeded", etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # low | medium | high | critical
    legal_basis: Mapped[Optional[str]] = mapped_column(String(255))  # "чл. 19, ал. 4 ЗПК"
    financial_impact: Mapped[float] = mapped_column(Float, default=0.0)
    
    contract: Mapped[Contract] = relationship("Contract", back_populates="violations")


class Complaint(Base, TimestampMixin):
    """Generated legal complaints"""
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaint_user", "user_id"),
        Index("ix_complaint_contract", "contract_id"),
        Index("ix_complaint_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    contract_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"))
    
    complaint_type: Mapped[str] = mapped_column(String(50), default="КЗП")  # КЗП | съд | БНБ
    complaint_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft | submitted | responded | closed
    
    submitted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    response_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    
    user: Mapped[Optional[User]] = relationship("User", back_populates="complaints")
    contract: Mapped[Optional[Contract]] = relationship("Contract", back_populates="complaints")


class Payment(Base, TimestampMixin):
    """Payment history for contracts"""
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payment_contract", "contract_id"),
        Index("ix_payment_date", "payment_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[Optional[str]] = mapped_column(String(100))  # "месечна вноска", "предсрочно", etc.
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    contract: Mapped[Contract] = relationship("Contract", back_populates="payments")


def init_database() -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
