"""Automated End-to-End Test for Real Cityscapes Scene Segmentation Pipeline.

Executes full authentication, media upload, real SegFormer/PyTorch inference execution,
task metrics validation, output file verification, and class distribution checks.
"""

from datetime import datetime
import os
import sys
import uuid

# Ensure backend & inference engine are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
engine_path = os.path.join(repo_root, "inference-engine")

for p in [repo_root, backend_path, engine_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app
from PIL import Image

def run_e2e_test():
    client = TestClient(app)
    print("=" * 60)
    print("STARTING REAL E2E CITYSCAPES PIPELINE INTEGRATION TEST")
    print("=" * 60)

    # 1. Register User
    test_email = f"e2e_pilot_{uuid.uuid4().hex[:8]}@selfdriving.com"
    test_password = "SecurePassword123!"
    test_name = "Autonomous Test Driver"

    print(f"\n[STEP 1] Registering test user: {test_email}...")
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": test_email, "password": test_password, "full_name": test_name},
    )
    assert reg_resp.status_code == 201, f"Registration failed ({reg_resp.status_code}): {reg_resp.text}"
    print(" -> SUCCESS: User registered.")

    # 2. Login User
    print(f"\n[STEP 2] Logging in user: {test_email}...")
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": test_email, "password": test_password},
    )
    assert login_resp.status_code == 200, f"Login failed ({login_resp.status_code}): {login_resp.text}"
    token_data = login_resp.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(" -> SUCCESS: Obtained JWT access token.")

    # 3. GET /me
    print("\n[STEP 3] Validating profile (GET /api/v1/auth/me)...")
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200, f"/me failed: {me_resp.text}"
    print(f" -> SUCCESS: Authenticated as {me_resp.json().get('email')}")

    # 4. Upload Real Road Image
    sample_img_path = os.path.join(repo_root, "tests", "fixtures", "sample_road_scene.jpg")
    assert os.path.exists(sample_img_path), f"Test fixture '{sample_img_path}' missing."

    print(f"\n[STEP 4] Uploading real road scene image '{sample_img_path}'...")
    with open(sample_img_path, "rb") as f:
        upload_resp = client.post(
            "/api/v1/media/upload",
            headers=headers,
            files={"file": ("sample_road_scene.jpg", f, "image/jpeg")},
        )
    assert upload_resp.status_code == 201, f"Upload failed ({upload_resp.status_code}): {upload_resp.text}"
    media_data = upload_resp.json()
    media_id = media_data["id"]
    print(f" -> SUCCESS: Media uploaded (ID: {media_id}, path: {media_data['file_path']})")

    # 5. Trigger Real Segmentation Inference
    print(f"\n[STEP 5] Triggering real Cityscapes segmentation inference (POST /api/v1/inference/segment)...")
    seg_resp = client.post(
        "/api/v1/inference/segment",
        headers=headers,
        json={"media_id": media_id},
    )
    assert seg_resp.status_code in (200, 202), f"Segmentation failed ({seg_resp.status_code}): {seg_resp.text}"
    task_data = seg_resp.json()
    task_id = task_data["task_id"]
    print(f" -> SUCCESS: Inference task dispatched (Task ID: {task_id})")

    # 6. Fetch Task Status & Verify Output
    print(f"\n[STEP 6] Polling task status (GET /api/v1/inference/tasks/{task_id})...")
    status_resp = client.get(f"/api/v1/inference/tasks/{task_id}", headers=headers)
    assert status_resp.status_code == 200, f"Task status fetch failed: {status_resp.text}"
    task_result = status_resp.json()
    assert task_result["status"] == "completed", f"Task status is '{task_result['status']}'"

    output_path = task_result["output_path"]
    metrics = task_result["metrics"]
    print(" -> SUCCESS: Task completed.")
    print(f"    - Output Path: {output_path}")
    print(f"    - Inference Latency: {metrics.get('avgInferenceMs')} ms")
    print(f"    - FPS: {metrics.get('fps')}")
    print(f"    - Class Distribution: {metrics.get('classDistribution')}")

    # 7. Strict Non-Synthetic Output Verification
    print("\n[STEP 7] Performing strict non-synthetic output file verification...")
    assert os.path.exists(output_path), f"Output file '{output_path}' does not exist."
    out_size = os.path.getsize(output_path)
    print(f"    - Output File Size: {out_size} bytes")

    # Ensure output is NOT a fake text file
    with open(output_path, "rb") as f:
        header_bytes = f.read(100)
        assert b"SYNTHETIC" not in header_bytes, "FAIL: Output contains synthetic byte text!"

    assert out_size > 2000, f"FAIL: Output file size {out_size} bytes is unreasonably small (< 2KB)."

    # Verify PIL image decodability
    with Image.open(output_path) as img:
        img.verify()
        print(f"    - Decoded Output Dimensions: {img.size[0]}x{img.size[1]} ({img.format} format)")

    # Verify non-empty real class distribution
    class_dist = metrics.get("classDistribution", {})
    assert len(class_dist) > 0, "FAIL: Class distribution is empty."
    assert "road" in class_dist or "building" in class_dist or "sky" in class_dist, "FAIL: Expected Cityscapes classes not found in distribution."

    print("\n" + "=" * 60)
    print(">>> ALL E2E REAL PIPELINE VERIFICATION TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_e2e_test()
        sys.exit(0)
    except Exception as exc:
        print(f"\n❌ E2E TEST FAILED: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
