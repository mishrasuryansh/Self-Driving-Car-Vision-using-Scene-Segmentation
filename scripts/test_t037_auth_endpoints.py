"""T037 Authentication Endpoints Verification Script.

Tests:
1. User registration POST `/api/v1/auth/register` (HTTP 201 Created + UserResponse).
2. Duplicate user registration error handling (HTTP 400 Bad Request).
3. User login POST `/api/v1/auth/login` with JSON payload (HTTP 200 OK + JWT Bearer Token).
4. User login with OAuth2 form payload (HTTP 200 OK + JWT Bearer Token).
5. Invalid password login error handling (HTTP 401 Unauthorized).
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
from app.core.security import decode_access_token
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t037")


def test_user_registration_and_login():
    print("[TEST 1] Testing POST /api/v1/auth/register...")
    client = TestClient(app)

    reg_payload = {
        "email": "pilot@selfdriving.com",
        "password": "SuperSecretPassword123!",
        "full_name": "Autonomous Pilot",
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"

    user_resp = response.json()
    assert user_resp["email"] == "pilot@selfdriving.com"
    assert user_resp["full_name"] == "Autonomous Pilot"
    assert "id" in user_resp
    assert "hashed_password" not in user_resp
    print(f" -> Registered User ID: {user_resp['id']}")
    print(" -> PASSED! User registration endpoint verified.")

    print("[TEST 2] Testing duplicate user registration error handling...")
    dup_response = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_response.status_code == 400
    dup_json = dup_response.json()
    assert dup_json["error"]["code"] == "BAD_REQUEST"
    assert dup_json["error"]["message"] == "Email already registered."
    print(" -> PASSED! Duplicate registration handling verified.")

    print("[TEST 3] Testing POST /api/v1/auth/login with JSON payload...")
    login_payload = {
        "username": "pilot@selfdriving.com",
        "password": "SuperSecretPassword123!",
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200, f"Expected 200 OK, got {login_resp.status_code}: {login_resp.text}"

    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Decode and verify JWT claims
    claims = decode_access_token(token_data["access_token"])
    assert claims["sub"] == "pilot@selfdriving.com"
    print(f" -> Issued JWT Token (sub: {claims['sub']}): {token_data['access_token'][:30]}...")
    print(" -> PASSED! JSON Login endpoint & token decoding verified.")

    print("[TEST 4] Testing POST /api/v1/auth/login with OAuth2 Form data...")
    form_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "pilot@selfdriving.com", "password": "SuperSecretPassword123!"},
    )
    assert form_resp.status_code == 200
    assert "access_token" in form_resp.json()
    print(" -> PASSED! Form data Login endpoint verified.")

    print("[TEST 5] Testing invalid password login error handling...")
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"username": "pilot@selfdriving.com", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    bad_json = bad_login.json()
    assert bad_json["error"]["code"] == "UNAUTHORIZED"
    assert bad_json["error"]["message"] == "Incorrect email or password."
    print(" -> PASSED! Invalid login handling verified.")


def run_all():
    print("====================================================")
    print("RUNNING T037 AUTHENTICATION ENDPOINTS SUITE")
    print("====================================================")
    test_user_registration_and_login()
    print("====================================================")
    print("ALL T037 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
