from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "version" in r.json()


def test_versioned_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["storage"] == "ok"
    assert "version" in data
