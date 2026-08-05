"""Image Preprocessing and Prediction Postprocessing Pipeline.

This module provides reusable functions for input image transformation, raw model prediction
postprocessing, class distribution statistical calculations, mask colorization, and mask resizing.
It serves as the centralized image processing pipeline for the inference engine.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import torch
    from torchvision import transforms
except ImportError:
    torch = None
    transforms = None

try:
    from .color_map import apply_color_map, create_color_map, overlay_mask_on_image
except (ImportError, ValueError):
    try:
        from color_map import apply_color_map, create_color_map, overlay_mask_on_image
    except (ImportError, ValueError):
        apply_color_map = None
        create_color_map = None
        overlay_mask_on_image = None

try:
    from ..taxonomy import PASCAL_VOC_CLASSES, PASCAL_VOC_PALETTE, get_class_name
except (ImportError, ValueError):
    from taxonomy import PASCAL_VOC_CLASSES, PASCAL_VOC_PALETTE, get_class_name

logger = logging.getLogger(__name__)


def get_default_transform(image_size: Tuple[int, int] = (520, 520)) -> Any:
    """Return standard torchvision ImageNet normalization transform pipeline.

    Args:
        image_size (Tuple[int, int]): Target image height and width.

    Returns:
        Any: torchvision.transforms.Compose pipeline instance.
    """
    if transforms is None:
        raise RuntimeError("torchvision is required to build default preprocessing transform.")
    return transforms.Compose(
        [
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )


def preprocess_image(image: Any, transform: Optional[Any] = None) -> Any:
    """Preprocess an input PIL Image into a normalized 4D tensor ready for model inference.

    Args:
        image (Any): Input image instance (PIL.Image.Image).
        transform (Optional[Any]): Model-specific torchvision transform callable provided by the model backend.

    Returns:
        Any: 4D PyTorch FloatTensor with batch dimension added `(1, C, H, W)`.

    Raises:
        ValueError: If input image is None or invalid.
        RuntimeError: If PyTorch or torchvision are unavailable.
    """
    if image is None:
        raise ValueError("Input image cannot be None.")

    if torch is None or transforms is None:
        raise RuntimeError("PyTorch and torchvision are required for image preprocessing.")

    try:
        if hasattr(image, "convert"):
            rgb_image = image.convert("RGB")
        else:
            raise ValueError("Input image must be a PIL Image instance.")
    except Exception as err:
        logger.error("Failed to convert image to RGB: %s", str(err))
        raise ValueError(f"Invalid input image: {str(err)}") from err

    if transform is None:
        transform = get_default_transform((520, 520))

    tensor = transform(rgb_image)
    if hasattr(tensor, "dim") and tensor.dim() == 3:
        tensor = tensor.unsqueeze(0)

    return tensor


def postprocess_prediction(output: Any) -> Any:
    """Extract raw model predictions and compute argmax label mask.

    Args:
        output (Any): Raw model output dictionary (containing 'out' key) or tensor.

    Returns:
        Any: 2D numpy ndarray containing predicted class index per pixel `(H, W)`.

    Raises:
        RuntimeError: If output format is invalid or argmax reduction fails.
    """
    if output is None:
        raise RuntimeError("Model output cannot be None.")

    if isinstance(output, dict) and "out" in output:
        tensor = output["out"]
    else:
        tensor = output

    if torch is not None and isinstance(tensor, torch.Tensor):
        if tensor.dim() == 4:
            mask_tensor = tensor.squeeze(0).argmax(0).cpu()
        elif tensor.dim() == 3:
            mask_tensor = tensor.argmax(0).cpu()
        elif tensor.dim() == 2:
            mask_tensor = tensor.cpu()
        else:
            raise RuntimeError(f"Unexpected output tensor dimension: {tensor.dim()}")

        if np is not None:
            return mask_tensor.numpy().astype(np.int32)
        return mask_tensor.numpy().tolist()

    if np is not None and isinstance(tensor, np.ndarray):
        if tensor.ndim == 4:
            return np.argmax(tensor[0], axis=0).astype(np.int32)
        elif tensor.ndim == 3:
            return np.argmax(tensor, axis=0).astype(np.int32)
        return tensor.astype(np.int32)

    raise RuntimeError(f"Unsupported output type for postprocessing: {type(output)}")


def compute_class_distribution(mask: Any) -> Dict[str, float]:
    """Calculate relative class pixel percentages from a 2D segmentation mask.

    Args:
        mask (Any): 2D numpy array or 2D list containing class index labels per pixel.

    Returns:
        Dict[str, float]: Dictionary mapping class names to pixel coverage percentage (0.0 to 100.0).
    """
    if mask is None:
        return {}

    if np is not None and isinstance(mask, np.ndarray):
        flat_mask = mask.flatten()
        total_pixels = flat_mask.size
        if total_pixels == 0:
            return {}
        unique_classes, counts = np.unique(flat_mask, return_counts=True)

        distribution: Dict[str, float] = {}
        for cls_idx, count in zip(unique_classes.tolist(), counts.tolist()):
            cls_idx = int(cls_idx)
            class_name = get_class_name(cls_idx) if 0 <= cls_idx < len(PASCAL_VOC_CLASSES) else f"class_{cls_idx}"
            percentage = round((count / total_pixels) * 100.0, 2)
            distribution[class_name] = percentage
        return distribution

    if isinstance(mask, list):
        flat_list = [pixel for row in mask for pixel in (row if isinstance(row, list) else [row])]
        total_pixels = len(flat_list)
        if total_pixels == 0:
            return {}

        counts_dict: Dict[int, int] = {}
        for item in flat_list:
            counts_dict[item] = counts_dict.get(item, 0) + 1

        distribution = {}
        for cls_idx, count in sorted(counts_dict.items()):
            class_name = get_class_name(cls_idx) if 0 <= cls_idx < len(PASCAL_VOC_CLASSES) else f"class_{cls_idx}"
            percentage = round((count / total_pixels) * 100.0, 2)
            distribution[class_name] = percentage
        return distribution

    return {}


def colorize_mask(mask: Any) -> Any:
    """Map 2D label index mask to an RGB visualization PIL Image using the taxonomy palette.

    Args:
        mask (Any): 2D numpy array or 2D list of integer class labels.

    Returns:
        Any: PIL.Image.Image instance in 'RGB' mode.

    Raises:
        RuntimeError: If Pillow is not installed or mask is invalid.
    """
    if Image is None:
        raise RuntimeError("Pillow is required for mask colorization. Install Pillow.")

    if mask is None:
        raise ValueError("Input mask cannot be None.")

    if np is not None and isinstance(mask, np.ndarray):
        arr = mask
    elif isinstance(mask, list):
        if np is not None:
            arr = np.array(mask, dtype=np.int32)
        else:
            raise RuntimeError("NumPy is required to colorize list-based masks.")
    else:
        raise ValueError(f"Unsupported mask type for colorization: {type(mask)}")

    height, width = arr.shape
    rgb_arr = np.zeros((height, width, 3), dtype=np.uint8)

    palette_len = len(PASCAL_VOC_PALETTE)
    unique_classes = np.unique(arr)

    for cls_id in unique_classes:
        cls_id_int = int(cls_id)
        if 0 <= cls_id_int < palette_len:
            color = PASCAL_VOC_PALETTE[cls_id_int]
        else:
            color = (0, 0, 0)
        rgb_arr[arr == cls_id] = color

    return Image.fromarray(rgb_arr, mode="RGB")


def resize_mask(mask: Any, target_size: Tuple[int, int]) -> Any:
    """Resize a 2D segmentation mask to target dimensions using nearest-neighbor interpolation.

    Args:
        mask (Any): 2D numpy array or 2D list of integer class labels.
        target_size (Tuple[int, int]): Target size tuple `(width, height)`.

    Returns:
        Any: Resized 2D numpy ndarray `(target_height, target_width)`.

    Raises:
        ValueError: If target_size or mask are invalid.
    """
    if mask is None:
        raise ValueError("Input mask cannot be None.")

    if not isinstance(target_size, (tuple, list)) or len(target_size) != 2:
        raise ValueError("target_size must be a tuple of (width, height).")

    width, height = target_size
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid target_size dimensions: {target_size}")

    if np is not None and isinstance(mask, np.ndarray):
        arr = mask
    elif isinstance(mask, list):
        if np is not None:
            arr = np.array(mask, dtype=np.int32)
        else:
            raise RuntimeError("NumPy is required to resize list-based masks.")
    else:
        raise ValueError(f"Unsupported mask type for resizing: {type(mask)}")

    if Image is not None:
        # PIL resize expects (width, height)
        pil_mask = Image.fromarray(arr.astype(np.int32))
        resample_mode = getattr(Image, "Resampling", Image).NEAREST
        resized_pil = pil_mask.resize((width, height), resample=resample_mode)
        return np.array(resized_pil, dtype=np.int32)

    raise RuntimeError("Pillow is required for mask resizing.")


__all__ = [
    "get_default_transform",
    "preprocess_image",
    "postprocess_prediction",
    "compute_class_distribution",
    "colorize_mask",
    "resize_mask",
]
