"""T032 Middleware, CORS, and Tracing Headers Verification Script.

Tests:
1. Verification of X-Request-ID generation and response header injection on GET `/api/v1/health`.
2. Verification of incoming X-Request-ID propagation.
3. Verification of X-Process-Time execution latency response header injection.
4. Verification of CORS middleware preflight OPTIONS header handling.
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
logger = logging.getLogger("test_t032")


def test_request_id_and_process_time_headers():
    """Verify X-Request-ID and X-Process-Time response headers."""
    print("[TEST 1] Testing X-Request-ID and X-Process-Time header generation...")
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    assert "x-request-id" in response.headers, "Missing 'X-Request-ID' in response headers"
    assert "x-process-time" in response.headers, "Missing 'X-Process-Time' in response headers"

    req_id = response.headers["x-request-id"]
    proc_time = float(response.headers["x-process-time"])

    assert len(req_id) > 0, "X-Request-ID header is empty"
    assert proc_time >= 0.0, f"Invalid X-Process-Time: {proc_time}"

    print(f" -> Generated X-Request-ID: {req_id}")
    print(f" -> Injected X-Process-Time: {proc_time:.6f}s")
    print(" -> PASSED! Middleware response headers verified.")


def test_custom_request_id_propagation():
    """Verify propagation of custom client X-Request-ID header."""
    print("[TEST 2] Testing custom X-Request-ID header propagation...")
    client = TestClient(app)
    custom_id = "test-custom-trace-id-998877"

    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    print(f" -> Propagated custom ID: {response.headers.get('x-request-id')}")
    print(" -> PASSED! Custom X-Request-ID propagation verified.")


def test_cors_preflight_headers():
    """Verify CORS preflight OPTIONS request handling."""
    print("[TEST 3] Testing CORS preflight headers...")
    client = TestClient(app)

    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Request-ID",
    }
    response = client.options("/api/v1/health", headers=headers)
    assert response.status_code == 200, f"Expected 200 for OPTIONS, got {response.status_code}"
    assert "access-control-allow-origin" in response.headers
    print(f" -> CORS Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    print(" -> PASSED! CORS preflight response headers verified.")


def run_all():
    print("====================================================")
    print("RUNNING T032 MIDDLEWARE & TRACING SUITE")
    print("====================================================")
    test_request_id_and_process_time_headers()
    test_custom_request_id_propagation()
    test_cors_preflight_headers()
    print("====================================================")
    print("ALL T032 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
