import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_readiness_endpoint():
    response = client.get("/readiness")
    # May be 200 or 503 depending on DB availability
    assert response.status_code in [200, 503]

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "creditors" in data
    assert "violations" in data
    assert isinstance(data["creditors"], int)

def test_gpr_calculate():
    payload = {
        "amount": 5000,
        "total_repayment": 6500,
        "term_months": 24,
        "fees": []
    }
    response = client.post("/api/gpr/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "gpr_exact" in data
    assert "gpr_simple" in data
    assert data["gpr_exact"] > 0

def test_gpr_verify():
    payload = {
        "declared_gpr": 25.0,
        "amount": 5000,
        "total_repayment": 6500,
        "term_months": 24,
        "fees": []
    }
    response = client.post("/api/gpr/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "calculated_gpr" in data

def test_creditor_not_found():
    response = client.get("/api/creditor/NonExistentBank123456")
    assert response.status_code == 404

def test_contract_analyze_invalid_format():
    files = {"file": ("test.exe", b"fake content", "application/octet-stream")}
    response = client.post("/api/contract/analyze", files=files)
    assert response.status_code == 400
    assert "Поддържат се" in response.json()["detail"]
