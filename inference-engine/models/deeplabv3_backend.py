"""DeepLabV3 Backend Package Module.

Re-exports DeepLabV3Backend and integrates with inference-engine config.
"""

from ..config import ACTIVE_MODEL_BACKEND, ModelBackend
from ..pipeline.deeplabv3 import DeepLabV3Backend

__all__ = ["DeepLabV3Backend", "ACTIVE_MODEL_BACKEND", "ModelBackend"]
