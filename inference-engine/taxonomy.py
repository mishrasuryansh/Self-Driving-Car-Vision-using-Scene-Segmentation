"""Canonical Pascal VOC & Cityscapes Semantic Segmentation Taxonomy and Color Palette Definitions.

This module serves as the single source of truth for class definitions, integer category IDs,
standard RGB color palettes, and lookup helper functions for semantic scene segmentation.
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

# Standard Pascal VOC 21-class RGB color palette
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

# Official Cityscapes 19 Urban Road-Scene Classes
CITYSCAPES_CLASSES: List[str] = [
    "road",
    "sidewalk",
    "building",
    "wall",
    "fence",
    "pole",
    "traffic light",
    "traffic sign",
    "vegetation",
    "terrain",
    "sky",
    "person",
    "rider",
    "car",
    "truck",
    "bus",
    "train",
    "motorcycle",
    "bicycle",
]

# Official Cityscapes 19-class RGB Color Palette
CITYSCAPES_PALETTE: List[Tuple[int, int, int]] = [
    (128, 64, 128),   # 0: road
    (244, 35, 232),   # 1: sidewalk
    (70, 70, 70),     # 2: building
    (102, 102, 156),  # 3: wall
    (190, 153, 153),  # 4: fence
    (153, 153, 153),  # 5: pole
    (250, 170, 30),   # 6: traffic light
    (220, 220, 0),    # 7: traffic sign
    (107, 142, 35),   # 8: vegetation
    (152, 251, 152),  # 9: terrain
    (70, 130, 180),   # 10: sky
    (220, 20, 60),    # 11: person
    (255, 0, 0),      # 12: rider
    (0, 0, 142),      # 13: car
    (0, 0, 70),       # 14: truck
    (0, 60, 100),     # 15: bus
    (0, 80, 100),     # 16: train
    (0, 0, 230),      # 17: motorcycle
    (119, 11, 32),    # 18: bicycle
]

# Internal lookup dictionary for fast case-insensitive name-to-ID matching
_CLASS_NAME_TO_ID: Dict[str, int] = {
    name.lower(): idx for idx, name in enumerate(PASCAL_VOC_CLASSES)
}
for idx, name in enumerate(CITYSCAPES_CLASSES):
    _CLASS_NAME_TO_ID[name.lower()] = idx


def get_class_name(class_id: int, taxonomy: str = "cityscapes") -> str:
    """Retrieve the class name string for a given integer class ID."""
    classes = CITYSCAPES_CLASSES if taxonomy.lower() == "cityscapes" else PASCAL_VOC_CLASSES
    if not isinstance(class_id, int) or class_id < 0 or class_id >= len(classes):
        return f"class_{class_id}"
    return classes[class_id]


def get_class_id(class_name: str) -> int:
    """Retrieve the integer class ID for a given class category name."""
    if not isinstance(class_name, str):
        raise ValueError(f"Invalid class_name type: {type(class_name)}. Must be a string.")

    cleaned_name = class_name.strip().lower()
    if cleaned_name in _CLASS_NAME_TO_ID:
        return _CLASS_NAME_TO_ID[cleaned_name]
    raise ValueError(f"Unknown class_name '{class_name}'.")


def is_valid_class(class_id_or_name: Union[int, str]) -> bool:
    """Validate whether an integer class ID or category name exists in the taxonomy."""
    if isinstance(class_id_or_name, int):
        return 0 <= class_id_or_name < max(len(PASCAL_VOC_CLASSES), len(CITYSCAPES_CLASSES))
    elif isinstance(class_id_or_name, str):
        return class_id_or_name.strip().lower() in _CLASS_NAME_TO_ID
    return False


def get_color(class_id_or_name: Union[int, str], taxonomy: str = "cityscapes") -> Tuple[int, int, int]:
    """Retrieve the canonical (R, G, B) color tuple for a given class ID or category name."""
    palette = CITYSCAPES_PALETTE if taxonomy.lower() == "cityscapes" else PASCAL_VOC_PALETTE
    if isinstance(class_id_or_name, int):
        class_id = class_id_or_name
    elif isinstance(class_id_or_name, str):
        class_id = get_class_id(class_id_or_name)
    else:
        raise ValueError(f"Invalid type for class_id_or_name: {type(class_id_or_name)}.")

    if 0 <= class_id < len(palette):
        return palette[class_id]
    return (128, 128, 128)


__all__ = [
    "NUM_CLASSES",
    "BACKGROUND_CLASS_ID",
    "BACKGROUND_CLASS_NAME",
    "PASCAL_VOC_CLASSES",
    "PASCAL_VOC_PALETTE",
    "CITYSCAPES_CLASSES",
    "CITYSCAPES_PALETTE",
    "get_class_name",
    "get_class_id",
    "is_valid_class",
    "get_color",
]
