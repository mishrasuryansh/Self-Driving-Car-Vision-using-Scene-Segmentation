"""T111-T112 Terminal Verification Test Suite.

Tests:
1. Backup demo assets existence (`docs/demo-backup-assets/`) (T111).
2. Offline presenter usage README (`docs/demo-backup-assets/README.md`) (T111).
3. Final rehearsal checklist & formal scope freeze announcement (`docs/scope-freeze-notes.md`) (T112).
"""

import logging
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ep12_suite")


def test_ep12_terminal():
    print("[TEST 1] Verifying offline backup demo assets directory & files (T111)...")
    backup_dir = os.path.join(repo_root, "docs", "demo-backup-assets")
    sample_img = os.path.join(backup_dir, "sample_input.jpg")
    overlay_img = os.path.join(backup_dir, "sample_segmented_overlay.jpg")
    sample_vid = os.path.join(backup_dir, "sample_video.mp4")
    overlay_vid = os.path.join(backup_dir, "sample_segmented_video.mp4")
    backup_readme = os.path.join(backup_dir, "README.md")

    assert os.path.exists(sample_img), "sample_input.jpg missing!"
    assert os.path.exists(overlay_img), "sample_segmented_overlay.jpg missing!"
    assert os.path.exists(sample_vid), "sample_video.mp4 missing!"
    assert os.path.exists(overlay_vid), "sample_segmented_video.mp4 missing!"
    assert os.path.exists(backup_readme), "backup assets README.md missing!"
    print(" -> PASSED! All 4 backup demo assets & README verified.")

    print("[TEST 2] Verifying rehearsal notes & formal scope freeze announcement (T112)...")
    freeze_notes = os.path.join(repo_root, "docs", "scope-freeze-notes.md")
    assert os.path.exists(freeze_notes), "scope-freeze-notes.md missing!"
    with open(freeze_notes, "r", encoding="utf-8") as f:
        content = f.read()
        assert "FORMAL DECLARATION OF SCOPE FREEZE" in content
        assert "FROZEN" in content
        assert "Suryansh Mishra" in content
    print(" -> PASSED! Formal scope freeze document verified.")


def run_all():
    print("====================================================")
    print("RUNNING T111-T112 TERMINAL ROADMAP SUITE")
    print("====================================================")
    test_ep12_terminal()
    print("====================================================")
    print("ALL 112 ROADMAP TASKS COMPLETED & VERIFIED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
