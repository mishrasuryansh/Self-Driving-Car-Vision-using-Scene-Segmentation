"""Inference Engine Mappings Package.

Exposes dataset raw label ID to canonical taxonomy mapping dictionaries.
"""

from .bdd100k import BDD100K_TO_VOC_MAP
from .cityscapes import CITYSCAPES_TO_VOC_MAP

__all__ = [
    "CITYSCAPES_TO_VOC_MAP",
    "BDD100K_TO_VOC_MAP",
]
