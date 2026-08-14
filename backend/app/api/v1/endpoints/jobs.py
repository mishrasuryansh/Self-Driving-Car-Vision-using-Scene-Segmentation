"""Job Status Query & Management Endpoints (T092, T093).

Provides HTTP endpoints for querying asynchronous job status (`GET /api/v1/jobs/{job_id}`),
listing user jobs (`GET /api/v1/jobs`), and cancelling active processing jobs (`POST /api/v1/jobs/{job_id}/cancel`)
with input path traversal guards (T092) and resource ownership validation (T093).
"""

from datetime import datetime, timezone
import json
import logging
import os
from typing import Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.api.deps import get_current_active_user
from app.config import settings
from app.core.celery_app import celery_app
from app.db.memory_store import _in_memory_jobs, _in_memory_tasks
from app.db.mongodb import get_db
from app.db.redis import get_redis
from app.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.inference import TaskMetrics
from app.models.job import JobResponse
from app.models.user import UserInDB
from app.tasks.video_tasks import process_video_task

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


@router.post(
    "/video",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobResponse,
    summary="Submit video for asynchronous scene segmentation (T092)",
)
async def submit_video_job(
    file: UploadFile = File(...),
    model_id: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> JobResponse:
    """Validate video file upload, check for path traversal attacks, create 'queued' job record, and dispatch Celery task (T092)."""
    filename = file.filename or "video.mp4"

    # Path traversal check (T092)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise BadRequestException(message="Invalid filename: path traversal sequences are not allowed.")

    mime_type = (file.content_type or "").lower().strip()

    if not filename.lower().endswith((".mp4", ".avi", ".mov")) and not mime_type.startswith("video/"):
        raise BadRequestException(message="Unsupported file type. Only MP4, AVI, and MOV video files are allowed.")

    contents = await file.read()
    size_bytes = len(contents)
    max_video_bytes = 200 * 1024 * 1024  # 200 MB limit

    if size_bytes > max_video_bytes:
        raise BadRequestException(
            message=f"Video size ({size_bytes / 1024 / 1024:.2f} MB) exceeds maximum allowed limit of 200 MB."
        )

    media_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = ".mp4"

    saved_filename = f"{media_id}{ext}"
    upload_dir = settings.STORAGE_UPLOADS_PATH
    if upload_dir.startswith("/app/"):
        upload_dir = upload_dir.replace("/app/", "", 1)
    dest_path = os.path.normpath(os.path.join(upload_dir, saved_filename))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as f:
        f.write(contents)

    now = datetime.now(timezone.utc)
    job_doc = {
        "_id": job_id,
        "job_id": job_id,
        "media_id": media_id,
        "user_id": current_user.id,
        "status": "queued",
        "progress_percent": 0.0,
        "output_path": None,
        "metrics": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }

    if db is not None:
        try:
            await db["jobs"].insert_one(job_doc)
        except Exception as exc:
            logger.warning("MongoDB insert_one failed for video job: %s", exc)
            _in_memory_jobs[job_id] = job_doc
    else:
        _in_memory_jobs[job_id] = job_doc

    # Enqueue Celery worker task
    try:
        process_video_task.delay(
            job_id=job_id,
            media_id=media_id,
            video_path=dest_path,
            user_id=current_user.id,
        )
        logger.info("Enqueued Celery video task '%s'", job_id)
    except Exception as exc:
        logger.warning("Could not dispatch Celery task '%s' (%s). Operating in local fallback mode.", job_id, exc)

    return _format_job_response(job_doc)


@router.get(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=JobResponse,
    summary="Get asynchronous job status and metrics (T093)",
)
async def get_job_status(
    job_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
    redis=Depends(get_redis),
) -> JobResponse:
    """Retrieve job status, progress, and performance metrics by job ID with resource ownership verification (T093)."""
    cache_key = f"job:{job_id}"

    # Try Redis cache first
    if redis is not None:
        try:
            cached_str = await redis.get(cache_key)
            if cached_str:
                cached_data = json.loads(cached_str)
                # Ownership check on cached item (T093)
                if cached_data.get("user_id") and cached_data["user_id"] != current_user.id:
                    raise ForbiddenException(message="Access denied: you do not own this job resource.")
                return _format_job_response(cached_data)
        except ForbiddenException:
            raise
        except Exception as exc:
            logger.warning("Redis cache read failed for key '%s': %s", cache_key, exc)

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

    # Ownership check (T093)
    if doc.get("user_id") and doc["user_id"] != current_user.id:
        raise ForbiddenException(message="Access denied: you do not own this job resource.")

    formatted_res = _format_job_response(doc)

    # Store in Redis cache for 60 seconds
    if redis is not None:
        try:
            await redis.set(cache_key, formatted_res.model_dump_json(), ex=60)
        except Exception as exc:
            logger.warning("Redis cache write failed for key '%s': %s", cache_key, exc)

    return formatted_res


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[JobResponse],
    summary="List all jobs for current user (T093)",
)
async def list_user_jobs(
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> List[JobResponse]:
    """Retrieve list of all processing jobs created by the current authenticated user (T093)."""
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
    summary="Cancel active processing job (T093)",
)
async def cancel_job(
    job_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> JobResponse:
    """Revoke active Celery task execution with ownership authorization verification (T093)."""
    doc = None
    if db is not None:
        try:
            doc = await db["jobs"].find_one({"_id": job_id})
        except Exception as exc:
            logger.warning("MongoDB lookup failed for cancel job '%s': %s", job_id, exc)
            doc = _in_memory_jobs.get(job_id)
    else:
        doc = _in_memory_jobs.get(job_id)

    # Ownership check (T093)
    if doc and doc.get("user_id") and doc["user_id"] != current_user.id:
        raise ForbiddenException(message="Access denied: you do not own this job resource.")

    # Revoke Celery task
    try:
        celery_app.control.revoke(job_id, terminate=True)
        logger.info("Revoked Celery task '%s'", job_id)
    except Exception as exc:
        logger.warning("Could not revoke Celery task '%s': %s", job_id, exc)

    now = datetime.now(timezone.utc)
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
