import cv2
import torch
import numpy as np
import time
from utils.color_map import get_voc_colormap, apply_colormap_overlay
from utils.fps_counter import FPSCounter
from segmentation_model import segment_frame, CLASS_NAME_MAP

def process_video(video_path, model, class_names):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output_segmentation.mp4', fourcc, fps, (width, height))

    color_map = get_voc_colormap()
    fps_counter = FPSCounter()

    print(f"Processing video: {video_path} ({total_frames} frames)")
    processed = 0
    prev_car_mask = None
    car_speed = 0.0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        start_time = time.time()
        mask = segment_frame(model, frame)
        mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)
        mapped_mask = np.zeros_like(mask_resized)
        for k, v in CLASS_NAME_MAP.items():
            mapped_mask[mask_resized == k] = k

        # Detect present classes
        present_classes = set()
        for k, v in CLASS_NAME_MAP.items():
            if np.any(mask_resized == k):
                present_classes.add(v)

        # Simulate car speed (mask centroid movement)
        car_mask = (mask_resized == 6) | (mask_resized == 7) | (mask_resized == 14)  # car, bus, motorbike
        if prev_car_mask is not None:
            prev_centroid = np.argwhere(prev_car_mask)
            curr_centroid = np.argwhere(car_mask)
            if prev_centroid.size > 0 and curr_centroid.size > 0:
                prev_mean = prev_centroid.mean(axis=0)
                curr_mean = curr_centroid.mean(axis=0)
                car_speed = np.linalg.norm(curr_mean - prev_mean)
        prev_car_mask = car_mask.copy()

        overlay = apply_colormap_overlay(frame, mapped_mask, color_map, alpha=0.5)
        inf_time = (time.time() - start_time) * 1000
        fps_counter.update()
        fps_val = fps_counter.get_fps()

        # Draw overlay panel
        panel_height = 90
        cv2.rectangle(overlay, (10, 10), (320, 10 + panel_height), (0, 0, 0), -1)
        cv2.putText(overlay, f"FPS: {fps_val:.1f}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(overlay, f"Inference: {inf_time:.1f} ms", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        cv2.putText(overlay, f"Classes: {', '.join(sorted(present_classes))}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        if 'car' in present_classes:
            cv2.putText(overlay, f"Car speed: {car_speed:.2f} px/frame", (170, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

        out.write(overlay)
        processed += 1
        if processed % 10 == 0 or processed == total_frames:
            print(f"Processed {processed}/{total_frames} frames ({(processed/total_frames)*100:.1f}%)")
    cap.release()
    out.release()
    print("Processing complete! Output saved as output_segmentation.mp4")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
