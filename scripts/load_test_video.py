"""Video Job Submissions Load Test Script (T104).

Simulates N concurrent async video uploads against server, polls job completion status,
flags lost or stuck jobs, and records total batch wall-clock completion time.
"""

import argparse
import concurrent.futures
import io
import logging
import os
import sys
import time
from fastapi.testclient import TestClient

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("load_test_video")


def submit_and_poll_video(client, headers, timeout_seconds=30):
    fake_video = b"FAKEMP4HEADER" + b"\x00" * 1024
    files = {"file": ("test_dashcam.mp4", io.BytesIO(fake_video), "video/mp4")}

    res = client.post("/api/v1/jobs/video", headers=headers, files=files)
    if res.status_code != 202:
        return "failed"

    job_id = res.json().get("job_id")
    start_t = time.time()

    while time.time() - start_t < timeout_seconds:
        status_res = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        if status_res.status_code == 200:
            st = status_res.json().get("status")
            if st in ("completed", "failed", "cancelled"):
                return st
        time.sleep(0.5)

    return "lost"


def run_video_load_test(num_jobs: int = 5, concurrency: int = 2):
    client = TestClient(app)

    # Auth login
    client.post(
        "/api/v1/auth/register",
        json={"email": "loadtest_vid@selfdriving.com", "password": "Pass123!", "full_name": "Video Load Tester"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "loadtest_vid@selfdriving.com", "password": "Pass123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("Executing video load test: %d jobs, concurrency %d...", num_jobs, concurrency)
    start_wall_clock = time.time()

    statuses = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(submit_and_poll_video, client, headers) for _ in range(num_jobs)]
        for f in concurrent.futures.as_completed(futures):
            statuses.append(f.result())

    total_time = time.time() - start_wall_clock
    completed = statuses.count("completed")
    failed = statuses.count("failed")
    lost = statuses.count("lost")

    logger.info("====================================================")
    logger.info("VIDEO LOAD TEST RESULTS (T104)")
    logger.info("====================================================")
    logger.info("Total Jobs Submitted: %d", num_jobs)
    logger.info("Completed: %d | Failed: %d | Lost/Timeout: %d", completed, failed, lost)
    logger.info("Total Batch Wall-Clock Time: %.2f s", total_time)
    logger.info("Scalability Check (Zero Lost Jobs): %s", "PASSED" if lost == 0 else "FAILED")
    logger.info("====================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video job endpoint load test.")
    parser.add_argument("--jobs", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=2)
    args = parser.parse_args()

    run_video_load_test(args.jobs, args.concurrency)
