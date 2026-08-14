"""Job Status Query & Management Endpoints.

Provides HTTP endpoints for querying asynchronous job status (`GET /api/v1/jobs/{job_id}`),
listing user jobs (`GET /api/v1/jobs`), and cancelling active processing jobs (`POST /api/v1/jobs/{job_id}/cancel`).
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_active_user
from app.core.celery_app import celery_app
from app.db.memory_store import _in_memory_jobs, _in_memory_tasks
from app.db.mongodb import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models.inference import TaskMetrics
from app.models.job import JobResponse
from app.models.user import UserInDB

logger = logging.getLogger("app.api.v1.endpoints.jobs")
router = APIRouter()


def _format_job_response(doc: dict) -> JobResponse:
    """Format MongoDB/dictionary record into typed JobResponse Pydantic model."""
    job_id = str(doc.get("_id") or doc.get("job_id") or doc.get("task_id"))
    metrics_raw = doc.get("metrics")
    metrics_obj = None
    if metrics_raw and isinstance(metrics_raw, dict):
        metrics_obj = TaskMetrics(
            fps=float(metrics_raw.get("fps", 30.0)),
            avgInferenceMs=float(metrics_raw.get("avgInferenceMs", 33.33)),
            classDistribution=metrics_raw.get("classDistribution", {}),
        )

    created = doc.get("created_at") or datetime.now(timezone.utc)
    updated = doc.get("updated_at") or created

    return JobResponse(
        job_id=job_id,
        user_id=str(doc.get("user_id", "default_user")),
        media_id=str(doc.get("media_id", "")),
        status=doc.get("status", "completed"),
        progress_percent=float(doc.get("progress_percent", 100.0)),
        output_media_id=doc.get("output_media_id"),
        output_path=doc.get("output_path"),
        metrics=metrics_obj,
        error=doc.get("error"),
        created_at=created,
        updated_at=updated,
    )


@router.get(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=JobResponse,
    summary="Get asynchronous job status and metrics",
)
async def get_job_status(
    job_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> JobResponse:
    """Retrieve job status, progress percentage, output path, and Section 8.2 performance metrics by job ID."""
    doc = None
    if db is not None:
        try:
            doc = await db["jobs"].find_one({"_id": job_id})
            if not doc:
                doc = await db["tasks"].find_one({"_id": job_id})
        except Exception as exc:
            logger.warning("MongoDB lookup failed for job '%s': %s", job_id, exc)
            doc = _in_memory_jobs.get(job_id) or _in_memory_tasks.get(job_id)
    else:
        doc = _in_memory_jobs.get(job_id) or _in_memory_tasks.get(job_id)

    if not doc:
        raise NotFoundException(message=f"Job #{job_id} not found.")

    return _format_job_response(doc)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[JobResponse],
    summary="List all jobs for current user",
)
async def list_user_jobs(
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> List[JobResponse]:
    """Retrieve list of all processing jobs created by the current authenticated user."""
    results = []
    if db is not None:
        try:
            cursor = db["jobs"].find({"user_id": current_user.id})
            async for doc in cursor:
                results.append(_format_job_response(doc))
        except Exception as exc:
            logger.warning("MongoDB query failed for user jobs: %s", exc)
            for jid, doc in _in_memory_jobs.items():
                if doc.get("user_id") == current_user.id:
                    results.append(_format_job_response(doc))
    else:
        for jid, doc in _in_memory_jobs.items():
            if doc.get("user_id") == current_user.id:
                results.append(_format_job_response(doc))

    return results


@router.post(
    "/{job_id}/cancel",
    status_code=status.HTTP_200_OK,
    response_model=JobResponse,
    summary="Cancel active processing job",
)
async def cancel_job(
    job_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> JobResponse:
    """Revoke active Celery task execution and update job status to cancelled."""
    # Revoke Celery task
    try:
        celery_app.control.revoke(job_id, terminate=True)
        logger.info("Revoked Celery task '%s'", job_id)
    except Exception as exc:
        logger.warning("Could not revoke Celery task '%s': %s", job_id, exc)

    now = datetime.now(timezone.utc)
    doc = None
    if db is not None:
        try:
            doc = await db["jobs"].find_one_and_update(
                {"_id": job_id},
                {"$set": {"status": "cancelled", "updated_at": now}},
                return_document=True,
            )
        except Exception as exc:
            logger.warning("MongoDB update failed during job cancel: %s", exc)
            if job_id in _in_memory_jobs:
                _in_memory_jobs[job_id]["status"] = "cancelled"
                _in_memory_jobs[job_id]["updated_at"] = now
                doc = _in_memory_jobs[job_id]
    else:
        if job_id in _in_memory_jobs:
            _in_memory_jobs[job_id]["status"] = "cancelled"
            _in_memory_jobs[job_id]["updated_at"] = now
            doc = _in_memory_jobs[job_id]

    if not doc:
        # Create cancelled record if missing
        doc = {
            "_id": job_id,
            "job_id": job_id,
            "user_id": current_user.id,
            "status": "cancelled",
            "progress_percent": 0.0,
            "created_at": now,
            "updated_at": now,
        }
        _in_memory_jobs[job_id] = doc

    return _format_job_response(doc)


__all__ = ["router", "_in_memory_jobs"]
