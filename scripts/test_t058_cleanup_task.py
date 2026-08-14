"""T058 Storage Artifact Expiry Cleanup Verification Script.

Tests:
1. Dry-run mode (`dry_run=True`) ensuring candidate records are logged without deleting files.
2. Live mode (`dry_run=False`) verifying file deletion and job status updating to "expired".
3. Idempotency test (running task twice on already cleaned records).
"""

from datetime import datetime, timedelta, timezone
import logging
import os
import sys

# Ensure repository root and backend directory are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
worker_path = os.path.join(repo_root, "worker")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if worker_path not in sys.path:
    sys.path.insert(0, worker_path)

from app.db.memory_store import _in_memory_jobs
from worker.app.tasks.cleanup_task import cleanup_expired_artifacts_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t058")


def test_cleanup_task():
    print("[TEST 1] Seeding old and recent job records with dummy files...")
    now = datetime.now(timezone.utc)
    old_date = now - timedelta(days=45)

    old_file_path = os.path.normpath("storage/outputs/old_expired_file.mp4")
    new_file_path = os.path.normpath("storage/outputs/new_recent_file.mp4")

    os.makedirs(os.path.dirname(old_file_path), exist_ok=True)
    with open(old_file_path, "wb") as f:
        f.write(b"OLD_EXPIRED_FILE_CONTENT")
    with open(new_file_path, "wb") as f:
        f.write(b"NEW_RECENT_FILE_CONTENT")

    _in_memory_jobs["job_old_111"] = {
        "_id": "job_old_111",
        "job_id": "job_old_111",
        "status": "completed",
        "output_path": old_file_path,
        "created_at": old_date,
    }

    _in_memory_jobs["job_new_222"] = {
        "_id": "job_new_222",
        "job_id": "job_new_222",
        "status": "completed",
        "output_path": new_file_path,
        "created_at": now,
    }

    print("[TEST 2] Running cleanup task in DRY-RUN mode (dry_run=True)...")
    dry_res = cleanup_expired_artifacts_task(retention_days=30, dry_run=True)
    assert dry_res["dry_run"] is True
    assert dry_res["expired_jobs_found"] == 1
    assert dry_res["files_deleted"] == 0
    assert os.path.exists(old_file_path), "File should NOT be deleted during dry-run!"
    print(f" -> Dry Run Result: {dry_res}")
    print(" -> PASSED! Dry-run mode verified.")

    print("[TEST 3] Running cleanup task in LIVE mode (dry_run=False)...")
    live_res = cleanup_expired_artifacts_task(retention_days=30, dry_run=False)
    assert live_res["dry_run"] is False
    assert live_res["files_deleted"] == 1
    assert live_res["jobs_updated"] == 1
    assert not os.path.exists(old_file_path), "Old file SHOULD be deleted in live run!"
    assert os.path.exists(new_file_path), "Recent file SHOULD NOT be deleted!"
    assert _in_memory_jobs["job_old_111"]["status"] == "expired"
    print(f" -> Live Run Result: {live_res}")
    print(" -> PASSED! Live run mode & file deletion verified.")

    print("[TEST 4] Testing idempotency (running cleanup again)...")
    repeat_res = cleanup_expired_artifacts_task(retention_days=30, dry_run=False)
    assert repeat_res["files_deleted"] == 0
    print(" -> PASSED! Idempotency verified.")


def run_all():
    print("====================================================")
    print("RUNNING T058 STORAGE CLEANUP TASK SUITE")
    print("====================================================")
    test_cleanup_task()
    print("====================================================")
    print("ALL T058 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
