"""Inference Engine Pipeline Module.

Exposes public interface contracts, dataclasses, model backends, preprocessing/postprocessing utilities,
color map overlay functions, and vectorized dataset label remapping utilities.
"""

from .color_map import apply_color_map, create_color_map, overlay_mask_on_image
from .deeplabv3 import DeepLabV3Backend
from .interface import MaskType, SegmentationBackend, SegmentationResult
from .label_mapping import (
    BDD100K_TO_VOC_MAP,
    CITYSCAPES_TO_VOC_MAP,
    build_lookup_table,
    remap_labels,
)
from .processor import (
    colorize_mask,
    compute_class_distribution,
    get_default_transform,
    postprocess_prediction,
    preprocess_image,
    resize_mask,
)

__all__ = [
    "DeepLabV3Backend",
    "MaskType",
    "SegmentationBackend",
    "SegmentationResult",
    "get_default_transform",
    "preprocess_image",
    "postprocess_prediction",
    "compute_class_distribution",
    "colorize_mask",
    "resize_mask",
    "apply_color_map",
    "create_color_map",
    "overlay_mask_on_image",
    "CITYSCAPES_TO_VOC_MAP",
    "BDD100K_TO_VOC_MAP",
    "build_lookup_table",
    "remap_labels",
]
