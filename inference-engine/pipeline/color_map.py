"""Color Map and Alpha-Blend Overlay Utilities.

Ports the alpha-blend overlay visualization algorithm (`cv2.addWeighted` / NumPy blend)
using the centralized RGB color palette from `taxonomy.py`.
"""

import logging
from typing import Any, List, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from ..taxonomy import CITYSCAPES_PALETTE, PASCAL_VOC_PALETTE
except (ImportError, ValueError):
    from taxonomy import CITYSCAPES_PALETTE, PASCAL_VOC_PALETTE

logger = logging.getLogger(__name__)


def create_color_map(palette: Optional[List[Tuple[int, int, int]]] = None) -> List[Tuple[int, int, int]]:
    """Return the RGB color palette list matching the taxonomy exactly.

    Args:
        palette (Optional[List[Tuple[int, int, int]]]): Optional palette override.

    Returns:
        List[Tuple[int, int, int]]: List of RGB color tuples.
    """
    if palette is not None:
        return palette
    return CITYSCAPES_PALETTE


def apply_color_map(mask: Any, palette: Optional[List[Tuple[int, int, int]]] = None) -> Any:
    """Apply RGB color palette mapping to a 2D class index segmentation mask.

    Args:
        mask (Any): 2D numpy array or 2D list of integer class labels.
        palette (Optional[List[Tuple[int, int, int]]]): Custom palette list.

    Returns:
        Any: 3D uint8 numpy array `(H, W, 3)` in RGB format.
    """
    if mask is None:
        raise ValueError("Input mask cannot be None.")

    if np is None:
        raise RuntimeError("NumPy is required to apply color map.")

    if isinstance(mask, list):
        arr = np.array(mask, dtype=np.int32)
    elif isinstance(mask, np.ndarray):
        arr = mask.astype(np.int32)
    else:
        raise ValueError(f"Unsupported mask type: {type(mask)}")

    color_palette = create_color_map(palette)
    palette_len = len(color_palette)

    height, width = arr.shape
    rgb_arr = np.zeros((height, width, 3), dtype=np.uint8)

    unique_classes = np.unique(arr)
    for cls_id in unique_classes:
        cls_id_int = int(cls_id)
        if 0 <= cls_id_int < palette_len:
            color = color_palette[cls_id_int]
        else:
            logger.warning(
                "Unmapped class ID %d found in segmentation mask. Falling back to background color (0,0,0).",
                cls_id_int,
            )
            color = (0, 0, 0)
        rgb_arr[arr == cls_id] = color

    return rgb_arr


def overlay_mask_on_image(
    image: Any,
    mask: Any,
    alpha: float = 0.5,
    palette: Optional[List[Tuple[int, int, int]]] = None,
) -> Any:
    """Alpha-blend a colored segmentation mask overlay onto an original RGB image."""
    if image is None or mask is None:
        raise ValueError("Image and mask cannot be None.")

    is_pil = Image is not None and isinstance(image, Image.Image)
    if is_pil:
        img_np = np.array(image.convert("RGB"))
    elif np is not None and isinstance(image, np.ndarray):
        img_np = image
    else:
        raise ValueError(f"Unsupported image type: {type(image)}")

    colored_mask = apply_color_map(mask, palette=palette)

    # Ensure mask dimensions match image dimensions
    if colored_mask.shape[:2] != img_np.shape[:2]:
        if Image is not None:
            mask_pil = Image.fromarray(colored_mask)
            mask_pil = mask_pil.resize((img_np.shape[1], img_np.shape[0]), resample=Image.NEAREST)
            colored_mask = np.array(mask_pil)

    # Perform alpha blending
    if cv2 is not None:
        blended = cv2.addWeighted(img_np, 1.0 - alpha, colored_mask, alpha, 0)
    else:
        blended = ((1.0 - alpha) * img_np + alpha * colored_mask).astype(np.uint8)

    if is_pil:
        return Image.fromarray(blended, mode="RGB")
    return blended


__all__ = [
    "create_color_map",
    "apply_color_map",
    "overlay_mask_on_image",
]
