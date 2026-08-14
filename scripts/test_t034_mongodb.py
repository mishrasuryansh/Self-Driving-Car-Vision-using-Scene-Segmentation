"""T034 MongoDB Connection Manager & Lifespan Context Verification Script.

Tests:
1. Verification of MongoDBManager class instantiation, connect(), get_database(), and close().
2. Verification of get_db FastAPI dependency helper.
3. Verification of FastAPI lifespan context manager integration during application startup and shutdown.
"""

import asyncio
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
from app.db.mongodb import MongoDBManager, get_db, mongodb_manager
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t034")


def test_mongodb_manager_unit():
    """Verify MongoDBManager lifecycle methods."""
    print("[TEST 1] Testing MongoDBManager lifecycle methods...")

    async def _run():
        mgr = MongoDBManager()
        await mgr.connect()
        db = mgr.get_database()
        print(f" -> Database handle retrieved: {db}")
        await mgr.close()
        assert mgr.client is None
        assert mgr.db is None

    asyncio.run(_run())
    print(" -> PASSED! MongoDBManager unit lifecycle test verified.")


def test_get_db_dependency():
    """Verify get_db dependency function generator."""
    print("[TEST 2] Testing get_db FastAPI dependency helper...")

    async def _run():
        async for db in get_db():
            print(f" -> Dependency yielded database: {db}")

    asyncio.run(_run())
    print(" -> PASSED! get_db dependency helper verified.")


def test_lifespan_integration():
    """Verify FastAPI application lifespan startup and shutdown events."""
    print("[TEST 3] Testing FastAPI lifespan context manager integration...")

    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}
        print(" -> App lifespan started successfully during TestClient context.")

    print(" -> App lifespan shutdown executed cleanly on TestClient exit.")
    print(" -> PASSED! FastAPI lifespan integration verified.")


def run_all():
    print("====================================================")
    print("RUNNING T034 MONGODB LIFECYCLE SUITE")
    print("====================================================")
    test_mongodb_manager_unit()
    test_get_db_dependency()
    test_lifespan_integration()
    print("====================================================")
    print("ALL T034 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
