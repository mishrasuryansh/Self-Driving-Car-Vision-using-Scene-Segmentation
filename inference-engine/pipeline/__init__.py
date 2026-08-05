"""Inference Engine Pipeline Module.

Exposes public interface contracts, dataclasses, model backends, and preprocessing/postprocessing utilities.
"""

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
]
