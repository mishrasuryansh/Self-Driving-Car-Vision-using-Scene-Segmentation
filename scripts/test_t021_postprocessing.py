"""T021 Postprocessing Unit Test and Sample Image Verification Script.

Tests:
1. Vectorized compute_class_stats on synthetic mask with known class proportions (asserting exact percentages and sum to ~100%).
2. Overlay generation via T014's overlay utility on 3 sample images with visual inspection image outputs saved to storage/outputs.
3. Backward compatibility of process_single_image returning SegmentationResult with mask, stats, and overlay.
"""

import io
import os
import sys
import numpy as np
from PIL import Image

# Ensure repository root and inference engine are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
inf_engine_path = os.path.join(repo_root, "inference-engine")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if inf_engine_path not in sys.path:
    sys.path.insert(0, inf_engine_path)

from pipeline.image_pipeline import (
    compute_class_stats,
    generate_overlay,
    process_single_image,
)
from pipeline.interface import SegmentationBackend, SegmentationResult
from taxonomy import PASCAL_VOC_CLASSES


class MockBackend(SegmentationBackend):
    """Mock backend for unit testing process_single_image without heavy PyTorch loading."""

    def __init__(self, mask: np.ndarray):
        self._mask = mask
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        self._loaded = True

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        stats = compute_class_stats(self._mask)
        return SegmentationResult(
            mask=self._mask,
            class_distribution=stats,
            inference_time_ms=12.34,
            metadata={"input_image_size": (self._mask.shape[1], self._mask.shape[0])},
        )

    def get_metadata(self):
        return {"model_name": "MockBackend"}


def test_synthetic_mask_proportions():
    """Unit test: synthetic mask with known class proportions."""
    print("[TEST 1] Testing compute_class_stats on known synthetic proportions...")

    # Create 100x100 mask (10,000 pixels total)
    # 5,000 pixels (50%) -> class 0 ("background")
    # 3,000 pixels (30%) -> class 7 ("car")
    # 2,000 pixels (20%) -> class 15 ("person")
    mask = np.zeros((100, 100), dtype=np.int32)
    mask[:50, :] = 0   # 50 rows = 5,000 pixels
    mask[50:80, :] = 7  # 30 rows = 3,000 pixels
    mask[80:, :] = 15   # 20 rows = 2,000 pixels

    stats = compute_class_stats(mask)

    assert "background" in stats, "Background class missing from stats"
    assert "car" in stats, "Car class missing from stats"
    assert "person" in stats, "Person class missing from stats"

    assert stats["background"] == 50.0, f"Expected 50.0%, got {stats['background']}"
    assert stats["car"] == 30.0, f"Expected 30.0%, got {stats['car']}"
    assert stats["person"] == 20.0, f"Expected 20.0%, got {stats['person']}"

    total_sum = sum(stats.values())
    assert abs(total_sum - 100.0) < 0.01, f"Percentages must sum to ~100%, got {total_sum}%"

    print(" -> PASSED! Stats match exact known proportions (50% background, 30% car, 20% person, sum=100.0%).")


def test_3_sample_images_overlay_and_pipeline():
    """Manual & automated verification: Run pipeline on 3 sample images, inspect overlays and stats."""
    print("[TEST 2] Testing process_single_image on 3 sample images...")

    output_dir = os.path.join(repo_root, "storage", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    sample_configs = [
        {"name": "sample_1_urban.png", "size": (520, 520), "cls1": 0, "cls2": 7},
        {"name": "sample_2_highway.png", "size": (640, 480), "cls1": 0, "cls2": 6},
        {"name": "sample_3_pedestrian.png", "size": (800, 600), "cls1": 0, "cls2": 15},
    ]

    for idx, cfg in enumerate(sample_configs, start=1):
        w, h = cfg["size"]
        img_arr = np.zeros((h, w, 3), dtype=np.uint8)
        img_arr[:, :] = [100, 150, 200]  # Light blue synthetic background
        # Add synthetic road box
        img_arr[int(h*0.5):, :] = [50, 50, 50]

        pil_img = Image.fromarray(img_arr)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        # Create synthetic mask
        mask = np.full((h, w), cfg["cls1"], dtype=np.int32)
        mask[int(h*0.5):, :] = cfg["cls2"]

        mock_backend = MockBackend(mask)
        result = process_single_image(img_bytes, backend=mock_backend, alpha=0.5)

        # Assert SegmentationResult contract
        assert result.mask is not None, f"Sample {idx} mask is None"
        assert result.class_distribution is not None, f"Sample {idx} stats missing"
        overlay_img = result.metadata.get("overlay") or getattr(result, "overlay", None)
        assert overlay_img is not None, f"Sample {idx} overlay missing in metadata"
        assert isinstance(overlay_img, Image.Image), f"Sample {idx} overlay is not PIL Image"
        assert overlay_img.size == (w, h), f"Sample {idx} overlay size mismatch: {overlay_img.size} vs {(w, h)}"

        # Assert stats sum to 100%
        stats_sum = sum(result.class_distribution.values())
        assert abs(stats_sum - 100.0) < 0.1, f"Sample {idx} stats sum invalid: {stats_sum}"

        # Save output image for visual inspection
        save_path = os.path.join(output_dir, f"sample_overlay_{idx}.png")
        overlay_img.save(save_path)
        print(f" -> Sample {idx} ({w}x{h}): Stats={result.class_distribution}, Overlay saved to '{save_path}'")

    print(" -> PASSED! All 3 sample image overlays and stats verified successfully.")


def run_all():
    print("====================================================")
    print("RUNNING T021 POSTPROCESSING VERIFICATION SUITE")
    print("====================================================")
    test_synthetic_mask_proportions()
    test_3_sample_images_overlay_and_pipeline()
    print("====================================================")
    print("ALL T021 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
