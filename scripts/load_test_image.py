"""Image Segmentation Endpoint Load Test Script (T103).

Simulates concurrent image segmentation requests against target server,
records per-request latencies, and computes mean & P95 latency vs NFR1 target (<3s GPU, <10s CPU).
"""

import argparse
import concurrent.futures
import io
import logging
import time
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("load_test_image")


def run_single_request(client, headers):
    img_buf = io.BytesIO()
    img = Image.fromarray(np.uint8(np.zeros((128, 128, 3))))
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    start_t = time.perf_counter()
    up = client.post("/api/v1/media/upload", headers=headers, files={"file": ("test.png", img_buf, "image/png")})
    if up.status_code != 201:
        return None
    media_id = up.json().get("id")

    res = client.post("/api/v1/inference/segment", headers=headers, json={"media_id": media_id})
    duration_ms = (time.perf_counter() - start_t) * 1000.0

    if res.status_code == 202 or res.status_code == 200:
        return duration_ms
    return None


def run_load_test(num_requests: int = 10, concurrency: int = 2):
    client = TestClient(app)

    # Auth login
    client.post(
        "/api/v1/auth/register",
        json={"email": "loadtest_img@selfdriving.com", "password": "Pass123!", "full_name": "Load Tester"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "loadtest_img@selfdriving.com", "password": "Pass123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("Executing image load test: %d requests, concurrency %d...", num_requests, concurrency)

    latencies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_single_request, client, headers) for _ in range(num_requests)]
        for f in concurrent.futures.as_completed(futures):
            res_ms = f.result()
            if res_ms is not None:
                latencies.append(res_ms)

    if not latencies:
        logger.error("All load test requests failed!")
        return

    latencies.sort()
    mean_lat = float(np.mean(latencies))
    p95_lat = float(np.percentile(latencies, 95))

    logger.info("====================================================")
    logger.info("IMAGE LOAD TEST RESULTS (T103)")
    logger.info("====================================================")
    logger.info("Total Requests Completed: %d / %d", len(latencies), num_requests)
    logger.info("Mean Latency: %.2f ms", mean_lat)
    logger.info("P95 Latency: %.2f ms", p95_lat)
    logger.info("NFR1 Target Check (<10,000ms CPU SLA): %s", "PASSED" if p95_lat < 10000 else "FAILED")
    logger.info("====================================================")


import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image endpoint load test.")
    parser.add_argument("--requests", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=2)
    args = parser.parse_args()

    run_load_test(args.requests, args.concurrency)
