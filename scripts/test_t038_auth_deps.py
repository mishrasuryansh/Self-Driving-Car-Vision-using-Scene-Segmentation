"""T038 Authentication Dependencies & Protected User Endpoint Verification Script.

Tests:
1. Retrieval of current user profile GET `/api/v1/auth/me` with valid JWT bearer token (HTTP 200 OK).
2. Unauthenticated request to GET `/api/v1/auth/me` without token (HTTP 401 Unauthorized).
3. Request to GET `/api/v1/auth/me` with invalid token (HTTP 401 Unauthorized).
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
logger = logging.getLogger("test_t038")


def test_auth_me_endpoint():
    print("[TEST 1] Registering user and acquiring JWT access token...")
    client = TestClient(app)

    reg_payload = {
        "email": "driver_me@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Profile Driver",
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "driver_me@selfdriving.com", "password": "ValidPassword987!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    print(f" -> Acquired JWT Token: {token[:30]}...")

    print("[TEST 2] Testing GET /api/v1/auth/me with valid Bearer token...")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200, f"Expected 200 OK, got {me_resp.status_code}: {me_resp.text}"

    me_json = me_resp.json()
    assert me_json["email"] == "driver_me@selfdriving.com"
    assert me_json["full_name"] == "Profile Driver"
    assert me_json["is_active"] is True
    assert "id" in me_json
    assert "hashed_password" not in me_json
    print(f" -> Authenticated User Profile: {me_json}")
    print(" -> PASSED! GET /api/v1/auth/me verified.")

    print("[TEST 3] Testing GET /api/v1/auth/me without Authorization header...")
    unauth_resp = client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401
    assert unauth_resp.json()["error"]["code"] == "UNAUTHORIZED"
    print(" -> PASSED! Missing token handling verified.")

    print("[TEST 4] Testing GET /api/v1/auth/me with invalid token...")
    bad_resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert bad_resp.status_code == 401
    assert bad_resp.json()["error"]["code"] == "UNAUTHORIZED"
    print(" -> PASSED! Invalid token handling verified.")


def run_all():
    print("====================================================")
    print("RUNNING T038 AUTH DEPENDENCIES & GET /ME SUITE")
    print("====================================================")
    test_auth_me_endpoint()
    print("====================================================")
    print("ALL T038 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
