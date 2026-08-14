"""MongoDB Real Persistence Automated Verification Test Script.

Validates end-to-end user registration, media upload, and scene segmentation task lifecycle
directly against MongoDB database collections ('users', 'media', 'tasks'), confirming metadata persistence
and post-restart document survival.
"""

import asyncio
import os
import sys
import uuid
from PIL import Image
from motor.motor_asyncio import AsyncIOMotorClient

# Add backend and inference-engine directories to sys.path BEFORE importing app.main
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
engine_path = os.path.join(repo_root, "inference-engine")

if engine_path not in sys.path:
    sys.path.insert(0, engine_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.main import app


def run_mongodb_persistence_test():
    print("=" * 60)
    print("STARTING REAL MONGODB PERSISTENCE VERIFICATION TEST")
    print("=" * 60)

    test_uid = uuid.uuid4().hex[:8]
    test_email = f"mongo_driver_{test_uid}@selfdriving.com"
    test_password = "SecurePassword123!"
    test_full_name = f"MongoDB Tester {test_uid}"

    # Use FastAPI TestClient inside lifespan context manager
    with TestClient(app) as client:
        # STEP 1: Register User
        print(f"\n[STEP 1] Registering test user: {test_email}...")
        reg_res = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": test_full_name,
            },
        )
        assert reg_res.status_code == 201, f"User registration failed: {reg_res.text}"
        user_id = reg_res.json()["id"]
        print(f" -> SUCCESS: Registered user ID: {user_id}")

        # STEP 2: Authenticate User
        print(f"\n[STEP 2] Authenticating user: {test_email}...")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": test_email, "password": test_password},
        )
        assert login_res.status_code == 200, f"User login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(" -> SUCCESS: Obtained JWT access token.")

        # STEP 3: Verify User Document in MongoDB
        async def verify_user_in_mongo():
            mongo_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
            db = mongo_client["self_driving_db"]
            doc = await db["users"].find_one({"email": test_email})
            mongo_client.close()
            return doc

        print(f"\n[STEP 3] Inspecting MongoDB 'users' collection for email '{test_email}'...")
        user_doc = asyncio.run(verify_user_in_mongo())
        assert user_doc is not None, f"User document not found in MongoDB collection 'users'."
        assert user_doc["id"] == user_id, "User ID mismatch in MongoDB."
        print(" -> SUCCESS: User document verified in MongoDB collection 'users':")
        print(f"    - _id: {user_doc['_id']}")
        print(f"    - Email: {user_doc['email']}")
        print(f"    - Full Name: {user_doc['full_name']}")

        # STEP 4: Upload Real Media File
        fixture_path = os.path.join(repo_root, "tests", "fixtures", "sample_road_scene.jpg")
        assert os.path.exists(fixture_path), f"Test fixture '{fixture_path}' missing."

        print(f"\n[STEP 4] Uploading media file '{fixture_path}'...")
        with open(fixture_path, "rb") as f:
            upload_res = client.post(
                "/api/v1/media/upload",
                files={"file": ("sample_road_scene.jpg", f, "image/jpeg")},
                headers=headers,
            )
        assert upload_res.status_code == 201, f"Media upload failed: {upload_res.text}"
        media_id = upload_res.json()["id"]
        print(f" -> SUCCESS: Media uploaded (Media ID: {media_id})")

        # STEP 5: Verify Media Document in MongoDB
        async def verify_media_in_mongo():
            mongo_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
            db = mongo_client["self_driving_db"]
            doc = await db["media"].find_one({"_id": media_id})
            mongo_client.close()
            return doc

        print(f"\n[STEP 5] Inspecting MongoDB 'media' collection for Media ID '{media_id}'...")
        media_doc = asyncio.run(verify_media_in_mongo())
        assert media_doc is not None, f"Media document not found in MongoDB collection 'media'."
        assert media_doc["user_id"] == user_id, "Media user_id mismatch."
        print(" -> SUCCESS: Media document verified in MongoDB collection 'media':")
        print(f"    - _id: {media_doc['_id']}")
        print(f"    - Filename: {media_doc['filename']}")
        print(f"    - File Type: {media_doc['file_type']}")
        print(f"    - User ID: {media_doc['user_id']}")

        # STEP 6: Trigger Real Segmentation
        print(f"\n[STEP 6] Triggering scene segmentation inference...")
        seg_res = client.post(
            "/api/v1/inference/segment",
            json={"media_id": media_id},
            headers=headers,
        )
        assert seg_res.status_code == 202, f"Inference request failed: {seg_res.text}"
        task_id = seg_res.json()["task_id"]
        print(f" -> SUCCESS: Inference task created (Task ID: {task_id})")

        # STEP 7: Verify Task Document in MongoDB
        async def verify_task_in_mongo():
            mongo_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
            db = mongo_client["self_driving_db"]
            doc = await db["tasks"].find_one({"_id": task_id})
            mongo_client.close()
            return doc

        print(f"\n[STEP 7] Inspecting MongoDB 'tasks' collection for Task ID '{task_id}'...")
        task_doc = asyncio.run(verify_task_in_mongo())
        assert task_doc is not None, f"Task document not found in MongoDB collection 'tasks'."
        assert task_doc["user_id"] == user_id, "Task user_id mismatch."
        assert task_doc["media_id"] == media_id, "Task media_id mismatch."
        assert task_doc["status"] == "completed", "Task status is not 'completed'."
        print(" -> SUCCESS: Task document verified in MongoDB collection 'tasks':")
        print(f"    - _id: {task_doc['_id']}")
        print(f"    - Status: {task_doc['status']}")
        print(f"    - User ID: {task_doc['user_id']}")
        print(f"    - Media ID: {task_doc['media_id']}")
        print(f"    - Output Path: {task_doc['output_path']}")
        print(f"    - Metrics: {task_doc['metrics']}")

        # STEP 8: Verify Output JPEG on Disk
        output_path = task_doc["output_path"]
        assert os.path.exists(output_path), f"Output file '{output_path}' not found."
        with Image.open(output_path) as img:
            img.verify()
        print(f"\n[STEP 8] Output file verified with PIL:")
        print(f"    - File Size: {os.path.getsize(output_path)} bytes")

    # STEP 9: Simulate Backend Restart & Metadata Retrieval
    print("\n[STEP 9] Simulating backend restart & querying GET /api/v1/inference/tasks/{task_id}...")
    with TestClient(app) as new_client:
        get_task_res = new_client.get(f"/api/v1/inference/tasks/{task_id}", headers=headers)
        assert get_task_res.status_code == 200, f"Failed to retrieve task post-restart: {get_task_res.text}"
        retrieved_data = get_task_res.json()
        assert retrieved_data["task_id"] == task_id
        assert retrieved_data["media_id"] == media_id
        print(" -> SUCCESS: Task metadata successfully retrieved post-restart from MongoDB.")

    # STEP 10: Clean up test documents
    async def cleanup_test_docs():
        mongo_client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
        db = mongo_client["self_driving_db"]
        await db["users"].delete_one({"email": test_email})
        await db["media"].delete_one({"_id": media_id})
        await db["tasks"].delete_one({"_id": task_id})
        mongo_client.close()

    asyncio.run(cleanup_test_docs())
    print("\n[STEP 10] Cleaned up temporary MongoDB test documents.")

    print("\n" + "=" * 60)
    print(">>> ALL MONGODB PERSISTENCE VERIFICATION TESTS PASSED! <<<")
    print("=" * 60)


if __name__ == "__main__":
    run_mongodb_persistence_test()
