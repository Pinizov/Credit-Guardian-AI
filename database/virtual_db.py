"""
Virtual Database Interface
Виртуален интерфейс за оптимизиран достъп до базата данни
Обединява данни от различни източници в единен интерфейс
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from database.models import (
    SessionLocal, Creditor, Violation, UnfairClause, 
    CourtCase, CreditProduct
)
from database.legal_models import LegalDocument as LegalDoc, LegalArticle, ConsumerCase

logger = logging.getLogger(__name__)


class VirtualDatabase:
    """Virtual database interface that unifies access to all data sources"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def search_creditors(self, 
                        query: Optional[str] = None,
                        creditor_type: Optional[str] = None,
                        min_risk_score: Optional[float] = None,
                        blacklisted_only: bool = False,
                        limit: int = 50,
                        offset: int = 0) -> Dict[str, Any]:
        """
        Search creditors with filters
        
        Args:
            query: Search by name or BULSTAT
            creditor_type: Filter by type (bank, non-bank, unknown)
            min_risk_score: Minimum risk score
            blacklisted_only: Show only blacklisted
            limit: Results limit
            offset: Pagination offset
            
        Returns:
            Dictionary with results and metadata
        """
        try:
            q = self.session.query(Creditor)
            
            # Apply filters
            if query:
                q = q.filter(
                    (Creditor.name.ilike(f"%{query}%")) |
                    (Creditor.bulstat.ilike(f"%{query}%"))
                )
            
            if creditor_type:
                q = q.filter(Creditor.type == creditor_type)
            
            if min_risk_score is not None:
                q = q.filter(Creditor.risk_score >= min_risk_score)
            
            if blacklisted_only:
                q = q.filter(Creditor.is_blacklisted == True)
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            creditors = q.order_by(Creditor.risk_score.desc()).offset(offset).limit(limit).all()
            
            # Serialize results
            results = []
            for creditor in creditors:
                results.append({
                    'id': creditor.id,
                    'name': creditor.name,
                    'type': creditor.type,
                    'bulstat': creditor.bulstat,
                    'license_number': creditor.license_number,
                    'address': creditor.address,
                    'violations_count': creditor.violations_count,
                    'risk_score': creditor.risk_score,
                    'is_blacklisted': creditor.is_blacklisted,
                    'created_at': creditor.created_at.isoformat() if creditor.created_at else None,
                })
            
            return {
                'total': total,
                'count': len(results),
                'offset': offset,
                'limit': limit,
                'creditors': results
            }
            
        except Exception as e:
            logger.error(f"Error searching creditors: {e}")
            return {
                'total': 0,
                'count': 0,
                'offset': offset,
                'limit': limit,
                'creditors': []
            }
    
    def get_creditor_details(self, creditor_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a creditor
        
        Args:
            creditor_id: Creditor ID
            
        Returns:
            Detailed creditor information
        """
        try:
            creditor = self.session.query(Creditor).filter_by(id=creditor_id).first()
            
            if not creditor:
                return None
            
            # Get related data
            violations = self.session.query(Violation).filter_by(creditor_id=creditor_id).all()
            clauses = self.session.query(UnfairClause).filter_by(creditor_id=creditor_id).all()
            cases = self.session.query(CourtCase).filter_by(creditor_id=creditor_id).all()
            products = self.session.query(CreditProduct).filter_by(creditor_id=creditor_id).all()
            
            return {
                'id': creditor.id,
                'name': creditor.name,
                'type': creditor.type,
                'bulstat': creditor.bulstat,
                'license_number': creditor.license_number,
                'address': creditor.address,
                'violations_count': creditor.violations_count,
                'risk_score': creditor.risk_score,
                'is_blacklisted': creditor.is_blacklisted,
                'violations': [
                    {
                        'id': v.id,
                        'violation_type': v.violation_type,
                        'description': v.description,
                        'law_reference': v.law_reference,
                        'authority': v.authority,
                        'penalty_amount': v.penalty_amount,
                        'severity': v.severity,
                        'decision_date': v.decision_date.isoformat() if v.decision_date else None,
                    }
                    for v in violations
                ],
                'unfair_clauses': [
                    {
                        'id': c.id,
                        'clause_text': c.clause_text[:200] + '...' if len(c.clause_text) > 200 else c.clause_text,
                        'clause_type': c.clause_type,
                        'legal_basis': c.legal_basis,
                        'is_confirmed_illegal': c.is_confirmed_illegal,
                    }
                    for c in clauses
                ],
                'court_cases': [
                    {
                        'id': c.id,
                        'case_number': c.case_number,
                        'court_name': c.court_name,
                        'case_type': c.case_type,
                        'decision_date': c.decision_date.isoformat() if c.decision_date else None,
                        'is_final': c.is_final,
                    }
                    for c in cases
                ],
                'credit_products': [
                    {
                        'id': p.id,
                        'product_name': p.product_name,
                        'interest_rate': p.interest_rate,
                        'gpr': p.gpr,
                        'gpr_calculated': p.gpr_calculated,
                        'gpr_mismatch': p.gpr_mismatch,
                    }
                    for p in products
                ],
                'created_at': creditor.created_at.isoformat() if creditor.created_at else None,
                'updated_at': creditor.updated_at.isoformat() if creditor.updated_at else None,
            }
            
        except Exception as e:
            logger.error(f"Error getting creditor details: {e}")
            return None
    
    def search_legal_documents(self,
                               query: Optional[str] = None,
                               document_type: Optional[str] = None,
                               limit: int = 50,
                               offset: int = 0) -> Dict[str, Any]:
        """
        Search legal documents
        
        Args:
            query: Search in title or content
            document_type: Filter by type (law, regulation, codex, etc.)
            limit: Results limit
            offset: Pagination offset
            
        Returns:
            Dictionary with results
        """
        try:
            q = self.session.query(LegalDoc)
            
            if query:
                q = q.filter(
                    (LegalDoc.title.ilike(f"%{query}%")) |
                    (LegalDoc.full_text.ilike(f"%{query}%"))
                )
            
            if document_type:
                q = q.filter(LegalDoc.document_type == document_type)
            
            q = q.filter(LegalDoc.is_active == True)
            
            total = q.count()
            documents = q.order_by(LegalDoc.created_at.desc()).offset(offset).limit(limit).all()
            
            results = []
            for doc in documents:
                results.append({
                    'id': doc.id,
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'document_number': doc.document_number,
                    'promulgation_date': doc.promulgation_date.isoformat() if doc.promulgation_date else None,
                    'effective_date': doc.effective_date.isoformat() if doc.effective_date else None,
                    'source_url': doc.source_url,
                    'content_preview': doc.full_text[:500] + '...' if doc.full_text and len(doc.full_text) > 500 else (doc.full_text or ''),
                    'created_at': doc.created_at.isoformat() if doc.created_at else None,
                })
            
            return {
                'total': total,
                'count': len(results),
                'offset': offset,
                'limit': limit,
                'documents': results
            }
            
        except Exception as e:
            logger.error(f"Error searching legal documents: {e}")
            return {
                'total': 0,
                'count': 0,
                'offset': offset,
                'limit': limit,
                'documents': []
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            return {
                'creditors': {
                    'total': self.session.query(Creditor).count(),
                    'banks': self.session.query(Creditor).filter_by(type='bank').count(),
                    'non_bank': self.session.query(Creditor).filter_by(type='non-bank').count(),
                    'blacklisted': self.session.query(Creditor).filter_by(is_blacklisted=True).count(),
                },
                'violations': {
                    'total': self.session.query(Violation).count(),
                    'critical': self.session.query(Violation).filter_by(severity='critical').count(),
                    'high': self.session.query(Violation).filter_by(severity='high').count(),
                },
                'legal_documents': {
                    'total': self.session.query(LegalDoc).filter_by(is_active=True).count(),
                    'laws': self.session.query(LegalDoc).filter_by(document_type='law', is_active=True).count(),
                    'regulations': self.session.query(LegalDoc).filter_by(document_type='regulation', is_active=True).count(),
                    'registers': self.session.query(LegalDoc).filter_by(document_type='registry', is_active=True).count(),
                },
                'unfair_clauses': self.session.query(UnfairClause).count(),
                'court_cases': self.session.query(CourtCase).count(),
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database session"""
        self.session.close()


def main():
    """Test the virtual database interface"""
    import json
    db = VirtualDatabase()
    
    # Get statistics
    stats = db.get_statistics()
    print("Database Statistics:")
    print(json.dumps(stats, indent=2, default=str))
    
    # Search creditors
    results = db.search_creditors(limit=10)
    print(f"\nFound {results['total']} creditors")
    print(f"Showing {results['count']} results")
    
    db.close()


if __name__ == "__main__":
    main()

