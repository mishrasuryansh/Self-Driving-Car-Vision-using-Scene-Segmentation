"""Single Image Preprocessing and Inference Execution Pipeline.

Implements the single-image inference pipeline `process_single_image()`,
accepting raw image bytes, file paths, or PIL Images, delegating model execution
to `SegmentationBackend` (e.g. `DeepLabV3Backend`), measuring pure inference latency,
and returning a `SegmentationResult` conforming strictly to T011's contract.
"""

import io
import logging
import os
import time
from typing import Any, Dict, Optional, Union

try:
    from PIL import Image
except ImportError:
    Image = None

from .deeplabv3 import DeepLabV3Backend
from .interface import SegmentationBackend, SegmentationResult

logger = logging.getLogger(__name__)


def process_single_image(
    image_input: Union[bytes, str, Any],
    backend: Optional[SegmentationBackend] = None,
) -> SegmentationResult:
    """Execute single-image semantic segmentation pipeline.

    Accepts raw image binary bytes, file path string, or PIL.Image instance.
    Delegates inference execution to the provided or default SegmentationBackend,
    logs input image shape and pure inference latency, and returns a SegmentationResult.

    Args:
        image_input (Union[bytes, str, Any]): Input image bytes, file path, or PIL.Image.
        backend (Optional[SegmentationBackend]): Segmentation backend instance (defaults to DeepLabV3Backend).

    Returns:
        SegmentationResult: Structured segmentation result matching T011's contract.

    Raises:
        ValueError: If image_input is None, empty, or invalid format/file path.
        RuntimeError: If Pillow or required dependencies are uninstalled or inference fails.
    """
    if image_input is None:
        raise ValueError("Input image_input cannot be None.")

    if Image is None:
        raise RuntimeError("Pillow is required for image processing. Ensure Pillow is installed.")

    # Convert input to binary bytes for backend processing
    if isinstance(image_input, bytes):
        if not image_input:
            raise ValueError("Input image_bytes cannot be empty.")
        image_bytes = image_input
    elif isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise ValueError(f"Image file path '{image_input}' does not exist.")
        try:
            with open(image_input, "rb") as f:
                image_bytes = f.read()
        except Exception as err:
            raise ValueError(f"Failed to read image file '{image_input}': {str(err)}") from err
    elif hasattr(image_input, "save") and hasattr(image_input, "size"):
        # Handle PIL Image object
        try:
            buffer = io.BytesIO()
            fmt = getattr(image_input, "format", None) or "PNG"
            image_input.save(buffer, format=fmt)
            image_bytes = buffer.getvalue()
        except Exception as err:
            raise ValueError(f"Failed to encode PIL Image: {str(err)}") from err
    else:
        raise ValueError(
            f"Unsupported image_input type: {type(image_input)}. Expected bytes, str path, or PIL Image."
        )

    # Instantiate default backend if not provided
    if backend is None:
        backend = DeepLabV3Backend()

    # Ensure backend model is loaded
    if hasattr(backend, "load_model") and hasattr(backend, "is_loaded"):
        if not backend.is_loaded:
            backend.load_model()

    start_time = time.perf_counter()
    result = backend.predict(image_bytes)
    inference_time = (time.perf_counter() - start_time) * 1000.0

    logger.info(
        "Single-image segmentation complete (input size=%s, pure latency=%.2f ms, detected classes=%d).",
        result.metadata.get("input_image_size", "unknown"),
        result.inference_time_ms,
        len(result.class_distribution),
    )

    return result


__all__ = ["process_single_image"]
