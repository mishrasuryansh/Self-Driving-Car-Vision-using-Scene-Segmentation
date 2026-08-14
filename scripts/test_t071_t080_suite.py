"""T071-T080 Verification Test Suite.

Tests:
1. ResultViewer & UI components (`frontend/src/components/ResultViewer.tsx`, `Toast.tsx`, `Spinner.tsx`, `ErrorBanner.tsx`).
2. Settings & About pages (`frontend/src/pages/SettingsPage.tsx`, `AboutPage.tsx`).
3. Backend `GET /api/v1/analytics/summary` endpoint (T079).
4. Worker daily analytics rollup task `aggregate_daily_analytics_task` (T080).
5. Smoke test document existence (`docs/frontend-smoke-test.md`).
"""

import logging
import os
import sys

# Ensure repository root and backend/worker directories are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
worker_path = os.path.join(repo_root, "worker")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if worker_path not in sys.path:
    sys.path.insert(0, worker_path)

from fastapi.testclient import TestClient
from app.main import app
from worker.app.tasks.analytics_rollup import aggregate_daily_analytics_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t071_t080")


def test_ep8_suite():
    print("[TEST 1] Verifying frontend components & UI primitives (T071, T075)...")
    res_viewer = os.path.join(repo_root, "frontend", "src", "components", "ResultViewer.tsx")
    toast_path = os.path.join(repo_root, "frontend", "src", "components", "Toast.tsx")
    spinner_path = os.path.join(repo_root, "frontend", "src", "components", "Spinner.tsx")
    error_path = os.path.join(repo_root, "frontend", "src", "components", "ErrorBanner.tsx")

    assert os.path.exists(res_viewer), "ResultViewer.tsx missing!"
    assert os.path.exists(toast_path), "Toast.tsx missing!"
    assert os.path.exists(spinner_path), "Spinner.tsx missing!"
    assert os.path.exists(error_path), "ErrorBanner.tsx missing!"
    print(" -> Frontend components & UI primitives verified.")

    print("[TEST 2] Verifying Settings & About pages (T072, T073)...")
    settings_pg = os.path.join(repo_root, "frontend", "src", "pages", "SettingsPage.tsx")
    about_pg = os.path.join(repo_root, "frontend", "src", "pages", "AboutPage.tsx")
    assert os.path.exists(settings_pg), "SettingsPage.tsx missing!"
    assert os.path.exists(about_pg), "AboutPage.tsx missing!"
    with open(about_pg, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Suryansh Mishra" in content
        assert "PSIT" in content
    print(" -> Settings & About pages verified.")

    print("[TEST 3] Testing backend GET /api/v1/analytics/summary endpoint (T079)...")
    client = TestClient(app)

    reg_payload = {
        "email": "analytics_test@selfdriving.com",
        "password": "ValidPassword987!",
        "full_name": "Analytics Tester",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "analytics_test@selfdriving.com", "password": "ValidPassword987!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    an_resp = client.get("/api/v1/analytics/summary", headers=headers)
    assert an_resp.status_code == 200
    an_json = an_resp.json()
    assert "totalJobs" in an_json
    assert "avgInferenceMs" in an_json
    assert "jobsOverTime" in an_json
    print(f" -> Analytics Summary Response: {an_json}")
    print(" -> PASSED! GET /api/v1/analytics/summary verified.")

    print("[TEST 4] Testing worker daily analytics rollup task (T080)...")
    rollup_res = aggregate_daily_analytics_task()
    assert rollup_res["status"] == "success"
    assert "users_processed" in rollup_res
    print(f" -> Analytics Rollup Result: {rollup_res}")
    print(" -> PASSED! Worker analytics rollup task verified.")

    print("[TEST 5] Verifying smoke test document (T078)...")
    smoke_doc = os.path.join(repo_root, "docs", "frontend-smoke-test.md")
    assert os.path.exists(smoke_doc), "frontend-smoke-test.md missing!"
    print(" -> Smoke test documentation verified.")


def run_all():
    print("====================================================")
    print("RUNNING T071-T080 SUITE")
    print("====================================================")
    test_ep8_suite()
    print("====================================================")
    print("ALL T071-T080 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
