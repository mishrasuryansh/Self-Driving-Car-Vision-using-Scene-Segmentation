"""Inference Engine Pipeline Module.

Exposes public interface contracts, dataclasses, model backends, preprocessing/postprocessing utilities, and color map overlay functions.
"""

from .color_map import apply_color_map, create_color_map, overlay_mask_on_image
from .deeplabv3 import DeepLabV3Backend
from .interface import MaskType, SegmentationBackend, SegmentationResult
from .processor import (
    colorize_mask,
    compute_class_distribution,
    postprocess_prediction,
    preprocess_image,
    resize_mask,
)

__all__ = [
    "DeepLabV3Backend",
    "MaskType",
    "SegmentationBackend",
    "SegmentationResult",
    "preprocess_image",
    "postprocess_prediction",
    "compute_class_distribution",
    "colorize_mask",
    "resize_mask",
    "apply_color_map",
    "create_color_map",
    "overlay_mask_on_image",
]
