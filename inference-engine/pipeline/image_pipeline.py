"""Single Image Preprocessing, Inference Execution, and Postprocessing Pipeline.

Implements the single-image inference pipeline `process_single_image()`,
accepting raw image bytes, file paths, or PIL Images, delegating model execution
to `SegmentationBackend` (e.g. `DeepLabV3Backend`), measuring pure inference latency,
postprocessing the raw segmentation mask into an alpha-blended overlay image (via T014's `overlay_mask_on_image`)
and per-class pixel percentage statistics (via vectorized NumPy operations in `compute_class_distribution`),
and returning a `SegmentationResult` conforming strictly to T011's contract with postprocessing metadata (`metadata["overlay"]`).
"""

import io
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple, Union

try:
    from PIL import Image
except ImportError:
    Image = None

from .color_map import overlay_mask_on_image
from .deeplabv3 import DeepLabV3Backend
from .interface import SegmentationBackend, SegmentationResult
from .processor import compute_class_distribution

logger = logging.getLogger(__name__)

# Alias compute_class_stats to compute_class_distribution to eliminate code duplication
compute_class_stats = compute_class_distribution


def generate_overlay(
    image_input: Union[bytes, str, Any],
    mask: Any,
    alpha: float = 0.5,
    palette: Optional[Any] = None,
) -> Any:
    """Generate alpha-blended colored segmentation mask overlay onto original image.

    Delegates overlay rendering to T014's `overlay_mask_on_image`.

    Args:
        image_input (Union[bytes, str, Any]): Input image (bytes, file path, or PIL.Image).
        mask (Any): 2D segmentation mask (NumPy array or 2D list).
        alpha (float): Transparency factor (0.0 = image only, 1.0 = mask only).
        palette (Optional[Any]): Custom RGB color palette list.

    Returns:
        Any: Alpha-blended image (PIL.Image.Image or NumPy array matching input type).

    Raises:
        ValueError: If input image or mask are invalid.
        RuntimeError: If Pillow or dependencies are uninstalled.
    """
    if image_input is None or mask is None:
        raise ValueError("Image input and mask cannot be None.")

    if Image is None:
        raise RuntimeError("Pillow is required for image overlay processing.")

    if isinstance(image_input, Image.Image):
        pil_image = image_input.convert("RGB")
    elif isinstance(image_input, bytes):
        if not image_input:
            raise ValueError("Input image bytes cannot be empty.")
        pil_image = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise ValueError(f"Image file path '{image_input}' does not exist.")
        pil_image = Image.open(image_input).convert("RGB")
    elif hasattr(image_input, "convert"):
        pil_image = image_input.convert("RGB")
    else:
        raise ValueError(f"Unsupported image_input type: {type(image_input)}")

    return overlay_mask_on_image(pil_image, mask, alpha=alpha, palette=palette)


def process_single_image(
    image_input: Union[bytes, str, Any],
    backend: Optional[SegmentationBackend] = None,
    alpha: float = 0.5,
    generate_overlay_image: bool = True,
) -> SegmentationResult:
    """Execute single-image semantic segmentation and postprocessing pipeline.

    Accepts raw image binary bytes, file path string, or PIL.Image instance.
    Delegates inference execution to the provided or default `SegmentationBackend`,
    postprocesses the raw 2D mask into an alpha-blended overlay image (reusing T014's `overlay_mask_on_image`)
    and per-class pixel percentage statistics (using vectorized NumPy operations), logs latency, and returns
    a `SegmentationResult` conforming strictly to T011's contract with extended postprocessing metadata (`metadata["overlay"]`).

    Args:
        image_input (Union[bytes, str, Any]): Input image bytes, file path, or PIL.Image.
        backend (Optional[SegmentationBackend]): Segmentation backend instance (defaults to DeepLabV3Backend).
        alpha (float): Transparency blending factor for overlay visualization (default 0.5).
        generate_overlay_image (bool): Whether to generate the overlay image (default True).

    Returns:
        SegmentationResult: Structured segmentation result matching T011's contract with postprocessing metadata.

    Raises:
        ValueError: If image_input is None, empty, or invalid format/file path.
        RuntimeError: If Pillow or required dependencies are uninstalled or inference fails.
    """
    if image_input is None:
        raise ValueError("Input image_input cannot be None.")

    if Image is None:
        raise RuntimeError("Pillow is required for image processing. Ensure Pillow is installed.")

    # Convert input to binary bytes and PIL Image for processing
    pil_image: Optional[Image.Image] = None
    if isinstance(image_input, bytes):
        if not image_input:
            raise ValueError("Input image_bytes cannot be empty.")
        image_bytes = image_input
        try:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as err:
            raise ValueError(f"Failed to decode image bytes: {str(err)}") from err
    elif isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise ValueError(f"Image file path '{image_input}' does not exist.")
        try:
            with open(image_input, "rb") as f:
                image_bytes = f.read()
            pil_image = Image.open(image_input).convert("RGB")
        except ValueError:
            raise
        except Exception as err:
            raise ValueError(f"Failed to read image file '{image_input}': {str(err)}") from err
    elif hasattr(image_input, "save") and hasattr(image_input, "size"):
        # Handle PIL Image object
        try:
            pil_image = image_input.convert("RGB")
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

    # Postprocessing step 1: Vectorized per-class pixel percentage statistics calculation
    stats = compute_class_stats(result.mask)
    result.class_distribution = stats

    # Postprocessing step 2: Generate alpha-blended mask overlay image via T014's overlay utility
    overlay_img = None
    if generate_overlay_image and pil_image is not None:
        try:
            overlay_img = overlay_mask_on_image(pil_image, result.mask, alpha=alpha)
        except Exception as err:
            logger.warning("Failed to generate image overlay: %s", str(err))

    # Extend SegmentationResult metadata with postprocessing outputs preserving exact T011 dataclass contract
    result.metadata["class_stats"] = stats
    result.metadata["overlay"] = overlay_img
    result.metadata["overlay_generated"] = overlay_img is not None

    logger.info(
        "Single-image segmentation and postprocessing complete (input size=%s, pure latency=%.2f ms, detected classes=%d).",
        result.metadata.get("input_image_size", "unknown"),
        result.inference_time_ms,
        len(result.class_distribution),
    )

    return result


__all__ = ["process_single_image", "compute_class_stats", "generate_overlay"]
