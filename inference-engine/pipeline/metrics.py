"""Evaluation Metrics for Semantic Segmentation.

Provides vectorized functions for calculating pixel accuracy and Mean Intersection-over-Union (mIoU)
for multi-class semantic segmentation models.
"""

import logging
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np

try:
    from ..taxonomy import NUM_CLASSES
except (ImportError, ValueError):
    try:
        from taxonomy import NUM_CLASSES
    except (ImportError, ValueError):
        NUM_CLASSES = 21

logger = logging.getLogger(__name__)


def _validate_and_prepare_masks(
    pred_mask: Union[np.ndarray, Any],
    gt_mask: Union[np.ndarray, Any],
) -> Tuple[np.ndarray, np.ndarray]:
    """Validate input masks and convert PyTorch tensors/lists to NumPy arrays.

    Args:
        pred_mask (Union[np.ndarray, Any]): Predicted class index mask array.
        gt_mask (Union[np.ndarray, Any]): Ground truth class index mask array.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Validated (pred_arr, gt_arr) NumPy arrays.

    Raises:
        ValueError: If either mask is None, empty, or their shapes do not match.
    """
    if pred_mask is None or gt_mask is None:
        raise ValueError("Input masks 'pred_mask' and 'gt_mask' cannot be None.")

    # Handle PyTorch Tensor or list conversion to NumPy arrays
    if hasattr(pred_mask, "detach") and hasattr(pred_mask, "cpu"):
        pred_arr = pred_mask.detach().cpu().numpy()
    else:
        pred_arr = np.asarray(pred_mask)

    if hasattr(gt_mask, "detach") and hasattr(gt_mask, "cpu"):
        gt_arr = gt_mask.detach().cpu().numpy()
    else:
        gt_arr = np.asarray(gt_mask)

    if pred_arr.shape != gt_arr.shape:
        raise ValueError(
            f"Shape mismatch between pred_mask shape {pred_arr.shape} and gt_mask shape {gt_arr.shape}."
        )

    if pred_arr.size == 0:
        raise ValueError("Input mask arrays cannot be empty.")

    return pred_arr, gt_arr


def compute_pixel_accuracy(
    pred_mask: Union[np.ndarray, Any],
    gt_mask: Union[np.ndarray, Any],
    ignore_index: Optional[int] = 255,
) -> float:
    """Compute the overall pixel accuracy between a predicted segmentation mask and ground truth mask.

    Pixel accuracy is calculated as the ratio of correctly classified pixels to the total number
    of evaluated (non-ignored) pixels using vectorized NumPy array operations.

    Args:
        pred_mask (Union[np.ndarray, Any]): Predicted class index mask array of shape (H, W) or (N, H, W).
        gt_mask (Union[np.ndarray, Any]): Ground truth class index mask array of shape (H, W) or (N, H, W).
        ignore_index (Optional[int]): Class index label to ignore in evaluation (default: 255).
            If None, all pixels are evaluated.

    Returns:
        float: Calculated pixel accuracy ratio in the range [0.0, 1.0].

    Raises:
        ValueError: If pred_mask and gt_mask shapes do not match or are empty.
        TypeError: If input arguments cannot be converted to NumPy arrays.
    """
    pred_arr, gt_arr = _validate_and_prepare_masks(pred_mask, gt_mask)

    # Create boolean mask for valid (non-ignored) ground-truth pixels
    if ignore_index is not None:
        valid_mask = gt_arr != ignore_index
    else:
        valid_mask = np.ones_like(gt_arr, dtype=bool)

    total_valid_pixels = int(np.sum(valid_mask))
    if total_valid_pixels == 0:
        logger.warning("No valid pixels found in ground truth mask for evaluation.")
        return 0.0

    # Vectorized computation of matching pixels across valid locations
    correct_pixels = int(np.sum((pred_arr == gt_arr) & valid_mask))
    accuracy = float(correct_pixels / total_valid_pixels)

    return max(0.0, min(1.0, accuracy))


def compute_mean_iou(
    pred_mask: Union[np.ndarray, Any],
    gt_mask: Union[np.ndarray, Any],
    num_classes: Optional[int] = None,
    ignore_index: Optional[int] = 255,
    return_per_class: bool = False,
) -> Union[float, Tuple[float, Dict[int, float]]]:
    """Compute Mean Intersection-over-Union (mIoU) across semantic segmentation classes.

    Per-class IoU is computed as intersection / union for each valid class present in ground truth
    or prediction. Classes absent from both ground truth and prediction (union == 0) are excluded
    from the mean to prevent skewing evaluation results.

    Args:
        pred_mask (Union[np.ndarray, Any]): Predicted class index mask array of shape (H, W) or (N, H, W).
        gt_mask (Union[np.ndarray, Any]): Ground truth class index mask array of shape (H, W) or (N, H, W).
        num_classes (Optional[int]): Total number of semantic classes (defaults to NUM_CLASSES=21).
        ignore_index (Optional[int]): Class index label to ignore in evaluation (default: 255).
        return_per_class (bool): If True, returns a tuple (mIoU, per_class_iou_dict).

    Returns:
        Union[float, Tuple[float, Dict[int, float]]]: Mean IoU float in range [0.0, 1.0], or
        (mIoU, per_class_iou_dict) if return_per_class is True.

    Raises:
        ValueError: If pred_mask and gt_mask shapes do not match or are empty.
    """
    pred_arr, gt_arr = _validate_and_prepare_masks(pred_mask, gt_mask)

    if num_classes is None:
        num_classes = NUM_CLASSES

    # Create boolean mask for valid (non-ignored) ground-truth pixels
    if ignore_index is not None:
        valid_mask = gt_arr != ignore_index
    else:
        valid_mask = np.ones_like(gt_arr, dtype=bool)

    per_class_iou: Dict[int, float] = {}

    for cls_idx in range(num_classes):
        if ignore_index is not None and cls_idx == ignore_index:
            continue

        pred_cls = (pred_arr == cls_idx) & valid_mask
        gt_cls = (gt_arr == cls_idx) & valid_mask

        intersection = int(np.sum(pred_cls & gt_cls))
        union = int(np.sum(pred_cls | gt_cls))

        # Exclude classes absent from both GT and Prediction (union == 0)
        if union == 0:
            continue

        iou_cls = float(intersection / union)
        per_class_iou[cls_idx] = iou_cls

    if not per_class_iou:
        logger.warning("No valid classes found in ground truth or prediction for mIoU evaluation.")
        miou = 0.0
    else:
        miou = float(np.mean(list(per_class_iou.values())))

    miou_bounded = max(0.0, min(1.0, miou))

    if return_per_class:
        return miou_bounded, per_class_iou
    return miou_bounded


__all__ = ["compute_pixel_accuracy", "compute_mean_iou"]
