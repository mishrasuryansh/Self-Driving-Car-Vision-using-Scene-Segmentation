"""Inference Engine Pipeline Module.

Exposes the public interface contracts and dataclasses for scene segmentation backends.
"""

from .interface import MaskType, SegmentationBackend, SegmentationResult

__all__ = ["MaskType", "SegmentationBackend", "SegmentationResult"]
