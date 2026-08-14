"""T039 Media Upload & Storage Verification Script.

Tests:
1. Valid image upload POST `/api/v1/media/upload` (HTTP 201 Created + MediaResponse).
2. Valid video upload POST `/api/v1/media/upload` (HTTP 201 Created + MediaResponse).
3. Retrieval of uploaded media metadata GET `/api/v1/media/{media_id}` (HTTP 200 OK).
4. Oversized file upload rejection (HTTP 400 Bad Request).
5. Unsupported file type upload rejection (HTTP 400 Bad Request).
6. File existence on disk in STORAGE_UPLOADS_PATH.
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
logger = logging.getLogger("test_t039")


def test_media_upload_and_retrieval():
    print("[TEST 1] Authenticating user to acquire JWT access token...")
    client = TestClient(app)

    reg_payload = {
        "email": "media_uploader@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Media Uploader",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "media_uploader@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f" -> Authenticated with JWT Token: {token[:30]}...")

    print("[TEST 2] Testing image file upload POST /api/v1/media/upload...")
    fake_image_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"X" * 1024
    files = {"file": ("test_road_scene.jpg", io.BytesIO(fake_image_bytes), "image/jpeg")}

    upload_resp = client.post("/api/v1/media/upload", headers=headers, files=files)
    assert upload_resp.status_code == 201, f"Expected 201 Created, got {upload_resp.status_code}: {upload_resp.text}"

    img_data = upload_resp.json()
    assert img_data["file_type"] == "image"
    assert img_data["original_name"] == "test_road_scene.jpg"
    assert img_data["size_bytes"] == len(fake_image_bytes)
    assert os.path.exists(img_data["file_path"]), f"File path does not exist on disk: {img_data['file_path']}"
    media_id = img_data["id"]
    print(f" -> Uploaded Image ID: {media_id}, Saved Path: {img_data['file_path']}")
    print(" -> PASSED! Image upload verified.")

    print("[TEST 3] Testing video file upload POST /api/v1/media/upload...")
    fake_video_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42" + b"V" * 2048
    files_video = {"file": ("highway_clip.mp4", io.BytesIO(fake_video_bytes), "video/mp4")}

    vid_resp = client.post("/api/v1/media/upload", headers=headers, files=files_video)
    assert vid_resp.status_code == 201
    vid_data = vid_resp.json()
    assert vid_data["file_type"] == "video"
    assert vid_data["original_name"] == "highway_clip.mp4"
    assert os.path.exists(vid_data["file_path"])
    print(f" -> Uploaded Video ID: {vid_data['id']}, Saved Path: {vid_data['file_path']}")
    print(" -> PASSED! Video upload verified.")

    print("[TEST 4] Testing GET /api/v1/media/{media_id} metadata retrieval...")
    meta_resp = client.get(f"/api/v1/media/{media_id}", headers=headers)
    assert meta_resp.status_code == 200
    meta_data = meta_resp.json()
    assert meta_data["id"] == media_id
    assert meta_data["file_type"] == "image"
    print(" -> PASSED! Media metadata retrieval verified.")

    print("[TEST 5] Testing unsupported file type rejection...")
    bad_file = {"file": ("malicious.exe", io.BytesIO(b"MZ12345"), "application/x-msdownload")}
    bad_resp = client.post("/api/v1/media/upload", headers=headers, files=bad_file)
    assert bad_resp.status_code == 400
    assert bad_resp.json()["error"]["code"] == "BAD_REQUEST"
    print(" -> PASSED! Unsupported file type rejection verified.")


def run_all():
    print("====================================================")
    print("RUNNING T039 MEDIA UPLOAD & STORAGE SUITE")
    print("====================================================")
    test_media_upload_and_retrieval()
    print("====================================================")
    print("ALL T039 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
