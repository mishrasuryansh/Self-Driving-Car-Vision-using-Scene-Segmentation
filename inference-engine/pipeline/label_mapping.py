"""Vectorized Dataset Label Remapping Utilities.

Translates raw dataset class label IDs (from Cityscapes, BDD100K, or custom datasets) into
T013's canonical 21-class semantic segmentation taxonomy using fast NumPy lookup tables (LUT).
Decoupled from specific dataset mapping dictionaries, which reside in the `mappings/` package.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    import numpy as np
except ImportError:
    np = None

try:
    from ..mappings import BDD100K_TO_VOC_MAP, CITYSCAPES_TO_VOC_MAP
except (ImportError, ValueError):
    from mappings import BDD100K_TO_VOC_MAP, CITYSCAPES_TO_VOC_MAP

try:
    from ..taxonomy import BACKGROUND_CLASS_ID, NUM_CLASSES, PASCAL_VOC_CLASSES, get_class_id
except (ImportError, ValueError):
    from taxonomy import BACKGROUND_CLASS_ID, NUM_CLASSES, PASCAL_VOC_CLASSES, get_class_id

logger = logging.getLogger(__name__)

# Global set to collect seen unmapped raw IDs and log warnings only once per newly discovered ID
_SEEN_UNMAPPED_RAW_IDS: Set[int] = set()


def reset_unmapped_ids_tracker() -> None:
    """Reset the global set of seen unmapped raw IDs (useful for testing)."""
    global _SEEN_UNMAPPED_RAW_IDS
    _SEEN_UNMAPPED_RAW_IDS.clear()


def build_lookup_table(
    mapping_dict: Dict[int, int],
    max_raw_id: int = 256,
    default_id: int = BACKGROUND_CLASS_ID,
) -> Any:
    """Construct a 1D NumPy lookup table array for O(1) vectorized label remapping.

    Args:
        mapping_dict (Dict[int, int]): Dictionary mapping raw label IDs to canonical class IDs.
        max_raw_id (int): Maximum expected raw label integer value + 1.
        default_id (int): Fallback class ID for unmapped raw label values (defaults to 0).

    Returns:
        Any: 1D int32 NumPy array `lut` where `lut[raw_id] = target_class_id`.

    Raises:
        RuntimeError: If NumPy is unavailable.
    """
    if np is None:
        raise RuntimeError("NumPy is required to build label mapping lookup tables.")

    # Determine required LUT size
    valid_positive_keys = [k for k in mapping_dict.keys() if k >= 0]
    lut_size = max(max_raw_id, max(valid_positive_keys) + 1 if valid_positive_keys else max_raw_id)

    lut = np.full((lut_size,), default_id, dtype=np.int32)
    for raw_id, target_id in mapping_dict.items():
        if 0 <= raw_id < lut_size:
            # Bound target class ID within T013 range [0, 20]
            bounded_target = target_id if 0 <= target_id < NUM_CLASSES else default_id
            lut[raw_id] = bounded_target

    return lut


def remap_labels(
    mask: Any,
    mapping_dict: Optional[Dict[int, int]] = None,
    default_class_id: int = BACKGROUND_CLASS_ID,
) -> Any:
    """Vectorized remapping of raw 2D dataset label mask into canonical T013 taxonomy IDs.

    Uses NumPy lookup table array indexing (`lut[mask]`) for maximum performance (no per-pixel Python loops).
    Gracefully handles out-of-bounds or unknown raw IDs by logging a warning once per newly discovered ID.

    Args:
        mask (Any): 2D NumPy array or 2D list of raw integer label IDs.
        mapping_dict (Optional[Dict[int, int]]): Dictionary mapping raw IDs to T013 IDs.
            Defaults to CITYSCAPES_TO_VOC_MAP if None.
        default_class_id (int): Fallback class ID for unmapped values (defaults to 0).

    Returns:
        Any: Remapped 2D int32 NumPy array or 2D list with values in [0, 20].

    Raises:
        ValueError: If input mask is None or invalid format.
    """
    if mask is None:
        raise ValueError("Input mask cannot be None.")

    if mapping_dict is None:
        mapping_dict = CITYSCAPES_TO_VOC_MAP

    if np is not None:
        if isinstance(mask, list):
            mask_arr = np.array(mask, dtype=np.int32)
        elif isinstance(mask, np.ndarray):
            mask_arr = mask.astype(np.int32)
        else:
            raise ValueError(f"Unsupported mask type: {type(mask)}. Expected np.ndarray or list.")

        if mask_arr.size == 0:
            return mask_arr

        # Detect new unmapped raw IDs and log once
        unique_raw_ids = set(np.unique(mask_arr).tolist())
        mapped_keys = set(mapping_dict.keys())
        unmapped_ids = unique_raw_ids - mapped_keys

        new_unmapped = unmapped_ids - _SEEN_UNMAPPED_RAW_IDS
        if new_unmapped:
            _SEEN_UNMAPPED_RAW_IDS.update(new_unmapped)
            logger.warning(
                "New unknown raw label IDs encountered: %s. Mapping to default background class ID %d.",
                sorted(list(new_unmapped)),
                default_class_id,
            )

        max_raw_in_mask = max(unique_raw_ids) if unique_raw_ids else 0
        lut = build_lookup_table(mapping_dict, max_raw_id=max(256, max_raw_in_mask + 1), default_id=default_class_id)

        clamped_mask = np.where((mask_arr >= 0) & (mask_arr < len(lut)), mask_arr, 0)
        remapped_mask = lut[clamped_mask]
        return remapped_mask.astype(np.int32)

    # Pure Python list fallback if NumPy is uninstalled
    if isinstance(mask, list):
        remapped = []
        for row in mask:
            if isinstance(row, list):
                remapped_row = [mapping_dict.get(val, default_class_id) for val in row]
                remapped.append(remapped_row)
            else:
                remapped.append(mapping_dict.get(row, default_class_id))
        return remapped

    raise RuntimeError("NumPy is required for label remapping when input is an array.")


__all__ = [
    "CITYSCAPES_TO_VOC_MAP",
    "BDD100K_TO_VOC_MAP",
    "build_lookup_table",
    "remap_labels",
    "reset_unmapped_ids_tracker",
]
