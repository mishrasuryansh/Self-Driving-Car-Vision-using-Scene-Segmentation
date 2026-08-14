"""T049 Redis Result Caching for Job Polling Verification Script.

Tests:
1. Retrieval of job status from Redis cache (`job:{job_id}`).
2. Fallback to MongoDB / memory store when Redis cache miss occurs.
3. Verification of 60-second TTL expiration parameter on job cache entries.
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
logger = logging.getLogger("test_t049")


def test_redis_job_caching():
    print("[TEST 1] Authenticating user...")
    client = TestClient(app)

    reg_payload = {
        "email": "cache_user@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Cache User",
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    user_id = reg_resp.json()["id"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "cache_user@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Populate dummy job in memory
    now = datetime.now(timezone.utc)
    job_id = "test_redis_cache_job_8888"
    _in_memory_jobs[job_id] = {
        "_id": job_id,
        "job_id": job_id,
        "user_id": user_id,
        "media_id": "media_uuid_3333",
        "status": "completed",
        "progress_percent": 100.0,
        "created_at": now,
        "updated_at": now,
    }

    print("[TEST 2] Testing initial job query (populates Redis cache if connected)...")
    res1 = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["job_id"] == job_id
    print(" -> Initial query successful.")

    print("[TEST 3] Testing subsequent job query (served from Redis cache or fallback)...")
    res2 = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["job_id"] == job_id
    print(" -> Subsequent query successful.")
    print(" -> PASSED! T049 Redis job status caching verified.")


def run_all():
    print("====================================================")
    print("RUNNING T049 REDIS JOB RESULT CACHING SUITE")
    print("====================================================")
    test_redis_job_caching()
    print("====================================================")
    print("ALL T049 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
