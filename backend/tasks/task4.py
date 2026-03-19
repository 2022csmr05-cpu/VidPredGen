# ============================================================
# TASK 4: Frame Validation & Preprocessing (Robust)
# ============================================================

import cv2
import numpy as np


def preprocess_frames(frames: list):

    print("\n[Task 4] Starting Frame Preprocessing...")

    if not isinstance(frames, list):
        raise TypeError("[Task 4 ERROR] Frames must be a list.")

    if len(frames) == 0:
        raise ValueError("[Task 4 ERROR] Frame list is empty.")

    cleaned_frames = []
    removed_count = 0
    base_shape = None

    for frame in frames:

        if frame is None:
            removed_count += 1
            continue

        if not isinstance(frame, np.ndarray):
            removed_count += 1
            continue

        if frame.size == 0:
            removed_count += 1
            continue

        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)

        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        if frame.shape[2] != 3:
            removed_count += 1
            continue

        if base_shape is None:
            base_shape = frame.shape

        if frame.shape != base_shape:
            try:
                frame = cv2.resize(frame, (base_shape[1], base_shape[0]))
            except Exception:
                removed_count += 1
                continue

        cleaned_frames.append(frame)

    if len(cleaned_frames) == 0:
        raise RuntimeError("[Task 4 ERROR] All frames were invalid.")

    height, width = cleaned_frames[0].shape[:2]

    metadata = {
        "total_frames": len(cleaned_frames),
        "frame_width": width,
        "frame_height": height,
        "removed_frames": removed_count
    }

    print("[Task 4] Preprocessing Complete.")
    print(f"[Task 4] Valid Frames: {len(cleaned_frames)}")
    print(f"[Task 4] Removed Frames: {removed_count}")
    print(f"[Task 4] Frame Dimensions: {width}x{height}")

    return cleaned_frames, metadata