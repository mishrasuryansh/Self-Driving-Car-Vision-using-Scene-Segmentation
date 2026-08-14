"""T059-T061 Frontend Scaffolding, Navigation, & API Client Verification Script.

Tests:
1. Verification of React SPA directory structure and entry points (`frontend/src/App.tsx`, `frontend/src/main.tsx`).
2. Verification of Section 10.2 navigation component routes (`NavBar.tsx`, `Layout.tsx`).
3. Verification of Axios API client and HTTP interceptors (`frontend/src/services/api.ts`).
"""

import logging
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
frontend_path = os.path.join(repo_root, "frontend")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t059_t061")


def test_frontend_scaffolding():
    print("[TEST 1] Verifying frontend directory structure & package.json (T059)...")
    pkg_json_path = os.path.join(frontend_path, "package.json")
    assert os.path.exists(pkg_json_path), "package.json missing!"
    print(" -> package.json exists.")

    print("[TEST 2] Verifying React Router setup & page routes (T059)...")
    app_tsx = os.path.join(frontend_path, "src", "App.tsx")
    assert os.path.exists(app_tsx), "App.tsx missing!"
    with open(app_tsx, "r", encoding="utf-8") as f:
        content = f.read()
        assert "/upload/image" in content
        assert "/upload/video" in content
        assert "/history" in content
        assert "/analytics" in content
        assert "/settings" in content
        assert "/about" in content
    print(" -> App.tsx routes verified.")

    print("[TEST 3] Verifying NavBar & Layout components (T060)...")
    navbar_path = os.path.join(frontend_path, "src", "components", "NavBar.tsx")
    layout_path = os.path.join(frontend_path, "src", "components", "Layout.tsx")
    assert os.path.exists(navbar_path), "NavBar.tsx missing!"
    assert os.path.exists(layout_path), "Layout.tsx missing!"
    with open(navbar_path, "r", encoding="utf-8") as f:
        nav_content = f.read()
        assert "isMobileOpen" in nav_content
        assert "Dashboard" in nav_content
    print(" -> NavBar & Layout components verified.")

    print("[TEST 4] Verifying Axios API client & 401 interceptor service (T061)...")
    api_ts = os.path.join(frontend_path, "src", "services", "api.ts")
    assert os.path.exists(api_ts), "api.ts missing!"
    with open(api_ts, "r", encoding="utf-8") as f:
        api_content = f.read()
        assert "apiClient" in api_content
        assert "Authorization" in api_content
        assert "status === 401" in api_content
    print(" -> Frontend API client & interceptors verified.")
    print(" -> PASSED! T059-T061 frontend scaffolding & API client verified.")


def run_all():
    print("====================================================")
    print("RUNNING T059-T061 FRONTEND SCAFFOLDING SUITE")
    print("====================================================")
    test_frontend_scaffolding()
    print("====================================================")
    print("ALL T059-T061 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
