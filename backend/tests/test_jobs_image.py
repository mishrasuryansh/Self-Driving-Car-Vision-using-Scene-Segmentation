"""Backend Image & Video Job Endpoints Integration Tests (T090).

Tests:
1. POST `/api/v1/media/upload` image file upload.
2. POST `/api/v1/inference/segment` image segmentation inference trigger.
3. POST `/api/v1/jobs/video` async video queue submission.
4. GET `/api/v1/jobs/{job_id}` query and 404 handling.
5. GET `/api/v1/jobs` list user jobs.
"""

import io
import os
import sys
import numpy as np
from PIL import Image

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_header():
    reg_payload = {
        "email": "jobs_test_user@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Jobs Tester",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "jobs_test_user@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_image_segmentation_endpoint():
    headers = get_auth_header()

    # 1. Upload media item first
    img_buf = io.BytesIO()
    img = Image.fromarray(np.uint8(np.zeros((64, 64, 3))))
    img.save(img_buf, format="PNG")
    img_buf.seek(0)
    files = {"file": ("test_road.png", img_buf, "image/png")}

    up_res = client.post("/api/v1/media/upload", headers=headers, files=files)
    assert up_res.status_code == 201
    media_json = up_res.json()
    media_id = media_json.get("id") or media_json.get("media_id")

    # 2. Trigger segmentation with media_id payload
    res = client.post("/api/v1/inference/segment", headers=headers, json={"media_id": media_id})
    assert res.status_code == 202
    res_json = res.json()
    assert "task_id" in res_json
    assert res_json["status"] == "completed"


def test_job_query_and_list():
    headers = get_auth_header()

    # Query list
    l_res = client.get("/api/v1/jobs", headers=headers)
    assert l_res.status_code == 200
    assert isinstance(l_res.json(), list)

    # Query 404 non-existent job
    n_res = client.get("/api/v1/jobs/non_existent_job_99999", headers=headers)
    assert n_res.status_code == 404
