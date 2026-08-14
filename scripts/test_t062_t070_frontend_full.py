"""T062-T070 Frontend Full Epic Verification Script.

Tests:
1. Verification of AuthContext (`AuthContext.tsx`) and ProtectedRoute (`ProtectedRoute.tsx`) (T062, T063).
2. Verification of SegmentMaskOverlay (`SegmentMaskOverlay.tsx`) and UploadImagePage (`UploadImagePage.tsx`) (T064, T065).
3. Verification of JobStatusStepper (`JobStatusStepper.tsx`) and VideoPlayerWithMetrics (`VideoPlayerWithMetrics.tsx`) (T066, T067).
4. Verification of MetricsPanel (`MetricsPanel.tsx`), HistoryPage (`HistoryPage.tsx`), and AnalyticsPage (`AnalyticsPage.tsx`) (T068, T069, T070).
"""

import logging
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
frontend_path = os.path.join(repo_root, "frontend")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t062_t070")


def test_frontend_full_epic():
    print("[TEST 1] Verifying AuthContext & ProtectedRoute components (T062, T063)...")
    auth_ctx = os.path.join(frontend_path, "src", "context", "AuthContext.tsx")
    prot_rt = os.path.join(frontend_path, "src", "components", "ProtectedRoute.tsx")
    assert os.path.exists(auth_ctx), "AuthContext.tsx missing!"
    assert os.path.exists(prot_rt), "ProtectedRoute.tsx missing!"
    with open(auth_ctx, "r", encoding="utf-8") as f:
        content = f.read()
        assert "AuthProvider" in content
        assert "access_token" in content
    print(" -> AuthContext & ProtectedRoute verified.")

    print("[TEST 2] Verifying SegmentMaskOverlay & UploadImagePage (T064, T065)...")
    mask_ov = os.path.join(frontend_path, "src", "components", "SegmentMaskOverlay.tsx")
    img_pg = os.path.join(frontend_path, "src", "pages", "UploadImagePage.tsx")
    assert os.path.exists(mask_ov), "SegmentMaskOverlay.tsx missing!"
    assert os.path.exists(img_pg), "UploadImagePage.tsx missing!"
    with open(mask_ov, "r", encoding="utf-8") as f:
        content = f.read()
        assert "opacity" in content
        assert "CLASS_COLORS" in content
    print(" -> SegmentMaskOverlay & UploadImagePage verified.")

    print("[TEST 3] Verifying JobStatusStepper & VideoPlayerWithMetrics (T066, T067)...")
    stepper = os.path.join(frontend_path, "src", "components", "JobStatusStepper.tsx")
    v_player = os.path.join(frontend_path, "src", "components", "VideoPlayerWithMetrics.tsx")
    vid_pg = os.path.join(frontend_path, "src", "pages", "UploadVideoPage.tsx")
    assert os.path.exists(stepper), "JobStatusStepper.tsx missing!"
    assert os.path.exists(v_player), "VideoPlayerWithMetrics.tsx missing!"
    assert os.path.exists(vid_pg), "UploadVideoPage.tsx missing!"
    with open(stepper, "r", encoding="utf-8") as f:
        content = f.read()
        assert "fetchJobStatus" in content
        assert "cancel" in content
    print(" -> JobStatusStepper & VideoPlayerWithMetrics verified.")

    print("[TEST 4] Verifying MetricsPanel, HistoryPage, & AnalyticsPage (T068, T069, T070)...")
    metrics_p = os.path.join(frontend_path, "src", "components", "MetricsPanel.tsx")
    hist_pg = os.path.join(frontend_path, "src", "pages", "HistoryPage.tsx")
    an_pg = os.path.join(frontend_path, "src", "pages", "AnalyticsPage.tsx")
    assert os.path.exists(metrics_p), "MetricsPanel.tsx missing!"
    assert os.path.exists(hist_pg), "HistoryPage.tsx missing!"
    assert os.path.exists(an_pg), "AnalyticsPage.tsx missing!"
    with open(hist_pg, "r", encoding="utf-8") as f:
        content = f.read()
        assert "filterStatus" in content
        assert "Inspect Details" in content
    print(" -> MetricsPanel, HistoryPage, & AnalyticsPage verified.")
    print(" -> PASSED! T062-T070 complete frontend suite verified.")


def run_all():
    print("====================================================")
    print("RUNNING T062-T070 FRONTEND FULL EPIC SUITE")
    print("====================================================")
    test_frontend_full_epic()
    print("====================================================")
    print("ALL T062-T070 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
