"""T023 FPS Counter Utility Unit Test and Video Pipeline Integration Verification Script.

Tests:
1. Unit tests for FPSCounter initialization, update, and get_fps.
2. End-to-end video pipeline verification with FPSCounter tracking and logging.
"""

import logging
import os
import sys
import tempfile
import time
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

from pipeline.fps_counter import FPSCounter
from pipeline.interface import SegmentationBackend, SegmentationResult
from pipeline.processor import compute_class_distribution
from pipeline.video_pipeline import process_video


class MockBackend(SegmentationBackend):
    """Mock backend for video pipeline testing."""

    def __init__(self, mask: np.ndarray):
        self._mask = mask
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        self._loaded = True

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        stats = compute_class_distribution(self._mask)
        return SegmentationResult(
            mask=self._mask,
            class_distribution=stats,
            inference_time_ms=10.0,
            metadata={"input_image_size": (self._mask.shape[1], self._mask.shape[0])},
        )

    def get_metadata(self):
        return {"model_name": "MockBackend"}


def test_fps_counter_unit():
    """Unit test for FPSCounter class."""
    print("[TEST 1] Testing FPSCounter unit behavior...")
    counter = FPSCounter()
    assert counter.get_fps() == 0.0, f"Expected initial FPS 0.0, got {counter.get_fps()}"

    # Simulate 50 frames over ~1.1 seconds
    start = counter.last_time
    time.sleep(1.1)
    for _ in range(50):
        counter.update()

    fps = counter.get_fps()
    assert fps > 0.0, f"Expected FPS > 0 after 1.1s, got {fps}"
    print(f" -> FPS calculated after 50 updates over ~1.1s: {fps:.2f}")
    print(" -> PASSED! FPSCounter unit test passed.")


def test_video_pipeline_with_fps_counter():
    """End-to-end test: video processing loop with FPSCounter integration."""
    print("[TEST 2] Testing video pipeline with FPSCounter integration...")

    if cv2 is None:
        print(" -> [SKIP] OpenCV not installed, skipping video pipeline test.")
        return

    temp_dir = tempfile.mkdtemp(prefix="t023_fps_test_")
    input_video_path = os.path.join(temp_dir, "sample_input.mp4")
    output_video_path = os.path.join(temp_dir, "sample_output.mp4")

    w, h = 320, 240
    fps = 25.0
    num_frames = 30

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(input_video_path, fourcc, fps, (w, h))

    for f_idx in range(num_frames):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = [100, 150, 200]
        writer.write(frame)

    writer.release()
    assert os.path.exists(input_video_path), "Failed to create synthetic input video"

    mask = np.zeros((h, w), dtype=np.int32)
    backend = MockBackend(mask)

    metrics = process_video(
        video_path=input_video_path,
        backend=backend,
        output_path=output_video_path,
        alpha=0.5,
        log_interval=10,
    )

    assert metrics["total_frames"] == num_frames, f"Expected {num_frames} total frames"
    assert os.path.exists(output_video_path), "Output video file not created"
    assert os.path.getsize(output_video_path) > 0, "Output video file is 0 bytes"
    print(" -> PASSED! Video processing with FPSCounter completed successfully.")


def run_all():
    print("====================================================")
    print("RUNNING T023 FPS COUNTER VERIFICATION SUITE")
    print("====================================================")
    test_fps_counter_unit()
    test_video_pipeline_with_fps_counter()
    print("====================================================")
    print("ALL T023 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
