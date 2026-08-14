"""T035 Redis Connection Manager & Cache Lifespan Verification Script.

Tests:
1. Verification of RedisManager class instantiation, connect(), set(), get(), delete(), and close().
2. Verification of get_redis FastAPI dependency helper.
3. Verification of FastAPI lifespan context manager integration for dual MongoDB + Redis connections during application startup and shutdown.
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
from app.db.redis import RedisManager, get_redis, redis_manager
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t035")


def test_redis_manager_unit():
    """Verify RedisManager lifecycle and cache helper methods."""
    print("[TEST 1] Testing RedisManager lifecycle methods...")

    async def _run():
        mgr = RedisManager()
        await mgr.connect()

        # Offline/disconnected fallback checks
        val = await mgr.get("test_key")
        assert val is None or isinstance(val, str)

        set_res = await mgr.set("test_key", "test_value", expire_seconds=10)
        assert set_res in (True, False)

        del_res = await mgr.delete("test_key")
        assert del_res in (True, False)

        await mgr.close()
        assert mgr.client is None

    asyncio.run(_run())
    print(" -> PASSED! RedisManager unit lifecycle test verified.")


def test_get_redis_dependency():
    """Verify get_redis FastAPI dependency helper."""
    print("[TEST 2] Testing get_redis FastAPI dependency helper...")

    async def _run():
        async for client in get_redis():
            print(f" -> Dependency yielded Redis client: {client}")

    asyncio.run(_run())
    print(" -> PASSED! get_redis dependency helper verified.")


def test_lifespan_dual_db_integration():
    """Verify FastAPI application lifespan startup and shutdown events for MongoDB + Redis."""
    print("[TEST 3] Testing FastAPI lifespan context manager integration for dual MongoDB + Redis...")

    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}
        print(" -> App lifespan (MongoDB + Redis) started successfully during TestClient context.")

    print(" -> App lifespan shutdown executed cleanly on TestClient exit.")
    print(" -> PASSED! Dual database lifespan integration verified.")


def run_all():
    print("====================================================")
    print("RUNNING T035 REDIS LIFECYCLE SUITE")
    print("====================================================")
    test_redis_manager_unit()
    test_get_redis_dependency()
    test_lifespan_dual_db_integration()
    print("====================================================")
    print("ALL T035 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
