"""DeepLabV3-ResNet101 Semantic Segmentation Inference Backend.

This module implements the `DeepLabV3Backend` class, inheriting from `SegmentationBackend`.
It supports loading fine-tuned model checkpoints (e.g. `model_v1.pt`) with sized classification
heads targeting T013's taxonomy (`NUM_CLASSES = 21`), or stock torchvision pretrained weights.
All preprocessing, postprocessing, and class distribution calculations are delegated
to `processor.py`.
"""

import io
import logging
import os
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

try:
    from ..taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES
except (ImportError, ValueError):
    from taxonomy import NUM_CLASSES, PASCAL_VOC_CLASSES

logger = logging.getLogger(__name__)


class DeepLabV3Backend(SegmentationBackend):
    """Concrete segmentation backend using DeepLabV3-ResNet101.

    Provides lazy model loading, CPU/CUDA hardware execution, fine-tuned checkpoint loading,
    and structured semantic segmentation inference for single images.
    """

    def __init__(
        self,
        device: Optional[str] = None,
        weights_path: Optional[str] = None,
    ) -> None:
        """Initialize the DeepLabV3 backend settings without loading heavy model weights.

        Args:
            device (Optional[str]): Hardware execution device ('cpu', 'cuda', or None for auto-detect).
            weights_path (Optional[str]): Path to fine-tuned PyTorch model weights `.pt`.
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
        self._explicit_weights_path: bool = weights_path is not None

        # Resolve weights path
        env_weights_path = os.getenv("MODEL_WEIGHTS_PATH")
        if weights_path is not None:
            self._weights_path: Optional[str] = weights_path
            self._explicit_weights_path = True
        elif env_weights_path:
            self._weights_path = env_weights_path
            self._explicit_weights_path = True
        else:
            # Check default checkpoint locations
            default_v1 = os.path.join("inference-engine", "weights", "model_v1.pt")
            default_ckpt = os.path.join("storage", "checkpoints", "best_deeplabv3_model.pt")
            if os.path.exists(default_v1):
                self._weights_path = default_v1
            elif os.path.exists(default_ckpt):
                self._weights_path = default_ckpt
            else:
                self._weights_path = None

        self._is_fine_tuned: bool = False
        self._weights_enum = (
            DeepLabV3_ResNet101_Weights.DEFAULT if DeepLabV3_ResNet101_Weights is not None else None
        )

        if transforms is not None and DeepLabV3_ResNet101_Weights is not None:
            try:
                self._transform: Optional[Any] = self._weights_enum.transforms()
            except Exception as err:
                logger.debug("Could not obtain weights.transforms(): %s. Falling back to Compose.", err)
                self._transform = transforms.Compose(
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
            "DeepLabV3Backend initialized for device '%s' (weights_path=%s, lazy loading enabled).",
            self._device_str,
            self._weights_path,
        )

    @property
    def is_loaded(self) -> bool:
        """Check whether the model weights are loaded in memory."""
        return self._loaded

    def load_model(self) -> None:
        """Load DeepLabV3-ResNet101 weights into memory and transfer to target device.

        Raises:
            FileNotFoundError: If explicitly configured weights_path does not exist.
            ValueError: If checkpoint content is invalid or corrupted.
            RuntimeError: If PyTorch/torchvision are missing or model loading fails.
        """
        if self._loaded and self._model is not None:
            logger.debug("Model already loaded on device '%s'.", self._device_str)
            return

        # Check explicit weights file existence first
        if self._weights_path is not None:
            if not os.path.exists(self._weights_path):
                msg = f"Configured weights file '{self._weights_path}' does not exist."
                logger.error(msg)
                raise FileNotFoundError(msg)

        if torch is None or deeplabv3_resnet101 is None:
            raise RuntimeError(
                "PyTorch and torchvision are required for DeepLabV3Backend. "
                "Ensure torch, torchvision, and Pillow are installed."
            )

        # If a valid weights path was configured or found at default location
        if self._weights_path is not None:
            try:
                logger.info("Loading fine-tuned model checkpoint from '%s'...", self._weights_path)
                checkpoint = torch.load(self._weights_path, map_location=self._device)

                if not isinstance(checkpoint, dict):
                    raise ValueError(f"Invalid checkpoint format in '{self._weights_path}'. Expected dict state.")

                state_dict = checkpoint.get("model_state_dict", checkpoint)

                # Instantiate model with classification head for T013 NUM_CLASSES
                model = deeplabv3_resnet101(weights=None)
                in_channels = model.classifier[4].in_channels
                model.classifier[4] = nn.Conv2d(in_channels, NUM_CLASSES, kernel_size=1)
                if hasattr(model, "aux_classifier") and model.aux_classifier is not None:
                    aux_channels = model.aux_classifier[4].in_channels
                    model.aux_classifier[4] = nn.Conv2d(aux_channels, NUM_CLASSES, kernel_size=1)

                model.load_state_dict(state_dict)
                model.eval()
                model.to(self._device)

                self._model = model
                self._loaded = True
                self._is_fine_tuned = True
                logger.info(
                    "Fine-tuned DeepLabV3 model successfully loaded from '%s' and transferred to '%s'.",
                    self._weights_path,
                    self._device_str,
                )
                return
            except (FileNotFoundError, ValueError):
                raise
            except Exception as err:
                self._loaded = False
                self._model = None
                msg = f"Failed to load fine-tuned checkpoint from '{self._weights_path}': {str(err)}"
                logger.error(msg, exc_info=True)
                raise RuntimeError(msg) from err

        # Fallback to stock pretrained model weights if no custom weights path is specified
        if self._explicit_weights_path:
            msg = "Explicit weights_path configuration failed."
            logger.error(msg)
            raise RuntimeError(msg)

        try:
            logger.info("No custom checkpoint specified. Loading stock pretrained weights (%s)...", self._weights_enum)
            model = deeplabv3_resnet101(weights=self._weights_enum)
            model.eval()
            model.to(self._device)

            self._model = model
            self._loaded = True
            self._is_fine_tuned = False
            logger.info(
                "Stock DeepLabV3-ResNet101 model successfully loaded and transferred to '%s'.",
                self._device_str,
            )
        except Exception as err:
            self._loaded = False
            self._model = None
            logger.error("Failed to load stock DeepLabV3 model: %s", str(err), exc_info=True)
            raise RuntimeError(f"Failed to load stock DeepLabV3 model: {str(err)}") from err

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
            # Delegate image preprocessing to processor pipeline
            input_tensor = preprocess_image(image, transform=self._transform).to(self._device)

            with torch.no_grad():
                output_raw = self._model(input_tensor)
                # Delegate argmax extraction to processor pipeline
                mask = postprocess_prediction(output_raw)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Delegate class distribution calculation to processor pipeline
            class_distribution = compute_class_distribution(mask)

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
            "weights": self._weights_path if self._is_fine_tuned else str(self._weights_enum),
            "weights_path": self._weights_path,
            "is_fine_tuned": self._is_fine_tuned,
            "device": self._device_str,
            "is_loaded": self._loaded,
            "recommended_input_size": (520, 520),
            "num_classes": len(PASCAL_VOC_CLASSES),
        }
