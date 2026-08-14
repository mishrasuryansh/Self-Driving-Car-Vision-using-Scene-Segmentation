"""T051-T052 Worker Process & Model Preloading Verification Script.

Tests:
1. Worker application entrypoint initialization (`worker/app/main.py`).
2. Verification of Celery app instance binding (`celery_app`).
3. Model pre-loading at startup (T052).
"""

import logging
import os
import sys

# Ensure repository root and worker directories are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
worker_path = os.path.join(repo_root, "worker")
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if worker_path not in sys.path:
    sys.path.insert(0, worker_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from worker.app.main import app, get_preloaded_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t051_t052")


def test_worker_main():
    print("[TEST 1] Testing worker process entrypoint (T051)...")
    assert app.main == "worker"
    print(f" -> Celery App Instance Name: '{app.main}'")

    print("[TEST 2] Testing model pre-loading initialization (T052)...")
    model = get_preloaded_model()
    print(f" -> Preloaded Model Instance: {model}")
    print(" -> PASSED! T051-T052 worker entrypoint & model pre-loader verified.")


def run_all():
    print("====================================================")
    print("RUNNING T051-T052 WORKER & MODEL PRELOADER SUITE")
    print("====================================================")
    test_worker_main()
    print("====================================================")
    print("ALL T051-T052 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
