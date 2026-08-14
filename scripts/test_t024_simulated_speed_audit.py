"""T024 Simulated Speed Removal Audit and Video Pipeline Verification Script.

Tests:
1. Code audit of video_pipeline.py: verifies absence of legacy simulated car speed calculations
   and presence of Section 2.4 / T024 removal explanation comment.
2. End-to-end video pipeline execution to verify video processing completes smoothly.
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


def test_code_audit():
    """Audit video_pipeline.py to verify removal of simulated speed metric and presence of documentation comment."""
    print("[TEST 1] Auditing video_pipeline.py for speed metric removal...")
    video_pipeline_file = os.path.join(inf_engine_path, "pipeline", "video_pipeline.py")
    assert os.path.exists(video_pipeline_file), f"File not found: {video_pipeline_file}"

    with open(video_pipeline_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify no legacy car speed computation remains
    assert "car_speed" not in content, "Found unexpected 'car_speed' in video_pipeline.py"
    assert "px/frame" not in content, "Found unexpected 'px/frame' in video_pipeline.py"

    # Verify presence of explanatory comment
    assert "Section 2.4 audit and T024 decision" in content, (
        "Missing Section 2.4 / T024 explanatory comment in video_pipeline.py"
    )

    print(" -> PASSED! Code audit confirmed removal of simulated speed metric and presence of decision comment.")


def test_video_pipeline_end_to_end():
    """Verify video pipeline executes end-to-end after speed metric removal."""
    print("[TEST 2] Testing video pipeline end-to-end execution post-removal...")

    if cv2 is None:
        print(" -> [SKIP] OpenCV not installed, skipping video execution test.")
        return

    temp_dir = tempfile.mkdtemp(prefix="t024_speed_test_")
    input_video_path = os.path.join(temp_dir, "sample_input.mp4")
    output_video_path = os.path.join(temp_dir, "sample_output.mp4")

    w, h = 320, 240
    fps = 25.0
    num_frames = 20

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(input_video_path, fourcc, fps, (w, h))

    for f_idx in range(num_frames):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = [50 + f_idx * 2, 120, 180]
        writer.write(frame)

    writer.release()
    assert os.path.exists(input_video_path), "Failed to generate synthetic input video"

    mask = np.zeros((h, w), dtype=np.int32)
    mask[50:150, 50:150] = 7  # Car class label
    backend = MockBackend(mask)

    metrics = process_video(
        video_path=input_video_path,
        backend=backend,
        output_path=output_video_path,
        alpha=0.5,
        log_interval=5,
    )

    assert metrics["total_frames"] == num_frames, f"Expected {num_frames} frames, got {metrics['total_frames']}"
    assert os.path.exists(output_video_path), "Output video was not created"
    assert os.path.getsize(output_video_path) > 0, "Output video is 0 bytes"
    print(" -> PASSED! Video processing loop completed successfully.")


def run_all():
    print("====================================================")
    print("RUNNING T024 SIMULATED SPEED AUDIT SUITE")
    print("====================================================")
    test_code_audit()
    test_video_pipeline_end_to_end()
    print("====================================================")
    print("ALL T024 AUDIT TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
