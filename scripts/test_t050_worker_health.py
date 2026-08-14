"""T050 Worker Health Monitoring & Readiness Check Verification Script.

Tests:
1. Health endpoint GET `/api/v1/health` (HTTP 200 OK).
2. Worker readiness check GET `/api/v1/health/worker` (HTTP 200 OK + redis_status + worker_active).
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
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t050")


def test_worker_health_endpoint():
    client = TestClient(app)

    print("[TEST 1] Testing GET /api/v1/health...")
    h_resp = client.get("/api/v1/health")
    assert h_resp.status_code == 200
    h_json = h_resp.json()
    assert h_json["status"] == "ok"
    assert "version" in h_json
    print(f" -> System Health Response: {h_json}")

    print("[TEST 2] Testing GET /api/v1/health/worker...")
    w_resp = client.get("/api/v1/health/worker")
    assert w_resp.status_code == 200
    w_json = w_resp.json()
    assert "status" in w_json
    assert "redis_status" in w_json
    assert "worker_active" in w_json
    print(f" -> Worker Health Response: {w_json}")
    print(" -> PASSED! T050 Worker health monitoring verified.")


def run_all():
    print("====================================================")
    print("RUNNING T050 WORKER HEALTH MONITORING SUITE")
    print("====================================================")
    test_worker_health_endpoint()
    print("====================================================")
    print("ALL T050 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
