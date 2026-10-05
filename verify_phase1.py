import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("GET /health:", c.get("/health").json())
print("GET /api/v1/health:", c.get("/api/v1/health").json())
print("GET /openapi.json paths:", list(c.get("/openapi.json").json()["paths"].keys()))
print("GET /docs status:", c.get("/docs").status_code)
print("VERIFY OK")
