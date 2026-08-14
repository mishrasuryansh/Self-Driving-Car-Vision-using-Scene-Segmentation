"""DeepLabV3 / SegFormer Cityscapes Semantic Segmentation Inference Backend.

Provides `DeepLabV3Backend`, which automatically delegates to `SegFormerCityscapesBackend`
for real road-scene segmentation (Cityscapes 19 classes) or loads fine-tuned PyTorch checkpoints.
"""

import io
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import torch
    import torch.nn as nn
    from torchvision import transforms
    from torchvision.models.segmentation import DeepLabV3_ResNet101_Weights, deeplabv3_resnet101
except ImportError:
    torch = None
    nn = None
    transforms = None
    deeplabv3_resnet101 = None
    DeepLabV3_ResNet101_Weights = None

from .interface import SegmentationBackend, SegmentationResult
from .processor import compute_class_distribution, postprocess_prediction, preprocess_image

# Ensure inference-engine root directory is in sys.path
engine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

try:
    from models.segformer_backend import SegFormerCityscapesBackend
except Exception as err:
    try:
        from ..models.segformer_backend import SegFormerCityscapesBackend
    except Exception:
        SegFormerCityscapesBackend = None

try:
    from ..taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES
except (ImportError, ValueError):
    try:
        from taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES
    except (ImportError, ValueError):
        NUM_CLASSES = 21
        PASCAL_VOC_CLASSES = [f"class_{i}" for i in range(21)]

logger = logging.getLogger(__name__)


class DeepLabV3Backend(SegmentationBackend):
    """Concrete segmentation backend supporting real Cityscapes road-scene segmentation."""

    def __init__(
        self,
        device: Optional[str] = None,
        weights_path: Optional[str] = None,
        use_fp16: bool = False,
    ) -> None:
        self._device_str = device or ("cuda" if (torch is not None and torch.cuda.is_available()) else "cpu")
        self._weights_path = weights_path
        self._use_fp16 = use_fp16
        self._segformer_backend: Optional[Any] = None

        if not self._weights_path and SegFormerCityscapesBackend is not None:
            self._segformer_backend = SegFormerCityscapesBackend(device=self._device_str)

        self._loaded: bool = False
        self._model: Optional[Any] = None

    @property
    def is_loaded(self) -> bool:
        if self._segformer_backend is not None:
            return self._segformer_backend.is_loaded
        return self._loaded

    def load_model(self) -> None:
        if self._segformer_backend is not None:
            self._segformer_backend.load_model()
            self._loaded = True
            return

        if torch is None or deeplabv3_resnet101 is None:
            raise RuntimeError("PyTorch and torchvision are required for DeepLabV3Backend.")

        if self._weights_path and os.path.exists(self._weights_path):
            logger.info("Loading PyTorch model checkpoint from '%s'...", self._weights_path)
            checkpoint = torch.load(self._weights_path, map_location=self._device_str)
            state_dict = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
            model = deeplabv3_resnet101(weights=None)
            in_channels = model.classifier[4].in_channels
            model.classifier[4] = nn.Conv2d(in_channels, NUM_CLASSES, kernel_size=1)
            model.load_state_dict(state_dict)
            model.eval()
            model.to(self._device_str)
            self._model = model
            self._loaded = True
            return

        if SegFormerCityscapesBackend is not None:
            self._segformer_backend = SegFormerCityscapesBackend(device=self._device_str)
            self._segformer_backend.load_model()
            self._loaded = True
            return

        raise RuntimeError("No model weights or SegFormer backend available.")

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        if not self.is_loaded:
            self.load_model()

        if self._segformer_backend is not None:
            return self._segformer_backend.predict(image_bytes)

        if not self._model:
            raise RuntimeError("DeepLabV3 model is not loaded.")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        start_t = time.perf_counter()
        tensor = preprocess_image(image).to(self._device_str)

        with torch.no_grad():
            output_raw = self._model(tensor)
            mask = postprocess_prediction(output_raw)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        class_dist = compute_class_distribution(mask)
        metadata = self.get_metadata()
        metadata["input_image_size"] = image.size

        return SegmentationResult(
            mask=mask,
            class_distribution=class_dist,
            inference_time_ms=round(elapsed_ms, 2),
            metadata=metadata,
        )

    def get_metadata(self) -> Dict[str, Any]:
        if self._segformer_backend is not None:
            return self._segformer_backend.get_metadata()
        return {
            "model_name": "DeepLabV3-ResNet101",
            "framework": "PyTorch / torchvision",
            "device": self._device_str,
            "is_loaded": self._loaded,
        }


__all__ = ["DeepLabV3Backend"]
