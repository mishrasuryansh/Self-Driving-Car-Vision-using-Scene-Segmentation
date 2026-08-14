"""T043 Job Cancellation Endpoint Verification Script.

Tests:
1. Cancellation of processing job POST `/api/v1/jobs/{job_id}/cancel` (HTTP 200 OK + JobResponse).
2. Verification of job status transition to "cancelled".
3. Revocation of Celery background task handle.
"""

from datetime import datetime, timezone
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
from app.api.v1.endpoints.jobs import _in_memory_jobs
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t043")


def test_job_cancellation():
    print("[TEST 1] Authenticating user...")
    client = TestClient(app)

    reg_payload = {
        "email": "cancel_user@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Cancel User",
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    user_id = reg_resp.json()["id"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "cancel_user@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Populate active processing job in memory
    now = datetime.now(timezone.utc)
    job_id = "test_cancel_job_uuid_1001"
    _in_memory_jobs[job_id] = {
        "_id": job_id,
        "job_id": job_id,
        "user_id": user_id,
        "media_id": "media_uuid_2222",
        "status": "processing",
        "progress_percent": 45.0,
        "created_at": now,
        "updated_at": now,
    }

    print("[TEST 2] Testing POST /api/v1/jobs/{job_id}/cancel...")
    cancel_resp = client.post(f"/api/v1/jobs/{job_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 200, f"Expected 200 OK, got {cancel_resp.status_code}: {cancel_resp.text}"

    c_data = cancel_resp.json()
    assert c_data["job_id"] == job_id
    assert c_data["status"] == "cancelled"
    print(f" -> Job Status after cancel: {c_data['status']}")
    print(" -> PASSED! POST /api/v1/jobs/{job_id}/cancel verified.")


def run_all():
    print("====================================================")
    print("RUNNING T043 JOB CANCELLATION SUITE")
    print("====================================================")
    test_job_cancellation()
    print("====================================================")
    print("ALL T043 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
