import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from datetime import datetime
from analyzers.gpr_calculator import GPRCalculator
from analyzers.contract_analyzer import ContractAnalyzer
from ai_agent.agent_executor import AgentExecutor
from ai_agent.tracing import TRACES
from database.models import (
    Session, Creditor, Violation, CourtCase, UnfairClause,
    User, Contract, Fee, ContractViolation, Complaint, Payment
)
from database.legal_models import LegalDocument, LegalArticle, LegalArticleTag
from database.embedding_models import ArticleEmbedding
from sqlalchemy import text
from utils.s3_storage import init_s3, upload_contract_to_s3

app = FastAPI(title="Credit Guardian API", version="0.1")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 (optional)
s3_enabled = init_s3()
if s3_enabled:
    print("✓ S3 storage enabled")
else:
    print("⚠ S3 storage disabled (missing AWS credentials)")


class GPRRequest(BaseModel):
    amount: float
    total_repayment: float
    term_months: int
    fees: list = []


class GPRVerifyRequest(BaseModel):
    declared_gpr: float
    amount: float
    total_repayment: float
    term_months: int
    fees: list = []

 
gpr_calc = GPRCalculator()
contract_analyzer = ContractAnalyzer()
ai_executor = AgentExecutor()
AI_COMPLAINTS = []  # simple in-memory store [{'id':int,'complaint':str,'analysis':dict}]


@app.post("/gpr/calculate")
def calculate_gpr(req: GPRRequest):
    result = gpr_calc.calculate_gpr(
        loan_amount=req.amount,
        total_repayment=req.total_repayment,
        fees=req.fees,
        term_months=req.term_months
    )
    return result


@app.post("/gpr/verify")
def verify_gpr(req: GPRVerifyRequest):
    result = gpr_calc.verify_gpr_declaration(
        req.declared_gpr,
        {
            'amount': req.amount,
            'total_repayment': req.total_repayment,
            'fees': req.fees,
            'term_months': req.term_months
        }
    )
    return result


@app.post("/contract/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Поддържат се .pdf .docx .txt")
    
    # Optional: upload to S3 first
    s3_url = None
    if s3_enabled:
        try:
            s3_url = upload_contract_to_s3(file, "analysis")
            file.file.seek(0)  # Reset after S3 upload
        except Exception as e:
            print(f"S3 upload warning: {e}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        analysis = contract_analyzer.analyze_file(tmp_path)
        if s3_url:
            analysis['s3_url'] = s3_url
        return analysis
    finally:
        os.remove(tmp_path)


@app.post("/ai/analyze")
async def ai_analyze_contract(file: UploadFile = File(...), name: str = "Потребител", address: str = ""):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Само PDF се поддържа за AI анализа")
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = ai_executor.process(tmp_path, {"name": name, "address": address})
        cid = len(AI_COMPLAINTS) + 1
        AI_COMPLAINTS.append({"id": cid, "complaint": result["complaint"], "analysis": result["analysis"]})
        result["complaint_id"] = cid
        return result
    finally:
        os.remove(tmp_path)

 
@app.get("/ai/traces")
def ai_traces():
    return {"count": len(TRACES), "traces": TRACES}

 
@app.get("/ai/complaint/pdf/{cid}")
def ai_complaint_pdf(cid: int):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO
    item = next((c for c in AI_COMPLAINTS if c["id"] == cid), None)
    if not item:
        raise HTTPException(status_code=404, detail="Complaint not found")
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text_obj = c.beginText(40, 800)
    text_obj.setFont("Helvetica", 10)
    for line in item["complaint"].splitlines():
        if text_obj.getY() < 40:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(40, 800)
            text_obj.setFont("Helvetica", 10)
        text_obj.textLine(line[:120])
    c.drawText(text_obj)
    c.showPage()
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=complaint_{cid}.pdf"})


@app.get("/creditor/{name}")
def creditor_info(name: str):
    s = Session()
    c = s.query(Creditor).filter(Creditor.name.ilike(f"%{name}%")).first()
    if not c:
        s.close()
        raise HTTPException(status_code=404, detail="Кредитор не намерен")
    violations = s.query(Violation).filter_by(creditor_id=c.id).all()
    clauses = s.query(UnfairClause).filter_by(creditor_id=c.id).all()
    cases = s.query(CourtCase).filter_by(creditor_id=c.id).all()
    data = {
        'name': c.name,
        'type': c.type,
        'violations_count': c.violations_count,
        'risk_score': c.risk_score,
        'blacklisted': c.is_blacklisted,
        'violations': [
            {
                'type': v.violation_type,
                'date': v.decision_date,
                'authority': v.authority,
                'penalty': v.penalty_amount,
                'severity': v.severity
            } for v in violations
        ],
        'unfair_clauses': [
            {
                'type': cl.clause_type,
                'legal_basis': cl.legal_basis,
                'confirmed': cl.is_confirmed_illegal
            } for cl in clauses
        ],
        'court_cases': [
            {
                'case_number': cs.case_number,
                'court': cs.court_name,
                'date': cs.decision_date,
                'final': cs.is_final
            } for cs in cases[:30]
        ]
    }
    s.close()
    return data




@app.post("/api/analyze-contract")
async def analyze_contract_full(
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    egn: str = Form("")
):
    """
    Complete contract analysis workflow:
    1. Create/update user
    2. Extract PDF text
    3. AI analysis with legal violation checks
    4. Save contract, fees, violations to database
    5. Generate complaint
    6. Return full results
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Само PDF файлове се поддържат")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Optional S3 upload
        s3_url = None
        if s3_enabled:
            try:
                file.file.seek(0)
                s3_url = upload_contract_to_s3(file, "contracts")
            except Exception as e:
                print(f"S3 upload warning: {e}")
        
        # Process with AI agent
        user_info = {"name": name, "email": email, "phone": phone, "address": address, "egn": egn}
        result = ai_executor.process(tmp_path, user_info)
        
        if result.get("status") == "error":
            return result
        
        analysis = result["analysis"]
        complaint_text = result["complaint"]
        
        # Database operations
        session = Session()
        
        try:
            # 1. Create or get user
            user = None
            if email:
                user = session.query(User).filter_by(email=email).first()
            
            if not user:
                user = User(
                    name=name,
                    email=email or None,
                    phone=phone or None,
                    address=address or None,
                    egn=egn or None
                )
                session.add(user)
                session.flush()  # Get user ID
            
            # 2. Get or create creditor
            creditor = None
            creditor_name = analysis.get("creditor", "Неизвестен")
            creditor_eik = analysis.get("creditor_eik")
            
            if creditor_eik:
                creditor = session.query(Creditor).filter_by(bulstat=creditor_eik).first()
            
            if not creditor and creditor_name != "Неизвестен":
                creditor = session.query(Creditor).filter_by(name=creditor_name).first()
            
            # 3. Create contract record
            contract = Contract(
                user_id=user.id,
                creditor_id=creditor.id if creditor else None,
                contract_number=analysis.get("contract_number"),
                creditor_name=creditor_name,
                creditor_eik=creditor_eik,
                principal=analysis.get("principal", 0),
                interest_rate=analysis.get("interest_rate"),
                stated_apr=analysis.get("stated_apr"),
                calculated_apr=analysis.get("calculated_real_apr"),
                term_months=analysis.get("term_months"),
                total_owed=analysis.get("total_actual_cost"),
                document_url=s3_url,
                document_text=result.get("text_excerpt", ""),
                document_path=file.filename,
                analysis_status="completed",
                analysis_result=analysis,
                ai_model_used="gpt-4"
            )
            
            # Parse contract date if available
            if analysis.get("contract_date"):
                try:
                    contract.contract_date = datetime.fromisoformat(analysis["contract_date"])
                except:
                    pass
            
            session.add(contract)
            session.flush()  # Get contract ID
            
            # 4. Save fees
            for fee_data in analysis.get("fees", []):
                fee = Fee(
                    contract_id=contract.id,
                    fee_type=fee_data.get("type", ""),
                    fee_amount=fee_data.get("amount", 0),
                    is_illegal=fee_data.get("is_illegal", False),
                    legal_basis=fee_data.get("basis", ""),
                    paid=False
                )
                session.add(fee)
            
            # 5. Save violations
            for violation_data in analysis.get("violations", []):
                violation = ContractViolation(
                    contract_id=contract.id,
                    violation_type=violation_data.get("type", ""),
                    description=violation_data.get("description", ""),
                    severity=violation_data.get("severity", "medium"),
                    legal_basis=violation_data.get("legal_basis", ""),
                    financial_impact=violation_data.get("financial_impact", 0)
                )
                session.add(violation)
            
            # 6. Create complaint (draft)
            complaint = Complaint(
                user_id=user.id,
                contract_id=contract.id,
                complaint_type="КЗП",
                complaint_text=complaint_text,
                status="draft"
            )
            session.add(complaint)
            session.flush()
            
            session.commit()
            
            return {
                "status": "success",
                "contract_id": contract.id,
                "complaint_id": complaint.id,
                "user_id": user.id,
                "analysis": analysis,
                "violations": analysis.get("violations", []),
                "financial_summary": result.get("financial_summary", {}),
                "s3_url": s3_url,
                "message": "Договорът е анализиран успешно"
            }
        
        except Exception as db_error:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        finally:
            session.close()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/api/users/{user_id}/contracts")
def get_user_contracts(user_id: int):
    """Get all contracts for a specific user"""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        contracts = session.query(Contract).filter_by(user_id=user_id).all()
        
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            },
            "contracts": [
                {
                    "id": c.id,
                    "contract_number": c.contract_number,
                    "creditor_name": c.creditor_name,
                    "principal": c.principal,
                    "stated_apr": c.stated_apr,
                    "calculated_apr": c.calculated_apr,
                    "analysis_status": c.analysis_status,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "violations_count": len(c.violations)
                }
                for c in contracts
            ]
        }
    finally:
        session.close()


@app.get("/api/contracts/{contract_id}")
def get_contract_details(contract_id: int):
    """Get detailed information about a specific contract"""
    session = Session()
    try:
        contract = session.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "contract": {
                "id": contract.id,
                "contract_number": contract.contract_number,
                "creditor_name": contract.creditor_name,
                "creditor_eik": contract.creditor_eik,
                "principal": contract.principal,
                "stated_apr": contract.stated_apr,
                "calculated_apr": contract.calculated_apr,
                "term_months": contract.term_months,
                "contract_date": contract.contract_date.isoformat() if contract.contract_date else None,
                "analysis_status": contract.analysis_status,
                "created_at": contract.created_at.isoformat() if contract.created_at else None
            },
            "analysis": contract.analysis_result,
            "fees": [
                {
                    "type": f.fee_type,
                    "amount": f.fee_amount,
                    "is_illegal": f.is_illegal,
                    "legal_basis": f.legal_basis
                }
                for f in contract.fees
            ],
            "violations": [
                {
                    "type": v.violation_type,
                    "description": v.description,
                    "severity": v.severity,
                    "legal_basis": v.legal_basis,
                    "financial_impact": v.financial_impact
                }
                for v in contract.violations
            ]
        }
    finally:
        session.close()


@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: int):
    """Get complaint details"""
    session = Session()
    try:
        complaint = session.query(Complaint).filter_by(id=complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        return {
            "id": complaint.id,
            "complaint_type": complaint.complaint_type,
            "complaint_text": complaint.complaint_text,
            "status": complaint.status,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "contract_id": complaint.contract_id,
            "user_id": complaint.user_id
        }
    finally:
        session.close()


@app.get("/api/complaints/{complaint_id}/export")
def export_complaint_pdf(complaint_id: int):
    """Export complaint as PDF"""
    session = Session()
    try:
        complaint = session.query(Complaint).filter_by(id=complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Generate PDF using ReportLab
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Split text into paragraphs and add to document
        for line in complaint.complaint_text.split('\n'):
            if line.strip():
                # Use normal style for better Bulgarian text support
                para = Paragraph(line, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="complaint_{complaint_id}.pdf"'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")
    finally:
        session.close()


@app.get("/api/legal/search")
def search_legal_articles(q: str, limit: int = 10):
    """
    Search Bulgarian legal articles by keyword
    Uses full-text search on article content
    """
    session = Session()
    try:
        # Search in article content and document titles
        articles = session.query(LegalArticle, LegalDocument)\
            .join(LegalDocument, LegalArticle.document_id == LegalDocument.id)\
            .filter(
                (LegalArticle.content.ilike(f"%{q}%")) |
                (LegalDocument.title.ilike(f"%{q}%"))
            )\
            .limit(limit)\
            .all()
        
        return {
            "query": q,
            "count": len(articles),
            "results": [
                {
                    "article_id": art.id,
                    "article_number": art.article_number,
                    "content": art.content[:500] + "..." if len(art.content) > 500 else art.content,
                    "document": doc.title,
                    "document_type": doc.document_type
                }
                for art, doc in articles
            ]
        }
    finally:
        session.close()


@app.get("/api/legal/article/{article_id}")
def get_legal_article(article_id: int):
    """Get detailed information about a specific legal article"""
    session = Session()
    try:
        article = session.query(LegalArticle).filter_by(id=article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        document = session.query(LegalDocument).filter_by(id=article.document_id).first()
        
        # Get tags
        tags = session.query(LegalArticleTag).filter_by(article_id=article_id).all()
        
        return {
            "article": {
                "id": article.id,
                "article_number": article.article_number,
                "content": article.content,
                "chapter": article.chapter,
                "section": article.section
            },
            "document": {
                "id": document.id,
                "title": document.title,
                "document_type": document.document_type,
                "document_number": document.document_number,
                "source_url": document.source_url
            },
            "tags": [
                {
                    "keyword": tag.keyword,
                    "tfidf_score": tag.tfidf_score
                }
                for tag in tags
            ]
        }
    finally:
        session.close()


@app.get("/api/legal/similar/{article_id}")
def find_similar_articles(article_id: int, top_k: int = 5):
    """
    Find similar legal articles using semantic embeddings
    Requires embeddings to be generated
    """
    session = Session()
    try:
        # Get the source article embedding
        source_embedding = session.query(ArticleEmbedding).filter_by(article_id=article_id).first()
        if not source_embedding:
            raise HTTPException(status_code=404, detail="Article embeddings not found")
        
        # Get source vector
        import numpy as np
        source_vector = np.frombuffer(source_embedding.embedding_vector, dtype=np.float32)
        
        # Calculate cosine similarity with all other articles
        all_embeddings = session.query(ArticleEmbedding).filter(ArticleEmbedding.article_id != article_id).all()
        
        similarities = []
        for emb in all_embeddings:
            target_vector = np.frombuffer(emb.embedding_vector, dtype=np.float32)
            
            # Cosine similarity
            similarity = np.dot(source_vector, target_vector) / (
                np.linalg.norm(source_vector) * np.linalg.norm(target_vector)
            )
            
            similarities.append((emb.article_id, float(similarity)))
        
        # Sort by similarity and take top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_articles = similarities[:top_k]
        
        # Fetch article details
        results = []
        for art_id, sim_score in top_articles:
            article = session.query(LegalArticle).filter_by(id=art_id).first()
            document = session.query(LegalDocument).filter_by(id=article.document_id).first()
            
            results.append({
                "article_id": article.id,
                "article_number": article.article_number,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "document": document.title,
                "similarity_score": round(sim_score, 4)
            })
        
        return {
            "source_article_id": article_id,
            "similar_articles": results
        }
    
    except ImportError:
        raise HTTPException(status_code=501, detail="NumPy required for similarity search")
    finally:
        session.close()


@app.get("/api/legal/documents")
def list_legal_documents(limit: int = 50):
    """List all available legal documents"""
    session = Session()
    try:
        documents = session.query(LegalDocument).limit(limit).all()
        
        return {
            "count": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "document_number": doc.document_number,
                    "article_count": len(doc.articles) if hasattr(doc, 'articles') else 0
                }
                for doc in documents
            ]
        }
    finally:
        session.close()


@app.get("/api/legal/stats")
def legal_database_stats():
    """Get statistics about the legal database"""
    session = Session()
    try:
        documents = session.query(LegalDocument).count()
        articles = session.query(LegalArticle).count()
        tags = session.query(LegalArticleTag).count()
        embeddings = session.query(ArticleEmbedding).count()
        
        # Get document type breakdown
        from sqlalchemy import func
        doc_types = session.query(
            LegalDocument.document_type,
            func.count(LegalDocument.id)
        ).group_by(LegalDocument.document_type).all()
        
        return {
            "total_documents": documents,
            "total_articles": articles,
            "total_tags": tags,
            "total_embeddings": embeddings,
            "document_types": {doc_type: count for doc_type, count in doc_types}
        }
    finally:
        session.close()


@app.get("/stats")
def stats():
    s = Session()
    creditors = s.query(Creditor).count()
    violations = s.query(Violation).count()
    cases = s.query(CourtCase).count()
    clauses = s.query(UnfairClause).count()
    critical = s.query(Violation).filter_by(severity='critical').count()
    s.close()
    return {
        'creditors': creditors,
        'violations': violations,
        'critical_violations': critical,
        'court_cases': cases,
        'unfair_clauses': clauses
    }


@app.get("/")
def root():
    return JSONResponse({"service": "Credit Guardian API", "endpoints": ["/gpr/calculate", "/gpr/verify", "/contract/analyze", "/creditor/{name}", "/stats"]})


@app.get("/health")
def health_check():
    """Health check endpoint for load balancers/k8s"""
    return {"status": "healthy", "service": "credit-guardian-api"}


@app.get("/readiness")
def readiness_check():
    """Readiness check - verify DB connection"""
    try:
        s = Session()
        s.execute(text("SELECT 1"))
        s.close()
        return {"status": "ready", "database": "connected", "s3": s3_enabled}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
