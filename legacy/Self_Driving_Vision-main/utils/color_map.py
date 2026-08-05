import numpy as np
import cv2

# VOC color palette (21 classes)
VOC_COLORS = [
    (0, 0, 0),        # background
    (128, 128, 128),  # sky (gray)
    (128, 64, 128),   # road (purple-gray)
    (0, 128, 0),      # tree (green)
    (0, 0, 255),      # blue (simulate sky)
    (255, 0, 0),      # red (person)
    (255, 255, 0),    # yellow (car)
    (128, 0, 128),    # purple (building)
    (0, 255, 255),    # cyan
    (255, 0, 255),    # magenta
    (64, 128, 128),   # extra
    (128, 128, 0),    # extra
    (0, 64, 64),      # extra
    (64, 0, 128),     # extra
    (0, 128, 128),    # extra
    (128, 0, 0),      # extra
    (0, 64, 128),     # extra
    (64, 128, 0),     # extra
    (128, 64, 0),     # extra
    (0, 0, 128),      # extra
    (64, 0, 0),       # extra
]

def get_voc_colormap():
    return VOC_COLORS

def apply_colormap_overlay(frame, mask, color_map, alpha=0.5):
    color_mask = np.zeros_like(frame)
    for idx, color in enumerate(color_map):
        color_mask[mask == idx] = color
    overlay = cv2.addWeighted(frame, 1 - alpha, color_mask, alpha, 0)
    return overlay
