"""SegFormer Cityscapes Semantic Segmentation Backend.

Implements `SegFormerCityscapesBackend` inheriting from `SegmentationBackend`.
Uses Hugging Face `transformers` & `nvidia/segformer-b0-finetuned-cityscapes-512-1024`
for real road-scene semantic segmentation on CPU/CUDA.
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
    from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
except ImportError:
    torch = None
    SegformerForSemanticSegmentation = None
    SegformerImageProcessor = None

try:
    import numpy as np
except ImportError:
    np = None

# Ensure inference-engine directory is in sys.path
engine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

try:
    from pipeline.interface import SegmentationBackend, SegmentationResult
    from pipeline.processor import compute_class_distribution
    from taxonomy import CITYSCAPES_CLASSES
except (ImportError, ValueError):
    from ..pipeline.interface import SegmentationBackend, SegmentationResult
    from ..pipeline.processor import compute_class_distribution
    from ..taxonomy import CITYSCAPES_CLASSES

logger = logging.getLogger(__name__)


class SegFormerCityscapesBackend(SegmentationBackend):
    """Concrete segmentation backend using SegFormer fine-tuned on Cityscapes 19 urban road classes."""

    MODEL_ID = "nvidia/segformer-b0-finetuned-cityscapes-512-1024"

    def __init__(self, device: Optional[str] = None, weights_path: Optional[str] = None) -> None:
        if torch is not None:
            self._device_str = device or ("cuda" if torch.cuda.is_available() else "cpu")
            self._device = torch.device(self._device_str)
        else:
            self._device_str = device or "cpu"
            self._device = None

        self._processor: Optional[Any] = None
        self._model: Optional[Any] = None
        self._loaded: bool = False

        logger.info("SegFormerCityscapesBackend initialized for device '%s'.", self._device_str)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        if self._loaded and self._model is not None:
            return

        if torch is None or SegformerForSemanticSegmentation is None:
            raise RuntimeError(
                "PyTorch and transformers are required for SegFormerCityscapesBackend. "
                "Ensure torch, torchvision, transformers, and Pillow are installed."
            )

        logger.info("Loading SegFormer Cityscapes model (%s)...", self.MODEL_ID)
        self._processor = SegformerImageProcessor.from_pretrained(self.MODEL_ID)
        self._model = SegformerForSemanticSegmentation.from_pretrained(self.MODEL_ID)
        self._model.eval()
        self._model.to(self._device)
        self._loaded = True
        logger.info("SegFormer Cityscapes model successfully loaded on device '%s'.", self._device_str)

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        if not image_bytes:
            raise ValueError("Input image_bytes cannot be empty.")

        if Image is None:
            raise RuntimeError("Pillow is required for image processing.")

        if not self._loaded or self._model is None:
            self.load_model()

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as err:
            raise ValueError(f"Invalid image bytes: {str(err)}") from err

        orig_w, orig_h = image.size
        start_time = time.perf_counter()

        try:
            inputs = self._processor(images=image, return_tensors="pt").to(self._device)

            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits  # shape [1, 19, H_feat, W_feat]

                # Resize logits to original image dimensions
                upsampled_logits = torch.nn.functional.interpolate(
                    logits, size=(orig_h, orig_w), mode="bilinear", align_corners=False
                )
                pred_mask_tensor = torch.argmax(upsampled_logits, dim=1).squeeze(0).cpu()
                mask = pred_mask_tensor.numpy().astype(np.int32)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            class_dist = compute_class_distribution(mask, taxonomy="cityscapes")

            metadata = self.get_metadata()
            metadata["input_image_size"] = image.size

            return SegmentationResult(
                mask=mask,
                class_distribution=class_dist,
                inference_time_ms=round(elapsed_ms, 2),
                metadata=metadata,
            )
        except Exception as err:
            logger.error("SegFormer inference failure: %s", str(err), exc_info=True)
            raise RuntimeError(f"SegFormer Cityscapes inference failed: {str(err)}") from err

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": "SegFormer B0 Cityscapes",
            "framework": "PyTorch / HuggingFace Transformers",
            "weights": self.MODEL_ID,
            "device": self._device_str,
            "is_loaded": self._loaded,
            "num_classes": len(CITYSCAPES_CLASSES),
            "classes": CITYSCAPES_CLASSES,
        }


__all__ = ["SegFormerCityscapesBackend"]
