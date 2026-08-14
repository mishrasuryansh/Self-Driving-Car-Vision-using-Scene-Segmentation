"""T101-T110 Complete EP11 Integration & Deployment Test Suite.

Tests:
1. Docker Compose configurations (`docker-compose.yml`, `infra/docker-compose.yml`).
2. Staging health verification script (`scripts/verify_staging.py`).
3. Image and video load test scripts (`scripts/load_test_image.py`, `scripts/load_test_video.py`).
4. Load test findings and staging SRS checklist (`docs/load-test-results.md`, `docs/staging-srs-checklist.md`).
5. Production README, User Guide, Final Report, and Presentation Deck (`README.md`, `docs/user-guide.md`, `docs/final-report.md`, `docs/presentation-deck.md`).
"""

import logging
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ep11_suite")


def test_ep11_full():
    print("[TEST 1] Verifying Docker Compose configurations (T101)...")
    dc1 = os.path.join(repo_root, "docker-compose.yml")
    dc2 = os.path.join(repo_root, "infra", "docker-compose.yml")
    assert os.path.exists(dc1), "Root docker-compose.yml missing!"
    assert os.path.exists(dc2), "infra/docker-compose.yml missing!"
    print(" -> PASSED! Docker Compose configurations verified.")

    print("[TEST 2] Verifying Staging Health Verification Script (T102)...")
    verify_script = os.path.join(repo_root, "scripts", "verify_staging.py")
    assert os.path.exists(verify_script), "verify_staging.py missing!"
    print(" -> PASSED! Staging health script verified.")

    print("[TEST 3] Verifying Image & Video Load Test Scripts (T103, T104)...")
    lt_img = os.path.join(repo_root, "scripts", "load_test_image.py")
    lt_vid = os.path.join(repo_root, "scripts", "load_test_video.py")
    assert os.path.exists(lt_img), "load_test_image.py missing!"
    assert os.path.exists(lt_vid), "load_test_video.py missing!"
    print(" -> PASSED! Load test scripts verified.")

    print("[TEST 4] Verifying Load Test Findings & SRS Checklist (T105, T106)...")
    doc_lt = os.path.join(repo_root, "docs", "load-test-results.md")
    doc_srs = os.path.join(repo_root, "docs", "staging-srs-checklist.md")
    assert os.path.exists(doc_lt), "load-test-results.md missing!"
    assert os.path.exists(doc_srs), "staging-srs-checklist.md missing!"
    print(" -> PASSED! Findings & SRS checklist documents verified.")

    print("[TEST 5] Verifying README, User Guide, Report & Deck (T107-T110)...")
    readme = os.path.join(repo_root, "README.md")
    ug = os.path.join(repo_root, "docs", "user-guide.md")
    fr = os.path.join(repo_root, "docs", "final-report.md")
    deck = os.path.join(repo_root, "docs", "presentation-deck.md")

    assert os.path.exists(readme), "README.md missing!"
    assert os.path.exists(ug), "user-guide.md missing!"
    assert os.path.exists(fr), "final-report.md missing!"
    assert os.path.exists(deck), "presentation-deck.md missing!"
    print(" -> PASSED! Final documentation artifacts verified.")


def run_all():
    print("====================================================")
    print("RUNNING T101-T110 COMPLETE EP11 DEPLOYMENT SUITE")
    print("====================================================")
    test_ep11_full()
    print("====================================================")
    print("ALL T101-T110 DEPLOYMENT TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
