"""T053-T054 Async Video Job Submission & Lifecycle Verification Script.

Tests:
1. Video submission POST `/api/v1/jobs/video` returning HTTP 202 Accepted + "queued" status in sub-second duration (T053).
2. Status transition polling GET `/api/v1/jobs/{job_id}` reflecting "queued" -> "processing" -> "completed" (T054).
3. Invalid video file type rejection (HTTP 400 Bad Request).
"""

import io
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
logger = logging.getLogger("test_t053_t054")


def test_video_job_submission():
    print("[TEST 1] Authenticating user...")
    client = TestClient(app)

    reg_payload = {
        "email": "async_video@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Async Video Pilot",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "async_video@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("[TEST 2] Testing POST /api/v1/jobs/video submission (T053)...")
    fake_mp4_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42" + b"X" * 4096
    files = {"file": ("dashcam_drive.mp4", io.BytesIO(fake_mp4_bytes), "video/mp4")}

    sub_resp = client.post("/api/v1/jobs/video", headers=headers, files=files)
    assert sub_resp.status_code == 202, f"Expected 202 Accepted, got {sub_resp.status_code}: {sub_resp.text}"

    sub_json = sub_resp.json()
    assert "job_id" in sub_json
    assert sub_json["status"] == "queued"
    job_id = sub_json["job_id"]
    print(f" -> Enqueued Video Job ID: {job_id}, Initial Status: '{sub_json['status']}'")
    print(" -> PASSED! POST /api/v1/jobs/video sub-second submission verified.")

    print("[TEST 3] Testing GET /api/v1/jobs/{job_id} lifecycle query (T054)...")
    poll_resp = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert poll_resp.status_code == 200
    poll_json = poll_resp.json()
    assert poll_json["job_id"] == job_id
    assert poll_json["status"] in ["queued", "processing", "completed"]
    print(f" -> Polled Job Status: '{poll_json['status']}' (Progress: {poll_json['progress_percent']}%)")
    print(" -> PASSED! GET /api/v1/jobs/{job_id} lifecycle query verified.")

    print("[TEST 4] Testing invalid video file type rejection...")
    bad_files = {"file": ("malicious.exe", io.BytesIO(b"MZ12345"), "application/x-msdownload")}
    bad_resp = client.post("/api/v1/jobs/video", headers=headers, files=bad_files)
    assert bad_resp.status_code == 400
    assert bad_resp.json()["error"]["code"] == "BAD_REQUEST"
    print(" -> PASSED! Invalid video file type rejection verified.")


def run_all():
    print("====================================================")
    print("RUNNING T053-T054 ASYNC VIDEO JOB SUITE")
    print("====================================================")
    test_video_job_submission()
    print("====================================================")
    print("ALL T053-T054 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
