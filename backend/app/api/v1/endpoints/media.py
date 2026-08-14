"""Media File Upload & Retrieval Endpoints.

Provides endpoints for uploading raw image/video files (`POST /api/v1/media/upload`)
and retrieving media metadata (`GET /api/v1/media/{media_id}`) conforming to Section 8.3 schema.
"""

from datetime import datetime, timezone
import logging
import os
from typing import Dict
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, status
from app.api.deps import get_current_active_user
from app.config import settings
from app.db.mongodb import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models.media import MediaResponse
from app.models.user import UserInDB

logger = logging.getLogger("app.api.v1.endpoints.media")
router = APIRouter()

from app.db.memory_store import _in_memory_media

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/quicktime", "video/x-msvideo"}


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=MediaResponse,
    summary="Upload raw image or video file",
)
async def upload_media(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> MediaResponse:
    """Upload media file (JPEG/PNG/MP4), validate mime type and size, and save to storage uploads directory."""
    filename = file.filename or "uploaded_file"
    mime_type = (file.content_type or "").lower().strip()

    # Determine file type
    file_type = None
    if mime_type in ALLOWED_IMAGE_TYPES or filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        file_type = "image"
        if not mime_type or mime_type == "application/octet-stream":
            mime_type = "image/jpeg"
    elif mime_type in ALLOWED_VIDEO_TYPES or filename.lower().endswith((".mp4", ".avi", ".mov")):
        file_type = "video"
        if not mime_type or mime_type == "application/octet-stream":
            mime_type = "video/mp4"
    else:
        raise BadRequestException(message=f"Unsupported file type '{mime_type}'. Only JPEG, PNG, WEBP images and MP4, AVI, MOV videos are allowed.")

    # Read content to validate file size
    contents = await file.read()
    size_bytes = len(contents)
    max_image_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    max_video_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024

    if file_type == "image" and size_bytes > max_image_bytes:
        raise BadRequestException(message=f"Image size ({size_bytes / 1024 / 1024:.2f} MB) exceeds maximum allowed limit of {settings.MAX_IMAGE_SIZE_MB} MB.")

    if file_type == "video" and size_bytes > max_video_bytes:
        raise BadRequestException(message=f"Video size ({size_bytes / 1024 / 1024:.2f} MB) exceeds maximum allowed limit of {settings.MAX_VIDEO_SIZE_MB} MB.")

    # Generate unique media ID and file storage path
    media_id = str(uuid.uuid4())
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = ".jpg" if file_type == "image" else ".mp4"

    saved_filename = f"{media_id}{ext}"
    upload_dir = settings.STORAGE_UPLOADS_PATH
    if upload_dir.startswith("/app/"):
        upload_dir = upload_dir.replace("/app/", "", 1)
    dest_path = os.path.normpath(os.path.join(upload_dir, saved_filename))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Save file to disk
    with open(dest_path, "wb") as f:
        f.write(contents)

    now = datetime.now(timezone.utc)
    media_doc = {
        "_id": media_id,
        "id": media_id,
        "filename": saved_filename,
        "original_name": filename,
        "file_type": file_type,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "file_path": dest_path,
        "user_id": current_user.id,
        "created_at": now,
    }

    # Persist document to MongoDB or in-memory fallback
    if db is not None:
        try:
            await db["media"].insert_one(media_doc)
        except Exception as exc:
            logger.warning("MongoDB insert_one failed for media: %s. Using fallback store.", exc)
            _in_memory_media[media_id] = media_doc
    else:
        _in_memory_media[media_id] = media_doc

    logger.info("Media file uploaded successfully: '%s' (%s, %d bytes) -> '%s'", filename, file_type, size_bytes, dest_path)

    return MediaResponse(
        id=media_id,
        filename=saved_filename,
        original_name=filename,
        file_type=file_type,
        mime_type=mime_type,
        size_bytes=size_bytes,
        file_path=dest_path,
        user_id=current_user.id,
        created_at=now,
    )


@router.get(
    "/{media_id}",
    status_code=status.HTTP_200_OK,
    response_model=MediaResponse,
    summary="Get uploaded media file metadata",
)
async def get_media_metadata(
    media_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_db),
) -> MediaResponse:
    """Retrieve uploaded media item metadata by ID."""
    doc = None
    if db is not None:
        try:
            doc = await db["media"].find_one({"_id": media_id})
        except Exception as exc:
            logger.warning("MongoDB find_one failed for media_id '%s': %s", media_id, exc)
            doc = _in_memory_media.get(media_id)
    else:
        doc = _in_memory_media.get(media_id)

    if not doc:
        raise NotFoundException(message=f"Media item #{media_id} not found.")

    return MediaResponse(
        id=str(doc.get("_id") or doc.get("id")),
        filename=doc["filename"],
        original_name=doc["original_name"],
        file_type=doc["file_type"],
        mime_type=doc["mime_type"],
        size_bytes=doc["size_bytes"],
        file_path=doc["file_path"],
        user_id=doc["user_id"],
        created_at=doc["created_at"],
    )


__all__ = ["router"]
