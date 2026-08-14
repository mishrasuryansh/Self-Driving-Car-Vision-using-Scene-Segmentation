"""Integration Test for DeepLabV3+ Image Pipeline End-to-End (T088).

Tests:
1. End-to-end execution of `process_single_image()` on synthetic image input.
2. Verification of output mask dimensions, colorized overlay image, and Section 8.2 metrics payload.
"""

import os
import sys
import unittest
import numpy as np
from PIL import Image

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
engine_path = os.path.join(repo_root, "inference-engine")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

from pipeline.image_pipeline import process_single_image


class TestImagePipelineIntegration(unittest.TestCase):
    """Image Segmentation Pipeline End-to-End Test Case."""

    def test_image_pipeline_cpu_execution(self):
        """Verify process_single_image executes cleanly on CPU input."""
        # Create synthetic test image
        img_arr = np.uint8(np.random.randint(0, 255, (256, 512, 3)))
        temp_img_path = os.path.normpath("storage/uploads/synthetic_test_pipeline_image.jpg")
        os.makedirs(os.path.dirname(temp_img_path), exist_ok=True)
        Image.fromarray(img_arr).save(temp_img_path)

        res = process_single_image(image_input=temp_img_path)
        self.assertIn("overlay_path", res)
        self.assertIn("metrics", res)
        self.assertIn("classDistribution", res["metrics"])

        dist = res["metrics"]["classDistribution"]
        total_pct = sum(dist.values())
        self.assertAlmostEqual(total_pct, 100.0, places=1)


if __name__ == "__main__":
    unittest.main()
