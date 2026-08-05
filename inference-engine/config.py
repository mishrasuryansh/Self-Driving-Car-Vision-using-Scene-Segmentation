"""Inference Engine Configuration and Backend Selection.

Defines the ModelBackend enum, default target image resolution, and configuration settings
for selecting the active semantic segmentation backbone model across the platform.
"""

from enum import Enum
import os
from typing import Tuple

# Default target input image resolution (height, width) across preprocessing and inference
DEFAULT_IMAGE_SIZE: Tuple[int, int] = (520, 520)


class ModelBackend(str, Enum):
    """Enumeration of supported semantic segmentation model backends."""

    DEEPLABV3 = "DEEPLABV3_PASCAL_VOC"
    DEEPLABV3_CITYSCAPES = "DEEPLABV3_CITYSCAPES"
    YOLOV8_SEG = "YOLOV8_SEG"


# Default active backend configured from environment or defaulted to DEEPLABV3 baseline
ACTIVE_MODEL_BACKEND: ModelBackend = ModelBackend(
    os.getenv("MODEL_BACKEND", ModelBackend.DEEPLABV3.value)
)

__all__ = ["ModelBackend", "ACTIVE_MODEL_BACKEND", "DEFAULT_IMAGE_SIZE"]
