"""Canonical Pascal VOC Semantic Segmentation Taxonomy and Color Palette Definitions.

This module serves as the single source of truth for class definitions, integer category IDs,
standard RGB color palettes, and lookup helper functions for the DeepLabV3 Pascal VOC baseline.
It contains zero external ML library dependencies.
"""

from typing import Dict, List, Tuple, Union

# Total number of classes in the Pascal VOC 2012 segmentation taxonomy
NUM_CLASSES: int = 21

# Default background class constants
BACKGROUND_CLASS_ID: int = 0
BACKGROUND_CLASS_NAME: str = "background"

# Ordered 21 Pascal VOC class names (indices 0 through 20)
PASCAL_VOC_CLASSES: List[str] = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]

# Standard Pascal VOC 21-class RGB color palette (RGB 0-255 tuples matching standard VOC evaluation visualization)
PASCAL_VOC_PALETTE: List[Tuple[int, int, int]] = [
    (0, 0, 0),       # 0: background
    (128, 0, 0),     # 1: aeroplane
    (0, 128, 0),     # 2: bicycle
    (128, 128, 0),   # 3: bird
    (0, 0, 128),     # 4: boat
    (128, 0, 128),   # 5: bottle
    (0, 128, 128),   # 6: bus
    (128, 128, 128), # 7: car
    (64, 0, 0),      # 8: cat
    (192, 0, 0),     # 9: chair
    (64, 128, 0),    # 10: cow
    (192, 128, 0),   # 11: diningtable
    (64, 0, 128),    # 12: dog
    (192, 0, 128),   # 13: horse
    (64, 128, 128),  # 14: motorbike
    (192, 128, 128), # 15: person
    (0, 64, 0),      # 16: pottedplant
    (128, 64, 0),    # 17: sheep
    (0, 192, 0),     # 18: sofa
    (128, 192, 0),   # 19: train
    (0, 64, 128),    # 20: tvmonitor
]

# Internal lookup dictionary for fast case-insensitive name-to-ID matching
_CLASS_NAME_TO_ID: Dict[str, int] = {
    name.lower(): idx for idx, name in enumerate(PASCAL_VOC_CLASSES)
}


def get_class_name(class_id: int) -> str:
    """Retrieve the class name string for a given integer class ID.

    Args:
        class_id (int): Integer class label ID (0 to 20).

    Returns:
        str: Class category name.

    Raises:
        ValueError: If class_id is outside valid range (0 to 20).
    """
    if not isinstance(class_id, int) or class_id < 0 or class_id >= NUM_CLASSES:
        raise ValueError(
            f"Invalid class_id: {class_id}. Must be an integer between 0 and {NUM_CLASSES - 1}."
        )
    return PASCAL_VOC_CLASSES[class_id]


def get_class_id(class_name: str) -> int:
    """Retrieve the integer class ID for a given class category name.

    Args:
        class_name (str): Category name string (case-insensitive).

    Returns:
        int: Corresponding integer class label ID.

    Raises:
        ValueError: If class_name is unknown or invalid.
    """
    if not isinstance(class_name, str):
        raise ValueError(f"Invalid class_name type: {type(class_name)}. Must be a string.")

    cleaned_name = class_name.strip().lower()
    if cleaned_name not in _CLASS_NAME_TO_ID:
        raise ValueError(
            f"Unknown class_name '{class_name}'. Valid classes: {PASCAL_VOC_CLASSES}"
        )
    return _CLASS_NAME_TO_ID[cleaned_name]


def is_valid_class(class_id_or_name: Union[int, str]) -> bool:
    """Validate whether an integer class ID or category name exists in the taxonomy.

    Args:
        class_id_or_name (Union[int, str]): Class ID (0 to 20) or category name string.

    Returns:
        bool: True if valid, False otherwise.
    """
    if isinstance(class_id_or_name, int):
        return 0 <= class_id_or_name < NUM_CLASSES
    elif isinstance(class_id_or_name, str):
        return class_id_or_name.strip().lower() in _CLASS_NAME_TO_ID
    return False


def get_color(class_id_or_name: Union[int, str]) -> Tuple[int, int, int]:
    """Retrieve the canonical (R, G, B) color tuple for a given class ID or category name.

    Args:
        class_id_or_name (Union[int, str]): Integer class ID (0 to 20) or category name string.

    Returns:
        Tuple[int, int, int]: RGB color tuple (0-255 values).

    Raises:
        ValueError: If the class ID or category name is invalid.
    """
    if isinstance(class_id_or_name, int):
        class_id = class_id_or_name
    elif isinstance(class_id_or_name, str):
        class_id = get_class_id(class_id_or_name)
    else:
        raise ValueError(
            f"Invalid type for class_id_or_name: {type(class_id_or_name)}. Expected int or str."
        )

    if class_id < 0 or class_id >= NUM_CLASSES:
        raise ValueError(
            f"Invalid class_id: {class_id}. Must be between 0 and {NUM_CLASSES - 1}."
        )

    return PASCAL_VOC_PALETTE[class_id]


__all__ = [
    "NUM_CLASSES",
    "BACKGROUND_CLASS_ID",
    "BACKGROUND_CLASS_NAME",
    "PASCAL_VOC_CLASSES",
    "PASCAL_VOC_PALETTE",
    "get_class_name",
    "get_class_id",
    "is_valid_class",
    "get_color",
]
