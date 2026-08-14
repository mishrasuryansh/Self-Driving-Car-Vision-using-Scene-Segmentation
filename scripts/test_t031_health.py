"""T031 FastAPI Application Initialization & Health Endpoint Unit Test Script.

Tests:
1. Verification of Pydantic Settings singleton reading .env.example contract variables.
2. FastAPI app instance instantiation.
3. Unit test hitting GET `/api/v1/health` via TestClient, asserting HTTP 200 and Section 8.3 response shape `{"status": "ok", "version": "1.0.0"}`.
"""

import logging
import os
import sys

# Ensure repository root and backend directory are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t031")


def test_settings_initialization():
    """Verify application Settings initialization and environment variables bindings."""
    print("[TEST 1] Testing Settings configuration loading...")
    assert settings.PROJECT_NAME == "Self-Driving Car Vision API"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.VERSION == "1.0.0"
    assert settings.BACKEND_PORT == 8000
    assert settings.STORAGE_UPLOADS_PATH == "/app/storage/uploads"
    assert settings.MAX_IMAGE_SIZE_MB == 10
    print(" -> PASSED! Settings configuration validated successfully.")


def test_health_endpoint_unit():
    """Verify GET /api/v1/health returns HTTP 200 with Section 8.3 payload."""
    print("[TEST 2] Testing GET /api/v1/health endpoint via FastAPI TestClient...")
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    payload = response.json()
    assert payload == {"status": "ok", "version": "1.0.0"}, f"Unexpected health response payload: {payload}"
    print(f" -> Response status: {response.status_code}, Payload: {payload}")
    print(" -> PASSED! GET /api/v1/health verified successfully.")


def test_health_root_alias():
    """Verify GET /health root alias endpoint."""
    print("[TEST 3] Testing GET /health root alias endpoint...")
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}
    print(" -> PASSED! Root health check alias verified successfully.")


def run_all():
    print("====================================================")
    print("RUNNING T031 FASTAPI APP & HEALTH ENDPOINT SUITE")
    print("====================================================")
    test_settings_initialization()
    test_health_endpoint_unit()
    test_health_root_alias()
    print("====================================================")
    print("ALL T031 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
