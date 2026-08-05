"""Cityscapes Raw Label ID to T013 Taxonomy Mapping Dictionary.

Source: Cityscapes Official Label Documentation (https://www.cityscapes-dataset.com/dataset-overview/)
"""

from typing import Dict

# Cityscapes 34 raw label ID to T013 Pascal VOC class ID mapping
CITYSCAPES_TO_VOC_MAP: Dict[int, int] = {
    0: 0,   # unlabeled -> background
    1: 0,   # ego vehicle -> background
    2: 0,   # rectification border -> background
    3: 0,   # out of roi -> background
    4: 0,   # static -> background
    5: 0,   # dynamic -> background
    6: 0,   # ground -> background
    7: 0,   # road -> background
    8: 0,   # sidewalk -> background
    9: 0,   # parking -> background
    10: 0,  # rail track -> background
    11: 0,  # building -> background
    12: 0,  # wall -> background
    13: 0,  # fence -> background
    14: 0,  # guard rail -> background
    15: 0,  # bridge -> background
    16: 0,  # tunnel -> background
    17: 0,  # pole -> background
    18: 0,  # polegroup -> background
    19: 0,  # traffic light -> background
    20: 0,  # traffic sign -> background
    21: 0,  # vegetation -> background
    22: 0,  # terrain -> background
    23: 0,  # sky -> background
    24: 15, # person -> person (VOC 15)
    25: 15, # rider -> person (VOC 15)
    26: 7,  # car -> car (VOC 7)
    27: 7,  # truck -> car (VOC 7)
    28: 6,  # bus -> bus (VOC 6)
    29: 7,  # caravan -> car (VOC 7)
    30: 7,  # trailer -> car (VOC 7)
    31: 19, # train -> train (VOC 19)
    32: 14, # motorcycle -> motorbike (VOC 14)
    33: 2,  # bicycle -> bicycle (VOC 2)
    -1: 0,  # license plate -> background
}

__all__ = ["CITYSCAPES_TO_VOC_MAP"]
