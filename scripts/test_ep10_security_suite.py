"""EP10 Complete Security & Hardening Integration Test Suite (T100).

Tests:
1. Security response headers injection (`X-Content-Type-Options`, `X-Frame-Options`, `HSTS`) (T091).
2. Path traversal attack filename rejection (T092).
3. Cross-user resource ownership authorization check (HTTP 403 Forbidden) (T093).
4. Security audit documentation existence (`docs/security-audit-report.md`) (T098).
"""

import logging
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from tests.test_security import (
    test_path_traversal_rejection,
    test_resource_ownership_authorization,
    test_security_headers,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ep10_suite")


def test_ep10_full():
    print("[TEST 1] Testing security HTTP response headers injection (T091)...")
    test_security_headers()
    print(" -> PASSED! Security response headers verified.")

    print("[TEST 2] Testing path traversal attack rejection (T092)...")
    test_path_traversal_rejection()
    print(" -> PASSED! Path traversal rejection verified.")

    print("[TEST 3] Testing cross-user resource ownership authorization checks (T093)...")
    test_resource_ownership_authorization()
    print(" -> PASSED! Ownership authorization checks verified.")

    print("[TEST 4] Verifying security audit documentation (T098)...")
    report_path = os.path.join(repo_root, "docs", "security-audit-report.md")
    assert os.path.exists(report_path), "security-audit-report.md missing!"
    print(" -> PASSED! Security audit documentation verified.")


def run_all():
    print("====================================================")
    print("RUNNING T091-T100 COMPLETE EP10 SECURITY SUITE")
    print("====================================================")
    test_ep10_full()
    print("====================================================")
    print("ALL T091-T100 SECURITY TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
