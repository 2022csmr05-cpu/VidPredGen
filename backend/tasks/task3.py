# ============================================================
# TASK 3: Dynamic Media Loader (Robust Version)
# ============================================================

import os
import cv2
import numpy as np
from PIL import Image


SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mov", "mkv", "webm"]
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "bmp", "webp"]


def load_media(file_path: str):
    """
    Loads media file (image or video) and converts into frame list.
    Returns:
        frames (list)
        fps (float)
        input_type (str)
    """

    print("\n[Task 3] Starting Media Load...")

    # --------------------------------------------------------
    # 1. Path Validation
    # --------------------------------------------------------
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"[Task 3 ERROR] File not found at path: {file_path}"
        )

    if not os.path.isfile(file_path):
        raise ValueError(
            f"[Task 3 ERROR] Provided path is not a valid file."
        )

    file_ext = file_path.split('.')[-1].lower()

    # --------------------------------------------------------
    # 2. Video Handling
    # --------------------------------------------------------
    if file_ext in SUPPORTED_VIDEO_FORMATS:

        print("[Task 3] Detected Video File.")

        cap = cv2.VideoCapture(file_path)

        if not cap.isOpened():
            raise RuntimeError(
                "[Task 3 ERROR] OpenCV could not open video file."
            )

        frames = []
        fps = cap.get(cv2.CAP_PROP_FPS)

        # FPS fallback
        if fps is None or fps <= 0:
            print("[Task 3 WARNING] FPS invalid. Defaulting to 24.")
            fps = 24.0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame is None:
                continue

            frames.append(frame)

        cap.release()

        if len(frames) == 0:
            raise RuntimeError(
                "[Task 3 ERROR] No frames extracted. Video may be corrupted."
            )

        print(f"[Task 3] Video Loaded Successfully.")
        print(f"[Task 3] Total Frames: {len(frames)}")
        print(f"[Task 3] FPS: {fps:.2f}")

        return frames, float(fps), "video"

    # --------------------------------------------------------
    # 3. Image Handling
    # --------------------------------------------------------
    elif file_ext in SUPPORTED_IMAGE_FORMATS:

        print("[Task 3] Detected Image File.")

        try:
            image = Image.open(file_path).convert("RGB")
        except Exception as e:
            raise RuntimeError(
                f"[Task 3 ERROR] Could not open image file: {str(e)}"
            )

        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        print("[Task 3] Image Loaded Successfully.")
        print("[Task 3] Treated as Single Frame Video.")

        return [frame], 1.0, "image"

    # --------------------------------------------------------
    # 4. Unsupported Format
    # --------------------------------------------------------
    else:
        raise ValueError(
            f"[Task 3 ERROR] Unsupported file format: .{file_ext}"
        )