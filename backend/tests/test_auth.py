"""Backend User Authentication Router Integration Tests (T089).

Tests:
1. Registration success (HTTP 201 Created).
2. Duplicate registration rejection (HTTP 400 / 409 Conflict).
3. User login token generation (HTTP 200 OK).
4. Protected profile endpoint `GET /api/v1/auth/me` (HTTP 200 OK vs HTTP 401 Unauthorized).
"""

import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_registration_flow():
    reg_payload = {
        "email": "auto_auth_test@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Auth Integration Tester",
    }
    # 1. Successful registration
    r1 = client.post("/api/v1/auth/register", json=reg_payload)
    assert r1.status_code == 201
    assert r1.json()["email"] == reg_payload["email"]

    # 2. Duplicate registration attempt
    r2 = client.post("/api/v1/auth/register", json=reg_payload)
    assert r2.status_code == 400


def test_auth_login_and_me():
    login_payload = {
        "username": "auto_auth_test@selfdriving.com",
        "password": "ValidPassword987!",
    }
    # 1. Login success
    l1 = client.post("/api/v1/auth/login", json=login_payload)
    assert l1.status_code == 200
    token = l1.json()["access_token"]
    assert token is not None

    # 2. GET /me with token
    m1 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert m1.status_code == 200
    assert m1.json()["email"] == login_payload["username"]

    # 3. GET /me without token
    m2 = client.get("/api/v1/auth/me")
    assert m2.status_code == 401
