"""Job Data Models.

Defines Pydantic models for asynchronous video/image processing jobs,
status updates, and job query responses conforming to Section 8.2 & Section 8.3 contract.
"""

from datetime import datetime, timezone
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field
from app.models.inference import TaskMetrics


class JobBase(BaseModel):
    """Base properties for an asynchronous processing job."""

    media_id: str
    status: Literal["pending", "processing", "completed", "failed", "cancelled"] = "pending"
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)


class JobCreate(JobBase):
    """Internal schema for creating a job record."""

    user_id: str


class JobResponse(JobBase):
    """Public API response schema for job status and progress querying."""

    job_id: str
    user_id: str
    output_media_id: Optional[str] = None
    output_path: Optional[str] = None
    metrics: Optional[TaskMetrics] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


__all__ = ["JobBase", "JobCreate", "JobResponse"]
