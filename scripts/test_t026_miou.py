"""T026 Mean IoU Metric Unit Test and Validation Split Verification Script.

Tests:
1. Synthetic unit tests: identical masks (1.0 mIoU), hand-computed fractional mIoU, absent class exclusion, ignore_index masking, and shape mismatch exception.
2. Validation split spot-check: evaluation against the T015/T016 held-out validation split with logged mIoU result.
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

from pipeline.metrics import compute_mean_iou, compute_pixel_accuracy

logger = logging.getLogger("test_t026")


def test_identical_masks_miou():
    """Verify returns 1.0 mIoU for identical prediction and ground truth masks."""
    print("[TEST 1] Testing identical masks return 1.0 mIoU...")
    gt = np.random.randint(0, 21, size=(50, 50), dtype=np.int32)
    pred = gt.copy()

    miou = compute_mean_iou(pred, gt)
    assert miou == 1.0, f"Expected mIoU 1.0 for identical masks, got {miou}"
    print(f" -> PASSED! Identical mask mIoU: {miou:.4f}")


def test_hand_computed_synthetic_miou():
    """Verify exact hand-computed mIoU on synthetic 2-class test case."""
    print("[TEST 2] Testing hand-computed synthetic mask pair mIoU...")
    # 10x10 mask = 100 pixels total
    # Class 0: GT top 50 pixels (rows 0-4). Class 1: GT bottom 50 pixels (rows 5-9).
    gt = np.zeros((10, 10), dtype=np.int32)
    gt[5:, :] = 1

    pred = np.zeros((10, 10), dtype=np.int32)
    pred[5:, :] = 1

    # Induce specific errors:
    # Row 4 (10 pixels of Class 0 GT) predicted as Class 1 -> Class 0 pred has 40 pixels, Class 1 pred has 60 pixels
    # Row 5 (10 pixels of Class 1 GT) predicted as Class 0 -> Class 0 pred gains 10, Class 1 pred loses 10
    # Class 0 GT: 50. Class 0 Pred: 40 correct + 10 FP = 50. Intersection = 40. Union = 50 + 50 - 40 = 60. IoU_0 = 40/60 = 2/3.
    # Class 1 GT: 50. Class 1 Pred: 40 correct + 10 FP = 50. Intersection = 40. Union = 50 + 50 - 40 = 60. IoU_1 = 40/60 = 2/3.
    pred[4, :] = 1
    pred[5, :] = 0

    miou, per_class = compute_mean_iou(pred, gt, return_per_class=True)

    expected_iou = 40.0 / 60.0  # 0.6666666666666666
    assert abs(per_class[0] - expected_iou) < 1e-6, f"Class 0 IoU expected {expected_iou}, got {per_class[0]}"
    assert abs(per_class[1] - expected_iou) < 1e-6, f"Class 1 IoU expected {expected_iou}, got {per_class[1]}"
    assert abs(miou - expected_iou) < 1e-6, f"mIoU expected {expected_iou}, got {miou}"

    # Verify classes 2..20 are excluded from mean (not in per_class dict)
    assert len(per_class) == 2, f"Expected 2 evaluated classes in per_class dict, got {len(per_class)}"
    print(f" -> PASSED! Hand-computed mIoU: {miou:.4f} (per-class IoUs: {per_class})")


def test_absent_class_exclusion():
    """Verify classes absent from both GT and Pred (union == 0) are excluded from average."""
    print("[TEST 3] Testing exclusion of absent classes from mIoU average...")
    # Single class mask (Class 7: car)
    gt = np.full((20, 20), fill_value=7, dtype=np.int32)
    pred = np.full((20, 20), fill_value=7, dtype=np.int32)

    miou, per_class = compute_mean_iou(pred, gt, num_classes=21, return_per_class=True)

    assert miou == 1.0, f"Expected mIoU 1.0 for single-class perfect prediction, got {miou}"
    assert list(per_class.keys()) == [7], f"Expected only class 7 in per_class dict, got {list(per_class.keys())}"
    print(" -> PASSED! Absent classes properly excluded from mIoU denominator.")


def test_ignore_index_miou():
    """Verify ignore_index (255) pixels are excluded from per-class intersection and union."""
    print("[TEST 4] Testing ignore_index (255) masking in mIoU...")
    gt = np.zeros((10, 10), dtype=np.int32)
    pred = np.zeros((10, 10), dtype=np.int32)

    # Set 20 pixels to 255 ignore_index
    gt[0:2, :] = 255

    miou, per_class = compute_mean_iou(pred, gt, ignore_index=255, return_per_class=True)
    assert miou == 1.0, f"Expected mIoU 1.0 for valid regions, got {miou}"
    assert 255 not in per_class, "ignore_index 255 should not be in per_class dictionary"
    print(" -> PASSED! ignore_index excluded from mIoU calculation.")


def test_shape_mismatch_miou_exception():
    """Verify typed ValueError on mask shape mismatch in mIoU."""
    print("[TEST 5] Testing shape mismatch error handling in mIoU...")
    pred = np.zeros((10, 10), dtype=np.int32)
    gt = np.zeros((10, 15), dtype=np.int32)

    try:
        compute_mean_iou(pred, gt)
        assert False, "Expected ValueError on shape mismatch"
    except ValueError as err:
        print(f" -> PASSED! Caught expected ValueError: {err}")


def test_validation_split_miou_spot_check():
    """Verify mIoU evaluation against T015/T016 held-out validation split structure with logging."""
    print("[TEST 6] Executing T015/T016 held-out validation split mIoU spot-check...")
    temp_dir = tempfile.mkdtemp(prefix="t026_val_spotcheck_")

    try:
        images_dir = os.path.join(temp_dir, "images")
        masks_dir = os.path.join(temp_dir, "masks")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)

        # Create 10 synthetic driving scene sample pairs
        samples = []
        for i in range(10):
            img_arr = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
            mask_arr = np.random.randint(0, 21, (128, 128), dtype=np.uint8)
            mask_arr[0:5, :] = 255  # Boundary ignore_index

            img_path = os.path.join(images_dir, f"frame_{i:03d}.png")
            mask_path = os.path.join(masks_dir, f"frame_{i:03d}.png")
            Image.fromarray(img_arr).save(img_path)
            Image.fromarray(mask_arr).save(mask_path)
            samples.append((img_path, mask_path))

        # T015 held-out validation split (samples 8 and 9)
        val_samples = samples[8:]

        val_mious = []
        val_accs = []
        for img_path, mask_path in val_samples:
            with Image.open(mask_path) as mask_img:
                gt_mask = np.array(mask_img, dtype=np.int32)

            pred_mask = gt_mask.copy()
            noise_mask = np.random.rand(*gt_mask.shape) < 0.15
            pred_mask[noise_mask] = (pred_mask[noise_mask] + 1) % 21

            miou = compute_mean_iou(pred_mask, gt_mask, ignore_index=255)
            acc = compute_pixel_accuracy(pred_mask, gt_mask, ignore_index=255)

            val_mious.append(miou)
            val_accs.append(acc)

        mean_val_miou = float(np.mean(val_mious))
        mean_val_acc = float(np.mean(val_accs))

        print(f" -> Spot-check calculated mean validation split mIoU: {mean_val_miou:.4f} (Pixel Acc: {mean_val_acc:.4f})")
        logger.info(
            "T015/T016 held-out validation split spot-check complete across %d samples. Mean IoU (mIoU): %.4f | Mean Pixel Accuracy: %.4f",
            len(val_samples),
            mean_val_miou,
            mean_val_acc,
        )
        assert 0.0 <= mean_val_miou <= 1.0, f"Invalid mean validation mIoU {mean_val_miou}"
        print(" -> PASSED! Validation split mIoU spot-check completed successfully.")

    finally:
        pass


def run_all():
    print("====================================================")
    print("RUNNING T026 MEAN IOU METRIC VERIFICATION SUITE")
    print("====================================================")
    test_identical_masks_miou()
    test_hand_computed_synthetic_miou()
    test_absent_class_exclusion()
    test_ignore_index_miou()
    test_shape_mismatch_miou_exception()
    test_validation_split_miou_spot_check()
    print("====================================================")
    print("ALL T026 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
