"""Scene Segmentation Inference & Task Status Endpoints.

Provides endpoints for triggering AI scene segmentation jobs (`POST /api/v1/inference/segment`)
and querying task execution status/metrics (`GET /api/v1/inference/tasks/{task_id}`).
"""

from datetime import datetime, timezone
import logging
import os
import sys
import time
from typing import Dict
import uuid
from fastapi import APIRouter, Depends, status
from PIL import Image

from app.api.deps import get_current_active_user
from app.config import settings
from app.db.memory_store import _in_memory_media, _in_memory_tasks
from app.db.mongodb import get_db
from app.exceptions import BadRequestException, NotFoundException, InternalServerErrorException
from app.models.inference import InferenceRequest, InferenceResponse, TaskMetrics, TaskStatusResponse
from app.models.user import UserInDB

# Ensure inference engine is in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
engine_path = os.path.join(repo_root, "inference-engine")
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

try:
    from pipeline import DeepLabV3Backend, process_single_image
except ImportError:
    DeepLabV3Backend = None
    process_single_image = None

logger = logging.getLogger("app.api.v1.endpoints.inference")
router = APIRouter()

# Shared model backend cache
_model_backend_cache = None


def _get_shared_backend():
    global _model_backend_cache
    if _model_backend_cache is None and DeepLabV3Backend is not None:
        try:
            _model_backend_cache = DeepLabV3Backend(
                weights_path=settings.MODEL_WEIGHTS_PATH if settings.MODEL_WEIGHTS_PATH else None,
                device=settings.MODEL_DEVICE,
            )
            _model_backend_cache.load_model()
        except Exception as exc:
            logger.error("Could not instantiate DeepLabV3Backend: %s", exc)
            raise InternalServerErrorException(message=f"Failed to load AI perception model: {str(exc)}")
    return _model_backend_cache


@router.post(
    "/segment",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=InferenceResponse,
    summary="Trigger scene segmentation inference job",
)
async def trigger_segmentation(
    request_in: InferenceRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> InferenceResponse:
    """Trigger scene segmentation on uploaded media item and execute AI pipeline processing."""
    media_id = request_in.media_id

    # Retrieve media metadata
    media_doc = None
    if db is not None:
        try:
            media_doc = await db["media"].find_one({"_id": media_id})
        except Exception as exc:
            logger.warning("MongoDB find_one failed for media_id '%s': %s", media_id, exc)
            media_doc = _in_memory_media.get(media_id)
    else:
        media_doc = _in_memory_media.get(media_id)

    if not media_doc:
        raise NotFoundException(message=f"Media item #{media_id} not found.")

    input_path = media_doc.get("file_path", "")
    file_type = media_doc.get("file_type", "image")

    if not os.path.exists(input_path):
        raise NotFoundException(message=f"Source media file '{input_path}' not found on disk.")

    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Determine output path
    _, ext = os.path.splitext(input_path)
    if not ext:
        ext = ".jpg"
    output_filename = f"segmented_{task_id}{ext}"
    output_dir = settings.STORAGE_OUTPUTS_PATH
    if output_dir.startswith("/app/"):
        output_dir = output_dir.replace("/app/", "", 1)
    output_path = os.path.normpath(os.path.join(output_dir, output_filename))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    backend = _get_shared_backend()
    if backend is None or process_single_image is None:
        raise InternalServerErrorException(message="Inference engine pipeline is unavailable.")

    try:
        logger.info("Executing Cityscapes segmentation inference for media '%s'...", media_id)
        result = process_single_image(
            image_input=input_path,
            backend=backend,
            generate_overlay_image=True,
        )

        overlay_img = result.metadata.get("overlay")
        if overlay_img is None:
            raise RuntimeError("Segmentation pipeline did not return a valid overlay image.")

        # Save actual overlay image to output path
        overlay_img.save(output_path, format="JPEG", quality=92)

        # Verify output file exists and is valid
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("Saved overlay image file is missing or empty.")

        with Image.open(output_path) as test_img:
            test_img.verify()

        avg_ms = float(result.inference_time_ms)
        fps_val = round(1000.0 / max(avg_ms, 1.0), 2)
        class_dist = {str(k): float(v) for k, v in result.class_distribution.items()}

        logger.info(
            "Inference completed in %.2f ms (FPS: %.2f, classes: %s)",
            avg_ms,
            fps_val,
            list(class_dist.keys()),
        )
    except Exception as exc:
        logger.error("Segmentation inference failed for media '%s': %s", media_id, exc, exc_info=True)
        raise InternalServerErrorException(message=f"Segmentation inference failed: {str(exc)}") from exc

    task_doc = {
        "_id": task_id,
        "task_id": task_id,
        "media_id": media_id,
        "user_id": current_user.id,
        "status": "completed",
        "progress_percent": 100.0,
        "output_path": output_path,
        "metrics": {
            "fps": fps_val,
            "avgInferenceMs": avg_ms,
            "classDistribution": class_dist,
        },
        "error": None,
        "created_at": now,
        "updated_at": now,
    }

    # Persist task document to MongoDB or in-memory fallback
    if db is not None:
        try:
            await db["tasks"].insert_one(task_doc)
        except Exception as exc:
            logger.warning("MongoDB insert_one failed for task: %s. Using fallback store.", exc)
            _in_memory_tasks[task_id] = task_doc
    else:
        _in_memory_tasks[task_id] = task_doc

    logger.info("Segmentation task created & processed successfully: Task ID '%s', Media ID '%s'", task_id, media_id)

    return InferenceResponse(
        task_id=task_id,
        media_id=media_id,
        status="completed",
        message="Scene segmentation processing completed successfully.",
        created_at=now,
    )


@router.get(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskStatusResponse,
    summary="Get inference task status and performance metrics",
)
async def get_task_status(
    task_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> TaskStatusResponse:
    """Retrieve inference task status, output file paths, and performance metrics by task ID."""
    task_doc = None
    if db is not None:
        try:
            task_doc = await db["tasks"].find_one({"_id": task_id})
        except Exception as exc:
            logger.warning("MongoDB find_one failed for task_id '%s': %s", task_id, exc)
            task_doc = _in_memory_tasks.get(task_id)
    else:
        task_doc = _in_memory_tasks.get(task_id)

    if not task_doc:
        raise NotFoundException(message=f"Inference task #{task_id} not found.")

    metrics_raw = task_doc.get("metrics")
    metrics_obj = None
    if metrics_raw:
        metrics_obj = TaskMetrics(
            fps=float(metrics_raw.get("fps", 30.0)),
            avgInferenceMs=float(metrics_raw.get("avgInferenceMs", 33.33)),
            classDistribution=metrics_raw.get("classDistribution", {}),
        )

    return TaskStatusResponse(
        task_id=str(task_doc.get("_id") or task_doc.get("task_id")),
        media_id=task_doc["media_id"],
        status=task_doc.get("status", "completed"),
        progress_percent=float(task_doc.get("progress_percent", 100.0)),
        output_path=task_doc.get("output_path"),
        metrics=metrics_obj,
        error=task_doc.get("error"),
        created_at=task_doc["created_at"],
        updated_at=task_doc.get("updated_at", task_doc["created_at"]),
    )


__all__ = ["router"]
