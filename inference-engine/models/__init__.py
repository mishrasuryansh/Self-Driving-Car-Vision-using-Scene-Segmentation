"""Inference Engine Models Package.

Exposes concrete model backends for scene segmentation.
"""

from .segformer_backend import SegFormerCityscapesBackend

__all__ = ["SegFormerCityscapesBackend"]
