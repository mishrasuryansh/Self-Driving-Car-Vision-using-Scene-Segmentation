"""Inference Request, Task Status, and Metrics Domain Models.

Defines Pydantic models for triggering scene segmentation tasks (`InferenceRequest`),
returning accepted task acknowledgments (`InferenceResponse`), and polling job status (`TaskStatusResponse`)
matching Section 8.2 & Section 8.3 requirements.
"""

from datetime import datetime, timezone
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Schema for triggering a scene segmentation inference job."""

    media_id: str = Field(..., description="ID of uploaded media item (image or video)")
    use_fp16: bool = Field(default=False, description="Enable FP16 mixed precision CUDA path")
    use_torchscript: bool = Field(default=True, description="Use TorchScript optimized model backend")


class InferenceResponse(BaseModel):
    """Schema for immediate acknowledgment of created inference task."""

    task_id: str
    media_id: str
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskMetrics(BaseModel):
    """Aggregate job performance and class distribution metrics conforming to Section 8.2 shape."""

    fps: float = Field(..., description="Average processing FPS")
    avgInferenceMs: float = Field(..., description="Average per-frame/image inference duration in milliseconds")
    classDistribution: Dict[str, float] = Field(..., description="Overall class pixel distribution breakdown (%)")


class TaskStatusResponse(BaseModel):
    """Schema for task status polling query responses."""

    task_id: str
    media_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress_percent: float = 0.0
    output_media_id: Optional[str] = None
    output_path: Optional[str] = None
    metrics: Optional[TaskMetrics] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


__all__ = [
    "InferenceRequest",
    "InferenceResponse",
    "TaskMetrics",
    "TaskStatusResponse",
]
