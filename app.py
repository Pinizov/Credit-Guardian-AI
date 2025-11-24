import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
from analyzers.gpr_calculator import GPRCalculator
from analyzers.contract_analyzer import ContractAnalyzer
from ai_agent.agent_executor import AgentExecutor
from ai_agent.tracing import TRACES
from database.models import Session, Creditor, Violation, CourtCase, UnfairClause
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
