from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    assert client.get("/healthz").status_code == 200

def test_readyz():
    assert client.get("/readyz").status_code == 200

def test_metrics_are_exposed():
    body = client.get("/metrics").text
    assert "pacer_http_requests_total" in body

def test_pace_endpoint():
    r = client.post("/api/pace", json={"distance_km": 10, "duration": "50:00"})
    assert r.status_code == 200
    assert r.json()["pace"] == "5:00 /km"

def test_bad_input_returns_400():
    r = client.post("/api/pace", json={"distance_km": -1, "duration": "50:00"})
    assert r.status_code == 400
