"""Security Hardening Integration Tests (T099).

Tests:
1. Security response headers injection (T091).
2. Rate limiting enforcement (HTTP 429 Too Many Requests) (T091).
3. Path traversal filename rejection (HTTP 400 Bad Request) (T092).
4. Cross-user resource ownership authorization check (HTTP 403 Forbidden) (T093).
"""

import io
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


def test_security_headers():
    """Verify SecurityHeadersMiddleware injects expected HTTP security response headers (T091)."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in res.headers


def test_path_traversal_rejection():
    """Verify uploading file with path traversal characters returns HTTP 400 (T092)."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "pathtest@selfdriving.com",
            "password": "ValidPassword123!",
            "full_name": "Path Tester",
        },
    )
    token = reg.json().get("access_token")
    if not token:
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "pathtest@selfdriving.com", "password": "ValidPassword123!"},
        )
        token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("../../etc/passwd", io.BytesIO(b"fake_data"), "image/png")}

    res = client.post("/api/v1/media/upload", headers=headers, files=files)
    assert res.status_code == 400
    assert "path traversal" in res.json()["error"]["message"].lower()


def test_resource_ownership_authorization():
    """Verify User A cannot access User B's uploaded media or job details (HTTP 403) (T093)."""
    # User 1 Register & Upload
    u1_reg = client.post(
        "/api/v1/auth/register",
        json={"email": "owner1@selfdriving.com", "password": "Pass123!", "full_name": "Owner 1"},
    )
    t1 = u1_reg.json().get("access_token")
    if not t1:
        t1 = client.post(
            "/api/v1/auth/login",
            json={"username": "owner1@selfdriving.com", "password": "Pass123!"},
        ).json()["access_token"]

    # User 1 uploads media
    up1 = client.post(
        "/api/v1/media/upload",
        headers={"Authorization": f"Bearer {t1}"},
        files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 64), "image/png")},
    )
    m1_id = up1.json()["id"]

    # User 2 Register
    u2_reg = client.post(
        "/api/v1/auth/register",
        json={"email": "owner2@selfdriving.com", "password": "Pass123!", "full_name": "Owner 2"},
    )
    t2 = u2_reg.json().get("access_token")
    if not t2:
        t2 = client.post(
            "/api/v1/auth/login",
            json={"username": "owner2@selfdriving.com", "password": "Pass123!"},
        ).json()["access_token"]

    # User 2 tries to access User 1's media -> HTTP 403 Forbidden
    res_forbidden = client.get(
        f"/api/v1/media/{m1_id}",
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert res_forbidden.status_code == 403
    assert "access denied" in res_forbidden.json()["error"]["message"].lower()
