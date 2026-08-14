"""Media Upload and Metadata Domain Models.

Defines Pydantic models for media file upload metadata, content validation,
and response schemas conforming to Section 8.3 & Section 11 specifications.
"""

from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


class MediaBase(BaseModel):
    """Base metadata properties for media objects."""

    filename: str
    original_name: str
    file_type: Literal["image", "video"]
    mime_type: str
    size_bytes: int


class MediaCreate(MediaBase):
    """Internal schema for persisting new media record."""

    user_id: str
    file_path: str


class MediaInDB(MediaBase):
    """Schema representing complete media document stored in MongoDB."""

    id: str = Field(..., description="Unique media document ID")
    user_id: str
    file_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MediaResponse(MediaBase):
    """Public API response schema for uploaded media metadata."""

    id: str
    user_id: str
    file_path: str
    created_at: datetime


__all__ = [
    "MediaBase",
    "MediaCreate",
    "MediaInDB",
    "MediaResponse",
]
