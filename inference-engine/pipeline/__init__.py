"""Inference Engine Pipeline Module.

Exposes the public interface contracts, dataclasses, and model backends for scene segmentation.
"""

from .deeplabv3 import DeepLabV3Backend
from .interface import MaskType, SegmentationBackend, SegmentationResult

__all__ = ["DeepLabV3Backend", "MaskType", "SegmentationBackend", "SegmentationResult"]
