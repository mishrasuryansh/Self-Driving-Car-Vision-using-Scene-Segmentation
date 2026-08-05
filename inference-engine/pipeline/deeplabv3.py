"""DeepLabV3-ResNet101 Semantic Segmentation Inference Backend.

This module implements the `DeepLabV3Backend` class, inheriting from `SegmentationBackend`.
It ports and modernizes the legacy model loading and inference execution logic, utilizing
the modern PyTorch/torchvision `weights=` API instead of deprecated `pretrained=True`.
"""

import io
import logging
import time
from typing import Any, Dict, Optional

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import torch
    from torchvision import transforms
    from torchvision.models.segmentation import DeepLabV3_ResNet101_Weights, deeplabv3_resnet101
except ImportError:
    torch = None
    transforms = None
    deeplabv3_resnet101 = None
    DeepLabV3_ResNet101_Weights = None

from .interface import SegmentationBackend, SegmentationResult

try:
    from ..taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES
except (ImportError, ValueError):
    from taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES

logger = logging.getLogger(__name__)


class DeepLabV3Backend(SegmentationBackend):
    """Concrete segmentation backend using DeepLabV3-ResNet101.

    Provides lazy model loading, CPU/CUDA hardware execution, and structured
    semantic segmentation inference for single images.
    """

    def __init__(self, device: Optional[str] = None) -> None:
        """Initialize the DeepLabV3 backend settings without loading heavy model weights.

        Args:
            device (Optional[str]): Hardware execution device ('cpu', 'cuda', or None for auto-detect).
        """
        if torch is not None:
            if device is None:
                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self._device_str = device
            self._device: Optional[Any] = torch.device(self._device_str)
        else:
            self._device_str = device or "cpu"
            self._device = None

        self._model: Optional[Any] = None
        self._loaded: bool = False
        self._weights_enum = (
            DeepLabV3_ResNet101_Weights.DEFAULT if DeepLabV3_ResNet101_Weights is not None else None
        )

        if transforms is not None:
            self._transform: Optional[Any] = transforms.Compose(
                [
                    transforms.Resize((520, 520)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225],
                    ),
                ]
            )
        else:
            self._transform = None

        logger.info(
            "DeepLabV3Backend initialized for device '%s' (lazy loading enabled).",
            self._device_str,
        )

    @property
    def is_loaded(self) -> bool:
        """Check whether the model weights are loaded in memory."""
        return self._loaded

    def load_model(self) -> None:
        """Load DeepLabV3-ResNet101 weights into memory and transfer to target device.

        Raises:
            RuntimeError: If PyTorch/torchvision are missing or model loading fails.
        """
        if torch is None or deeplabv3_resnet101 is None:
            raise RuntimeError(
                "PyTorch and torchvision are required for DeepLabV3Backend. "
                "Ensure torch, torchvision, and Pillow are installed."
            )

        if self._loaded and self._model is not None:
            logger.debug("Model already loaded on device '%s'.", self._device_str)
            return

        try:
            logger.info(
                "Loading DeepLabV3-ResNet101 model weights (%s)...",
                self._weights_enum,
            )
            # Modern torchvision weights API (replaces deprecated pretrained=True)
            model = deeplabv3_resnet101(weights=self._weights_enum)
            model.eval()
            model.to(self._device)

            self._model = model
            self._loaded = True
            logger.info(
                "DeepLabV3-ResNet101 model successfully loaded and transferred to '%s'.",
                self._device_str,
            )
        except Exception as err:
            self._loaded = False
            self._model = None
            logger.error("Failed to load DeepLabV3 model: %s", str(err), exc_info=True)
            raise RuntimeError(f"Failed to load DeepLabV3 model: {str(err)}") from err

    def predict(self, image_bytes: bytes) -> SegmentationResult:
        """Execute semantic segmentation inference on input image binary data.

        Args:
            image_bytes (bytes): Binary image file data (JPEG, PNG, etc.).

        Returns:
            SegmentationResult: Structured result with mask, class distribution, latency, and metadata.

        Raises:
            ValueError: If input image bytes are empty or corrupted.
            RuntimeError: If model loading or inference execution fails.
        """
        if not image_bytes:
            raise ValueError("Input image_bytes cannot be empty.")

        if Image is None:
            raise RuntimeError("Pillow is required for image decoding. Install Pillow.")

        # Ensure model weights are loaded
        if not self._loaded or self._model is None:
            self.load_model()

        # Decode image
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as err:
            logger.warning("Failed to decode image bytes: %s", str(err))
            raise ValueError(f"Invalid or corrupted image bytes: {str(err)}") from err

        start_time = time.perf_counter()

        try:
            input_tensor = self._transform(image).unsqueeze(0).to(self._device)

            with torch.no_grad():
                output = self._model(input_tensor)["out"][0]
                mask_tensor = output.argmax(0).cpu()
                mask = mask_tensor.numpy().tolist()

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Calculate class pixel distribution
            flat_mask = mask_tensor.flatten()
            total_pixels = flat_mask.numel()
            unique_classes, counts = torch.unique(flat_mask, return_counts=True)

            class_distribution: Dict[str, float] = {}
            for cls_idx, count in zip(unique_classes.tolist(), counts.tolist()):
                class_name = (
                    PASCAL_VOC_CLASSES[cls_idx]
                    if cls_idx < len(PASCAL_VOC_CLASSES)
                    else f"class_{cls_idx}"
                )
                percentage = round((count / total_pixels) * 100.0, 2)
                class_distribution[class_name] = percentage

            metadata = self.get_metadata()
            metadata["input_image_size"] = image.size

            return SegmentationResult(
                mask=mask,
                class_distribution=class_distribution,
                inference_time_ms=round(elapsed_ms, 2),
                metadata=metadata,
            )
        except Exception as err:
            logger.error("Inference execution failure: %s", str(err), exc_info=True)
            raise RuntimeError(f"DeepLabV3 inference failed: {str(err)}") from err

    def get_metadata(self) -> Dict[str, Any]:
        """Retrieve backend operational metadata.

        Returns:
            Dict[str, Any]: Metadata dictionary containing model specifications.
        """
        return {
            "model_name": "DeepLabV3-ResNet101",
            "framework": "PyTorch / torchvision",
            "weights": str(self._weights_enum),
            "device": self._device_str,
            "is_loaded": self._loaded,
            "recommended_input_size": (520, 520),
            "num_classes": len(PASCAL_VOC_CLASSES),
        }
