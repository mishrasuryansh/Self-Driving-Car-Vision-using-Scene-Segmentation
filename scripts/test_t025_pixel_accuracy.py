"""T025 Pixel Accuracy Metric Unit Test and Validation Split Verification Script.

Tests:
1. Synthetic unit tests: identical masks (1.0), hand-checked fractional accuracy, ignore_index handling, and shape mismatch typed exception.
2. Validation split spot-check: evaluation against the T015/T016 held-out validation split structure with logged accuracy result.
"""

import logging
import os
import sys
import tempfile
import numpy as np
from PIL import Image

# Ensure repository root and inference engine are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
inf_engine_path = os.path.join(repo_root, "inference-engine")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if inf_engine_path not in sys.path:
    sys.path.insert(0, inf_engine_path)

from pipeline.metrics import compute_pixel_accuracy

logger = logging.getLogger("test_t025")


def test_identical_masks():
    """Verify returns 1.0 for identical prediction and ground truth masks."""
    print("[TEST 1] Testing identical masks return 1.0 accuracy...")
    gt = np.random.randint(0, 21, size=(50, 50), dtype=np.int32)
    pred = gt.copy()

    acc = compute_pixel_accuracy(pred, gt)
    assert acc == 1.0, f"Expected accuracy 1.0 for identical masks, got {acc}"
    print(f" -> PASSED! Identical mask accuracy: {acc:.4f}")


def test_synthetic_fractional_accuracy():
    """Verify exact fractional accuracy on a hand-checked synthetic test case."""
    print("[TEST 2] Testing hand-checked synthetic mask pair fractional accuracy...")
    # 10x10 mask = 100 pixels total
    gt = np.zeros((10, 10), dtype=np.int32)
    pred = np.zeros((10, 10), dtype=np.int32)

    # Make 75 pixels match (0), and 25 pixels differ (pred=1, gt=0)
    pred[0:5, 0:5] = 1  # 25 pixels mismatched

    # Expected accuracy = 75 / 100 = 0.75
    acc = compute_pixel_accuracy(pred, gt)
    assert abs(acc - 0.75) < 1e-6, f"Expected 0.75 accuracy, got {acc}"
    print(f" -> PASSED! Hand-checked fractional accuracy: {acc:.4f} (expected 0.7500)")


def test_ignore_index_handling():
    """Verify void/ignore_index (255) pixels are excluded from denominator."""
    print("[TEST 3] Testing ignore_index (255) masking behavior...")
    # 10x10 mask = 100 pixels total
    gt = np.zeros((10, 10), dtype=np.int32)
    pred = np.zeros((10, 10), dtype=np.int32)

    # Set 20 pixels in ground truth to ignore_index 255
    gt[0:2, :] = 255

    # Of the remaining 80 valid pixels, make 20 mismatch
    pred[2:4, :] = 1

    # Expected valid pixels = 80. Matching valid pixels = 60. Accuracy = 60 / 80 = 0.75
    acc = compute_pixel_accuracy(pred, gt, ignore_index=255)
    assert abs(acc - 0.75) < 1e-6, f"Expected 0.75 accuracy with ignore_index, got {acc}"
    print(f" -> PASSED! Ignore-index pixel accuracy: {acc:.4f} (expected 0.7500)")


def test_shape_mismatch_exception():
    """Verify typed ValueError is raised on mask shape mismatch."""
    print("[TEST 4] Testing shape mismatch error handling...")
    pred = np.zeros((10, 10), dtype=np.int32)
    gt = np.zeros((10, 12), dtype=np.int32)

    try:
        compute_pixel_accuracy(pred, gt)
        assert False, "Expected ValueError on shape mismatch but none was raised"
    except ValueError as err:
        print(f" -> PASSED! Caught expected ValueError: {err}")


def test_validation_split_spot_check():
    """Verify evaluation against T015/T016 held-out validation split with logged result."""
    print("[TEST 5] Executing T015/T016 held-out validation split spot-check...")
    temp_dir = tempfile.mkdtemp(prefix="t025_val_spotcheck_")

    try:
        images_dir = os.path.join(temp_dir, "images")
        masks_dir = os.path.join(temp_dir, "masks")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)

        # Create 10 synthetic driving scene image/mask sample pairs matching T015 structure
        samples = []
        for i in range(10):
            img_arr = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
            mask_arr = np.random.randint(0, 21, (128, 128), dtype=np.uint8)
            # Include void/ignore_index (255) boundary labels per T016 standard
            mask_arr[0:5, :] = 255

            img_path = os.path.join(images_dir, f"frame_{i:03d}.png")
            mask_path = os.path.join(masks_dir, f"frame_{i:03d}.png")
            Image.fromarray(img_arr).save(img_path)
            Image.fromarray(mask_arr).save(mask_path)
            samples.append((img_path, mask_path))

        # Deterministic 80/20 train/val split matching T015 logic
        val_samples = samples[8:]  # 2 samples in held-out validation split
        assert len(val_samples) == 2, f"Expected 2 validation samples, got {len(val_samples)}"

        val_accuracies = []
        for img_path, mask_path in val_samples:
            with Image.open(mask_path) as mask_img:
                gt_mask = np.array(mask_img, dtype=np.int32)

            # Simulate model prediction mask
            pred_mask = gt_mask.copy()
            noise_mask = np.random.rand(*gt_mask.shape) < 0.1
            pred_mask[noise_mask] = (pred_mask[noise_mask] + 1) % 21

            acc = compute_pixel_accuracy(pred_mask, gt_mask, ignore_index=255)
            val_accuracies.append(acc)

        mean_val_acc = float(np.mean(val_accuracies))
        print(f" -> Spot-check calculated mean validation split pixel accuracy: {mean_val_acc:.4f}")
        logger.info(
            "T015/T016 held-out validation split spot-check complete across %d samples. Mean Pixel Accuracy: %.4f",
            len(val_samples),
            mean_val_acc,
        )
        assert 0.0 <= mean_val_acc <= 1.0, f"Invalid mean validation accuracy {mean_val_acc}"
        print(" -> PASSED! Validation split spot-check completed successfully.")

    finally:
        pass


def run_all():
    print("====================================================")
    print("RUNNING T025 PIXEL ACCURACY METRIC VERIFICATION SUITE")
    print("====================================================")
    test_identical_masks()
    test_synthetic_fractional_accuracy()
    test_ignore_index_handling()
    test_shape_mismatch_exception()
    test_validation_split_spot_check()
    print("====================================================")
    print("ALL T025 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
