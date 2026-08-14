"""Storage Artifact Expiry & Retention Cleanup Worker Task (T058).

Implements background retention cleanup for job artifacts older than N days (Section 15.3 mitigation).
Supports dry-run verification mode before actual file/record deletion.
"""

from datetime import datetime, timedelta, timezone
import logging
import os
import sys
from typing import Dict, List
from app.config import settings
from app.core.celery_app import celery_app
from app.db.memory_store import _in_memory_jobs

logger = logging.getLogger("worker.app.tasks.cleanup_task")


@celery_app.task(name="tasks.cleanup_expired_artifacts_task")
def cleanup_expired_artifacts_task(
    retention_days: int = 30,
    dry_run: bool = True,
) -> Dict:
    """Scan and clean up stored artifacts and job records older than retention_days threshold (T058)."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    logger.info("[T058] Running artifact cleanup task (retention_days=%d, dry_run=%s, cutoff=%s)...", retention_days, dry_run, cutoff_date.isoformat())

    expired_job_ids: List[str] = []
    files_to_delete: List[str] = []

    for job_id, job_doc in list(_in_memory_jobs.items()):
        created_at = job_doc.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except Exception:
                created_at = None

        if created_at and created_at < cutoff_date:
            expired_job_ids.append(job_id)
            out_path = job_doc.get("output_path")
            if out_path:
                files_to_delete.append(out_path)

    deleted_files_count = 0
    deleted_records_count = 0

    if not dry_run:
        for filePath in files_to_delete:
            if os.path.exists(filePath):
                try:
                    os.remove(filePath)
                    deleted_files_count += 1
                    logger.info("[T058] Deleted expired artifact: '%s'", filePath)
                except Exception as exc:
                    logger.warning("[T058] Could not remove artifact '%s': %s", filePath, exc)

        for job_id in expired_job_ids:
            if job_id in _in_memory_jobs:
                _in_memory_jobs[job_id]["status"] = "expired"
                _in_memory_jobs[job_id]["output_path"] = None
                deleted_records_count += 1
                logger.info("[T058] Marked job '%s' as expired.", job_id)
    else:
        logger.info("[T058] [DRY RUN] Identified %d expired jobs and %d files for deletion.", len(expired_job_ids), len(files_to_delete))

    summary_payload = {
        "status": "success",
        "dry_run": dry_run,
        "retention_days": retention_days,
        "cutoff_date": cutoff_date.isoformat(),
        "expired_jobs_found": len(expired_job_ids),
        "files_deleted": deleted_files_count if not dry_run else 0,
        "jobs_updated": deleted_records_count if not dry_run else 0,
    }

    return summary_payload


__all__ = ["cleanup_expired_artifacts_task"]
