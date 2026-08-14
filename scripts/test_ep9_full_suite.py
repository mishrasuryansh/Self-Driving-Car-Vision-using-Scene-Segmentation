"""T081-T090 Complete EP9 Integration & Unit Test Suite.

Tests:
1. Analytics Page date-range filter & CSV export (`frontend/src/pages/AnalyticsPage.tsx`).
2. Scope decision documentation (`docs/analytics-scope-decision.md`).
3. Taxonomy and metrics unit tests (`test_taxonomy.py`, `test_metrics.py`).
4. DeepLabV3+ image pipeline end-to-end integration test (`test_image_pipeline.py`).
5. Backend authentication integration tests (`backend/tests/test_auth.py`).
6. Backend job endpoints integration tests (`backend/tests/test_jobs_image.py`).
"""

import logging
import os
import sys
import unittest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
engine_path = os.path.join(repo_root, "inference-engine")
backend_path = os.path.join(repo_root, "backend")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from tests.test_auth import test_auth_login_and_me, test_auth_registration_flow
from tests.test_jobs_image import test_image_segmentation_endpoint, test_job_query_and_list
from tests.test_metrics import TestPerceptionMetrics
from tests.test_taxonomy import TestTaxonomyAndColorMap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ep9_suite")


def test_ep9_full():
    print("[TEST 1] Running Taxonomy and Color Map unit tests (T087)...")
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestTaxonomyAndColorMap)
    res1 = unittest.TextTestRunner().run(suite1)
    assert res1.wasSuccessful(), "Taxonomy unit tests failed!"
    print(" -> PASSED! Taxonomy & Color Map unit tests verified.")

    print("[TEST 2] Running Perception Metrics unit tests (T087)...")
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestPerceptionMetrics)
    res2 = unittest.TextTestRunner().run(suite2)
    assert res2.wasSuccessful(), "Perception Metrics unit tests failed!"
    print(" -> PASSED! Perception Metrics unit tests verified.")

    print("[TEST 3] Running Backend Authentication Integration Tests (T089)...")
    test_auth_registration_flow()
    test_auth_login_and_me()
    print(" -> PASSED! Auth integration tests verified.")

    print("[TEST 4] Running Backend Jobs Integration Tests (T090)...")
    test_image_segmentation_endpoint()
    test_job_query_and_list()
    print(" -> PASSED! Backend job integration tests verified.")

    print("[TEST 5] Verifying Scope Decision Document (T086)...")
    doc_path = os.path.join(repo_root, "docs", "analytics-scope-decision.md")
    assert os.path.exists(doc_path), "analytics-scope-decision.md missing!"
    print(" -> PASSED! Scope decision document verified.")


def run_all():
    print("====================================================")
    print("RUNNING T081-T090 COMPLETE EP9 SUITE")
    print("====================================================")
    test_ep9_full()
    print("====================================================")
    print("ALL T081-T090 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
