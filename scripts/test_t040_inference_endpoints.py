"""T040 Scene Segmentation Inference & Task Status Verification Script.

Tests:
1. Triggering inference job POST `/api/v1/inference/segment` (HTTP 202 Accepted + InferenceResponse).
2. Polling task status GET `/api/v1/inference/tasks/{task_id}` (HTTP 200 OK + TaskStatusResponse).
3. Verification of Section 8.2 performance metrics shape (fps, avgInferenceMs, classDistribution).
4. Verification of output segmented file creation in STORAGE_OUTPUTS_PATH.
5. Non-existent media_id handling (HTTP 404 Not Found).
6. Non-existent task_id handling (HTTP 404 Not Found).
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
logger = logging.getLogger("test_t040")


def test_inference_and_task_status():
    print("[TEST 1] Authenticating user and uploading media item...")
    client = TestClient(app)

    reg_payload = {
        "email": "segmenter@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Segmentation Pilot",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "segmenter@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload test image
    fake_image_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"Y" * 1024
    files = {"file": ("urban_street.jpg", io.BytesIO(fake_image_bytes), "image/jpeg")}
    upload_resp = client.post("/api/v1/media/upload", headers=headers, files=files)
    assert upload_resp.status_code == 201
    media_id = upload_resp.json()["id"]
    print(f" -> Uploaded Media ID: {media_id}")

    print("[TEST 2] Triggering scene segmentation POST /api/v1/inference/segment...")
    segment_req = {"media_id": media_id, "use_fp16": False, "use_torchscript": True}
    seg_resp = client.post("/api/v1/inference/segment", headers=headers, json=segment_req)
    assert seg_resp.status_code == 202, f"Expected 202 Accepted, got {seg_resp.status_code}: {seg_resp.text}"

    seg_data = seg_resp.json()
    assert seg_data["media_id"] == media_id
    assert "task_id" in seg_data
    task_id = seg_data["task_id"]
    print(f" -> Triggered Task ID: {task_id}, Status: {seg_data['status']}")
    print(" -> PASSED! Trigger segmentation endpoint verified.")

    print("[TEST 3] Querying task status GET /api/v1/inference/tasks/{task_id}...")
    status_resp = client.get(f"/api/v1/inference/tasks/{task_id}", headers=headers)
    assert status_resp.status_code == 200, f"Expected 200 OK, got {status_resp.status_code}: {status_resp.text}"

    status_data = status_resp.json()
    assert status_data["task_id"] == task_id
    assert status_data["media_id"] == media_id
    assert status_data["status"] == "completed"
    assert "metrics" in status_data and status_data["metrics"] is not None

    metrics = status_data["metrics"]
    assert "fps" in metrics and metrics["fps"] > 0
    assert "avgInferenceMs" in metrics and metrics["avgInferenceMs"] > 0
    assert "classDistribution" in metrics and isinstance(metrics["classDistribution"], dict)
    assert os.path.exists(status_data["output_path"]), f"Output file does not exist on disk: {status_data['output_path']}"

    print(f" -> Performance Metrics: FPS={metrics['fps']}, Latency={metrics['avgInferenceMs']}ms")
    print(f" -> Class Distribution: {metrics['classDistribution']}")
    print(f" -> Output Path: {status_data['output_path']}")
    print(" -> PASSED! Task status & metrics query verified.")

    print("[TEST 4] Testing non-existent media_id handling...")
    bad_media = client.post(
        "/api/v1/inference/segment",
        headers=headers,
        json={"media_id": "non_existent_media_id_999"},
    )
    assert bad_media.status_code == 404
    assert bad_media.json()["error"]["code"] == "NOT_FOUND"
    print(" -> PASSED! Non-existent media_id handling verified.")

    print("[TEST 5] Testing non-existent task_id handling...")
    bad_task = client.get("/api/v1/inference/tasks/non_existent_task_id_999", headers=headers)
    assert bad_task.status_code == 404
    assert bad_task.json()["error"]["code"] == "NOT_FOUND"
    print(" -> PASSED! Non-existent task_id handling verified.")


def run_all():
    print("====================================================")
    print("RUNNING T040 INFERENCE ENDPOINTS SUITE")
    print("====================================================")
    test_inference_and_task_status()
    print("====================================================")
    print("ALL T040 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
