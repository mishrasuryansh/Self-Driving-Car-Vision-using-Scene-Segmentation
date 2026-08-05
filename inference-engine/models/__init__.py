"""Inference Engine Models Package.

Exposes concrete model backends for scene segmentation.
"""

from .deeplabv3_backend import DeepLabV3Backend

__all__ = ["DeepLabV3Backend"]
