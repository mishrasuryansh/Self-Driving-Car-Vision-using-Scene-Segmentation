"""Frame-by-Frame Video Semantic Segmentation Pipeline.

Implements the video processing pipeline `process_video()`, reading frames from
an input video file using OpenCV, executing inference using a single pre-loaded
`SegmentationBackend` instance (loaded once, never reloaded per frame or per run),
reusing T014/T021's overlay/stats utilities (`overlay_mask_on_image` and `compute_class_distribution`),
and writing the overlaid segmentation video to an output file.
"""

import logging
import os
import time
from typing import Any, Dict, Optional, Tuple, Union

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    from PIL import Image
except ImportError:
    Image = None

from .color_map import overlay_mask_on_image
from .deeplabv3 import DeepLabV3Backend
from .interface import SegmentationBackend, SegmentationResult
from .processor import compute_class_distribution

logger = logging.getLogger(__name__)


def process_video(
    video_path: str,
    backend: Optional[SegmentationBackend] = None,
    output_path: Optional[str] = None,
    alpha: float = 0.5,
    log_interval: int = 10,
) -> Dict[str, Any]:
    """Execute frame-by-frame video semantic segmentation and overlay rendering pipeline.

    Reads video frames using OpenCV, delegates model inference to a pre-loaded `SegmentationBackend`
    instance (ensuring the model is loaded once prior to the loop), applies T014's alpha-blend overlay,
    and writes the annotated video to `output_path`.

    Args:
        video_path (str): Path to input video file.
        backend (Optional[SegmentationBackend]): Pre-loaded segmentation backend instance.
            If None, a default DeepLabV3Backend is instantiated and loaded once.
        output_path (Optional[str]): Path to save the overlaid output video file.
            Defaults to 'storage/outputs/output_segmentation.mp4' or alongside input video.
        alpha (float): Transparency factor for overlay visualization (0.0 to 1.0, default 0.5).
        log_interval (int): Frequency (in frames) for progress logging (default 10).

    Returns:
        Dict[str, Any]: Dictionary containing video execution metrics:
            - "total_frames" (int): Total number of frames processed.
            - "fps" (float): Original video frames-per-second rate.
            - "output_path" (str): Path to generated output video.
            - "processing_time_sec" (float): Total processing pipeline execution time in seconds.

    Raises:
        ValueError: If video_path is None or empty.
        FileNotFoundError: If video_path file does not exist on disk.
        RuntimeError: If OpenCV is not installed or video file cannot be opened/read.
    """
    if not video_path:
        raise ValueError("Input video_path cannot be None or empty.")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video file '{video_path}' does not exist.")

    if cv2 is None:
        raise RuntimeError("OpenCV (cv2) is required for video processing. Ensure opencv-python is installed.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video file '{video_path}'. File may be corrupt or unsupported format.")

    # Retrieve video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if width <= 0 or height <= 0:
        cap.release()
        raise RuntimeError(f"Invalid video dimensions ({width}x{height}) for file '{video_path}'.")

    # Resolve output video path
    if output_path is None:
        default_dir = os.path.join("storage", "outputs")
        os.makedirs(default_dir, exist_ok=True)
        output_path = os.path.join(default_dir, "output_segmentation.mp4")
    else:
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if not out.isOpened():
        # Fallback codec if mp4v fails
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to initialize VideoWriter for output path '{output_path}'.")

    # Ensure backend model is instantiated and loaded ONCE before the frame loop
    if backend is None:
        logger.info("No backend provided to process_video. Instantiating default DeepLabV3Backend...")
        backend = DeepLabV3Backend()

    if hasattr(backend, "is_loaded") and hasattr(backend, "load_model"):
        if not backend.is_loaded:
            logger.info("Loading backend model weights (once for video run)...")
            backend.load_model()
        else:
            logger.info("Model already loaded on backend; proceeding without reloading.")

    logger.info(
        "Starting video processing loop: '%s' (%dx%d, %.2f fps, %d total frames) -> '%s'",
        video_path,
        width,
        height,
        fps,
        total_frames,
        output_path,
    )

    start_time = time.perf_counter()
    processed_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            # Frame is OpenCV BGR (H, W, 3). Convert to PIL Image in RGB format for model/overlay pipeline
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame) if Image is not None else rgb_frame

            # Convert frame to image bytes for backend.predict
            encode_success, buffer = cv2.imencode(".png", frame)
            if not encode_success:
                frame_bytes = b""
            else:
                frame_bytes = buffer.tobytes()

            # Execute single frame inference (model is ALREADY loaded)
            result = backend.predict(frame_bytes)

            # Apply T014 overlay utility
            overlay_result = overlay_mask_on_image(pil_img, result.mask, alpha=alpha)

            # Convert overlay result back to BGR NumPy array for OpenCV VideoWriter
            if Image is not None and isinstance(overlay_result, Image.Image):
                overlay_bgr = cv2.cvtColor(np.array(overlay_result), cv2.COLOR_RGB2BGR)
            elif np is not None and isinstance(overlay_result, np.ndarray):
                overlay_bgr = cv2.cvtColor(overlay_result, cv2.COLOR_RGB2BGR)
            else:
                overlay_bgr = frame

            out.write(overlay_bgr)
            processed_count += 1

            if log_interval > 0 and (processed_count % log_interval == 0 or processed_count == total_frames):
                pct = (processed_count / total_frames * 100.0) if total_frames > 0 else 0.0
                logger.info("Processed %d/%d frames (%.1f%%)", processed_count, total_frames, pct)

    finally:
        cap.release()
        out.release()

    total_elapsed = time.perf_counter() - start_time
    logger.info(
        "Video processing complete: %d frames processed in %.2f seconds (%.2f fps effective). Output saved to '%s'.",
        processed_count,
        total_elapsed,
        (processed_count / total_elapsed) if total_elapsed > 0 else 0.0,
        output_path,
    )

    return {
        "total_frames": processed_count,
        "fps": fps,
        "output_path": output_path,
        "processing_time_sec": round(total_elapsed, 2),
    }


__all__ = ["process_video"]
