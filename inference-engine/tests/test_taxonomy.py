"""Unit Tests for Deep Learning Taxonomy & Color Map Modules (T087).

Tests:
1. Taxonomy class label integrity and unique class indexing.
2. Color map RGB palette completeness for all taxonomy classes.
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

from pipeline.color_map import create_color_map, apply_color_map
from pipeline.label_mapping import CITYSCAPES_TO_VOC_MAP, remap_labels
from taxonomy import PASCAL_VOC_CLASSES


class TestTaxonomyAndColorMap(unittest.TestCase):
    """Taxonomy & Color Map Integrity Test Cases."""

    def test_taxonomy_class_indices_unique(self):
        """Verify all class labels in PASCAL VOC / Cityscapes canonical taxonomy are unique."""
        self.assertEqual(len(PASCAL_VOC_CLASSES), len(set(PASCAL_VOC_CLASSES)), "Duplicate class labels in taxonomy!")
        self.assertEqual(len(PASCAL_VOC_CLASSES), 21, "Taxonomy must define 21 classes!")

    def test_color_map_palette_completeness(self):
        """Verify color map palette returns RGB tuple for every class index."""
        palette = create_color_map()
        self.assertTrue(len(palette) >= 21, "Color map must cover at least 21 classes!")

    def test_apply_color_map_output_shape(self):
        """Verify apply_color_map converts 2D mask to 3D RGB array."""
        mask = np.zeros((100, 100), dtype=np.int32)
        rgb_mask = apply_color_map(mask)
        self.assertEqual(rgb_mask.shape, (100, 100, 3))


if __name__ == "__main__":
    unittest.main()
