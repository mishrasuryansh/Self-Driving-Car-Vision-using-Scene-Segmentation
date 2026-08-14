"""T033 Global Exception Handling Verification Script.

Tests:
1. Custom APIException formatting (NotFoundException, BadRequestException).
2. Standard HTTPException formatting.
3. RequestValidationError formatting (HTTP 422).
4. Unhandled Exception fallback formatting (HTTP 500).
5. Inclusion of request_id in all error response payloads.
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

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from app.exceptions import BadRequestException, NotFoundException
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t033")

# Add temporary test routes to verify error handlers
@app.get("/test-not-found", include_in_schema=False)
def route_not_found():
    raise NotFoundException(message="Item #999 not found in database.")


@app.get("/test-bad-request", include_in_schema=False)
def route_bad_request():
    raise BadRequestException(message="Param 'threshold' must be positive.", details={"field": "threshold"})


@app.get("/test-http-exception", include_in_schema=False)
def route_http_exception():
    raise HTTPException(status_code=403, detail="Access denied.")


class SampleValidationModel(BaseModel):
    age: int
    name: str


@app.post("/test-validation", include_in_schema=False)
def route_validation(payload: SampleValidationModel):
    return payload


@app.get("/test-unhandled-exception", include_in_schema=False)
def route_unhandled():
    raise RuntimeError("Unexpected database connection drop!")


def test_custom_not_found_exception():
    print("[TEST 1] Testing custom NotFoundException handler...")
    client = TestClient(app)
    response = client.get("/test-not-found")
    assert response.status_code == 404
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "NOT_FOUND"
    assert payload["error"]["message"] == "Item #999 not found in database."
    assert "request_id" in payload["error"]
    print(f" -> Response status 404, payload: {payload}")
    print(" -> PASSED! NotFoundException handler verified.")


def test_custom_bad_request_exception():
    print("[TEST 2] Testing custom BadRequestException handler...")
    client = TestClient(app)
    response = client.get("/test-bad-request")
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "BAD_REQUEST"
    assert payload["error"]["details"] == {"field": "threshold"}
    assert "request_id" in payload["error"]
    print(f" -> Response status 400, payload: {payload}")
    print(" -> PASSED! BadRequestException handler verified.")


def test_http_exception_handler():
    print("[TEST 3] Testing standard HTTPException handler...")
    client = TestClient(app)
    response = client.get("/test-http-exception")
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "FORBIDDEN"
    assert payload["error"]["message"] == "Access denied."
    assert "request_id" in payload["error"]
    print(f" -> Response status 403, payload: {payload}")
    print(" -> PASSED! HTTPException handler verified.")


def test_validation_error_handler():
    print("[TEST 4] Testing RequestValidationError handler...")
    client = TestClient(app)
    response = client.post("/test-validation", json={"age": "invalid_int"})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["message"] == "Request validation failed."
    assert "details" in payload["error"]
    assert "request_id" in payload["error"]
    print(f" -> Response status 422, payload: {payload}")
    print(" -> PASSED! Validation error handler verified.")


def test_unhandled_exception_handler():
    print("[TEST 5] Testing unhandled Exception fallback handler...")
    client = TestClient(raise_server_exceptions=False, app=app)
    response = client.get("/test-unhandled-exception")
    assert response.status_code == 500
    payload = response.json()
    assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert payload["error"]["message"] == "An unexpected internal server error occurred."
    assert "request_id" in payload["error"]
    print(f" -> Response status 500, payload: {payload}")
    print(" -> PASSED! Unhandled Exception fallback handler verified.")


def run_all():
    print("====================================================")
    print("RUNNING T033 EXCEPTION HANDLER SUITE")
    print("====================================================")
    test_custom_not_found_exception()
    test_custom_bad_request_exception()
    test_http_exception_handler()
    test_validation_error_handler()
    test_unhandled_exception_handler()
    print("====================================================")
    print("ALL T033 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
