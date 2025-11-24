from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ai_analyze_stub_without_key(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample minimal content for testing")
    with open(pdf_path, "rb") as f:
        resp = client.post("/ai/analyze", files={"file": ("sample.pdf", f.read(), "application/pdf")})
    assert resp.status_code == 200
    data = resp.json()
    assert "analysis" in data
    assert data["analysis"].get("summary", "").startswith("AI анализ") or "analysis" in data
