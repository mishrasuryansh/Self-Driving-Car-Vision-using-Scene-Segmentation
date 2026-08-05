"""Public Interface and Data Contracts for the Inference Engine Pipeline.

This module defines the abstract base class `SegmentationBackend` and the
`SegmentationResult` data structure. All inference engine backends must implement
this contract to ensure modularity and seamless integration with FastAPI
services and Celery workers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Type alias for 2D segmentation mask representations (e.g., List[List[int]] or np.ndarray)
MaskType = Any


@dataclass
class SegmentationResult:
    """Data contract representing the output of a scene segmentation inference execution.

    Attributes:
        mask (MaskType): The 2D segmentation mask containing class label indices for each pixel.
            Can be represented as a 2D list of integers or a numpy array.
        class_distribution (Dict[str, float]): A dictionary mapping class names or label IDs
            to their relative pixel coverage percentages (0.0 to 100.0) or pixel counts.
        inference_time_ms (float): Total execution latency of the model inference pass in milliseconds.
        metadata (Dict[str, Any]): Additional execution context (e.g., model name, version, device, input dimensions).
    """

    mask: MaskType
    class_distribution: Dict[str, float]
    inference_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class SegmentationBackend(ABC):
    """Abstract base class interface for semantic scene segmentation model backends.

    All model backends (e.g., DeepLabV3, YOLOv8-Seg, SegFormer) must inherit
    from this interface and implement its abstract methods.
    """

    @abstractmethod
    def load_model(self) -> None:
        """Initialize and load model architecture and weights into memory/device.

        Raises:
            RuntimeError: If model weights fail to load or hardware device is unavailable.
        """
        pass

    @abstractmethod
    def predict(self, image_bytes: bytes) -> SegmentationResult:
        """Perform semantic segmentation inference on a raw input image.

        Args:
            image_bytes (bytes): Raw binary content of the input image file (JPEG, PNG, etc.).

        Returns:
            SegmentationResult: Structured dataclass containing mask, class stats, and latency metrics.

        Raises:
            ValueError: If input image bytes are invalid or corrupted.
            RuntimeError: If model execution fails during inference.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Retrieve backend operational metadata.

        Returns:
            Dict[str, Any]: Metadata dictionary containing model name, version, device, and class taxonomy.
        """
        pass
