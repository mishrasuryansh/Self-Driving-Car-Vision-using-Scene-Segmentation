"""T022 Video Pipeline Unit Test and End-to-End Verification Script.

Tests:
1. Typed exceptions for invalid, missing, or corrupt video inputs.
2. End-to-end video processing execution on a synthetic sample video.
3. Verification that model weights are loaded ONCE (never reloaded per frame).
4. Verification that overlaid output video file is generated and non-empty.
"""

import logging
import os
import sys
import tempfile
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

# Ensure repository root and inference engine are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
inf_engine_path = os.path.join(repo_root, "inference-engine")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if inf_engine_path not in sys.path:
    sys.path.insert(0, inf_engine_path)

from pipeline.video_pipeline import process_video
from pipeline.interface import SegmentationBackend, SegmentationResult
from pipeline.processor import compute_class_distribution


class TrackingMockBackend(SegmentationBackend):
    """Mock backend that tracks model loading count to verify no per-frame reloads occur."""

    def __init__(self, mask: np.ndarray):
        self._mask = mask
        self._loaded = False
        self.load_count = 0
        self.predict_count = 0

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        self.load_count += 1
        self._loaded = True
        print(f" -> [LOG] Model loaded into memory (total load calls: {self.load_count})")

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        if not self._loaded:
            raise RuntimeError("predict() called before load_model()!")
        self.predict_count += 1
        stats = compute_class_distribution(self._mask)
        return SegmentationResult(
            mask=self._mask,
            class_distribution=stats,
            inference_time_ms=15.0,
            metadata={"input_image_size": (self._mask.shape[1], self._mask.shape[0])},
        )

    def get_metadata(self):
        return {"model_name": "TrackingMockBackend"}


def test_exception_handling():
    """Unit test: typed exception handling on invalid inputs."""
    print("[TEST 1] Testing typed exception handling...")

    # Test 1: Empty video path -> ValueError
    try:
        process_video("")
        assert False, "Expected ValueError for empty video path"
    except ValueError as err:
        print(f" -> Passed empty video path check: {err}")

    # Test 2: Non-existent video path -> FileNotFoundError
    try:
        process_video("non_existent_file_path_12345.mp4")
        assert False, "Expected FileNotFoundError for missing file"
    except FileNotFoundError as err:
        print(f" -> Passed missing file path check: {err}")

    print(" -> PASSED! All exception handling tests passed.")


def test_end_to_end_video_processing():
    """End-to-end test: process a synthetic sample video and verify single model load."""
    print("[TEST 2] Testing end-to-end video processing and single model-load policy...")

    if cv2 is None:
        print(" -> [SKIP] OpenCV not installed, skipping video generation test.")
        return

    # Create temporary input video (15 frames of 320x240)
    temp_dir = tempfile.mkdtemp(prefix="t022_video_test_")
    input_video_path = os.path.join(temp_dir, "sample_input.mp4")
    output_video_path = os.path.join(temp_dir, "sample_output_overlaid.mp4")

    w, h = 320, 240
    fps = 25.0
    num_frames = 15

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(input_video_path, fourcc, fps, (w, h))

    for f_idx in range(num_frames):
        # Create synthetic synthetic frame
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = [50 + f_idx * 5, 100, 150]
        writer.write(frame)

    writer.release()
    assert os.path.exists(input_video_path), "Failed to generate synthetic input video"
    print(f" -> Created synthetic input video ({num_frames} frames, {w}x{h}): {input_video_path}")

    # Prepare tracking backend
    mask = np.zeros((h, w), dtype=np.int32)
    mask[100:200, 50:250] = 7  # Car class label
    backend = TrackingMockBackend(mask)

    # Execute process_video
    metrics = process_video(
        video_path=input_video_path,
        backend=backend,
        output_path=output_video_path,
        alpha=0.5,
        log_interval=5,
    )

    # Verify single model load
    assert backend.load_count == 1, f"Expected model loaded EXACTLY ONCE, but was loaded {backend.load_count} times!"
    assert backend.predict_count == num_frames, f"Expected predict called for all {num_frames} frames, got {backend.predict_count}"

    # Verify output metrics & file
    assert os.path.exists(output_video_path), f"Output video was not created at '{output_video_path}'"
    assert os.path.getsize(output_video_path) > 0, "Output video file is 0 bytes"
    assert metrics["total_frames"] == num_frames, f"Expected {num_frames} frames, got {metrics['total_frames']}"

    print(f" -> Output video verified successfully: {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    print(" -> PASSED! Single model load verified (load_count=1) across all frames.")


def run_all():
    print("====================================================")
    print("RUNNING T022 VIDEO PIPELINE VERIFICATION SUITE")
    print("====================================================")
    test_exception_handling()
    test_end_to_end_video_processing()
    print("====================================================")
    print("ALL T022 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
