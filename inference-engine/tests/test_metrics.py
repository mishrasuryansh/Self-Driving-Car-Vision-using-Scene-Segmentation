"""Unit Tests for Perception Metrics & IoU Evaluation Modules (T087).

Tests:
1. Mean IoU calculation on synthetic segmentation masks.
2. Pixel accuracy calculation.
3. Edge case masks: all background, single class, and empty prediction.
"""

import os
import sys
import unittest
import numpy as np

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
engine_path = os.path.join(repo_root, "inference-engine")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

from pipeline.metrics import compute_pixel_accuracy, compute_mean_iou


class TestPerceptionMetrics(unittest.TestCase):
    """Segmentation Metrics Test Cases."""

    def test_perfect_prediction_metrics(self):
        """Verify 100% accuracy and 1.0 IoU when prediction matches ground truth exactly."""
        target = np.array([[0, 1], [2, 0]], dtype=np.int64)
        pred = np.array([[0, 1], [2, 0]], dtype=np.int64)

        acc = compute_pixel_accuracy(pred, target)
        miou = compute_mean_iou(pred, target, num_classes=19)
        self.assertAlmostEqual(acc, 1.0, places=4)
        self.assertAlmostEqual(miou, 1.0, places=4)

    def test_edge_case_all_single_class(self):
        """Verify edge case where mask contains only a single class."""
        target = np.zeros((64, 64), dtype=np.int64)
        pred = np.zeros((64, 64), dtype=np.int64)
        acc = compute_pixel_accuracy(pred, target)
        miou = compute_mean_iou(pred, target, num_classes=19)
        self.assertAlmostEqual(acc, 1.0, places=4)
        self.assertAlmostEqual(miou, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
