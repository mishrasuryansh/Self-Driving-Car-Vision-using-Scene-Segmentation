"""T042 Job Status Tracking & Query Verification Script.

Tests:
1. Retrieval of job status GET `/api/v1/jobs/{job_id}` (HTTP 200 OK + JobResponse).
2. Listing all jobs for current user GET `/api/v1/jobs` (HTTP 200 OK + list of JobResponse).
3. Non-existent job query error handling (HTTP 404 Not Found).
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
logger = logging.getLogger("test_t042")


def test_jobs_endpoints():
    print("[TEST 1] Authenticating user...")
    client = TestClient(app)

    reg_payload = {
        "email": "job_user@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Job User",
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    user_id = reg_resp.json()["id"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "job_user@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Populate dummy job in memory
    now = datetime.now(timezone.utc)
    job_id = "test_job_uuid_9999"
    _in_memory_jobs[job_id] = {
        "_id": job_id,
        "job_id": job_id,
        "user_id": user_id,
        "media_id": "media_uuid_1111",
        "status": "completed",
        "progress_percent": 100.0,
        "output_path": "storage/outputs/segmented_test_job_uuid_9999.jpg",
        "metrics": {"fps": 32.5, "avgInferenceMs": 30.77, "classDistribution": {"road": 50.0, "sky": 20.0}},
        "created_at": now,
        "updated_at": now,
    }

    print("[TEST 2] Testing GET /api/v1/jobs/{job_id}...")
    job_resp = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert job_resp.status_code == 200, f"Expected 200 OK, got {job_resp.status_code}: {job_resp.text}"

    j_data = job_resp.json()
    assert j_data["job_id"] == job_id
    assert j_data["status"] == "completed"
    assert j_data["metrics"]["fps"] == 32.5
    print(f" -> Job Data: ID={j_data['job_id']}, Status={j_data['status']}, FPS={j_data['metrics']['fps']}")
    print(" -> PASSED! GET /api/v1/jobs/{job_id} verified.")

    print("[TEST 3] Testing GET /api/v1/jobs list endpoint...")
    list_resp = client.get("/api/v1/jobs", headers=headers)
    assert list_resp.status_code == 200
    jobs_list = list_resp.json()
    assert isinstance(jobs_list, list) and len(jobs_list) >= 1
    print(f" -> Retreived {len(jobs_list)} job records for current user.")
    print(" -> PASSED! GET /api/v1/jobs list endpoint verified.")

    print("[TEST 4] Testing non-existent job query...")
    bad_resp = client.get("/api/v1/jobs/non_existent_job_123", headers=headers)
    assert bad_resp.status_code == 404
    assert bad_resp.json()["error"]["code"] == "NOT_FOUND"
    print(" -> PASSED! Non-existent job query handling verified.")


def run_all():
    print("====================================================")
    print("RUNNING T042 JOB STATUS & QUERY SUITE")
    print("====================================================")
    test_jobs_endpoints()
    print("====================================================")
    print("ALL T042 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
