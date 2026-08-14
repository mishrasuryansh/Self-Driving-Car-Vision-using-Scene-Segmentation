"""Unit test for FastAPI health endpoint."""

from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": settings.VERSION}
