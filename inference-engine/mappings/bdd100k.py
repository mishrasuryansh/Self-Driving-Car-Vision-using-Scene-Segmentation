"""BDD100K Raw Label ID to T013 Taxonomy Mapping Dictionary.

Source: BDD100K Official Documentation (https://bdd-data.berkeley.edu/)
"""

from typing import Dict

# BDD100K 19 raw label ID to T013 Pascal VOC class ID mapping
BDD100K_TO_VOC_MAP: Dict[int, int] = {
    0: 0,   # road -> background
    1: 0,   # sidewalk -> background
    2: 0,   # building -> background
    3: 0,   # wall -> background
    4: 0,   # fence -> background
    5: 0,   # pole -> background
    6: 0,   # traffic light -> background
    7: 0,   # traffic sign -> background
    8: 0,   # vegetation -> background
    9: 0,   # terrain -> background
    10: 0,  # sky -> background
    11: 15, # person -> person (VOC 15)
    12: 15, # rider -> person (VOC 15)
    13: 7,  # car -> car (VOC 7)
    14: 7,  # truck -> car (VOC 7)
    15: 6,  # bus -> bus (VOC 6)
    16: 19, # train -> train (VOC 19)
    17: 14, # motorcycle -> motorbike (VOC 14)
    18: 2,  # bicycle -> bicycle (VOC 2)
    255: 0, # void / ignore -> background
}

__all__ = ["BDD100K_TO_VOC_MAP"]
