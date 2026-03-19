# ============================================================
# TASK 5: Context & Style Detection (Robust)
# ============================================================

import cv2
import numpy as np


def detect_style(frames):

    print("\n[Task 5] Starting Context Detection...")

    # Handle accidental tuple input
    if isinstance(frames, tuple):
        frames = frames[0]

    if frames is None or len(frames) == 0:
        raise ValueError("[Task 5 ERROR] No frames provided.")

    sample_frames = frames[:min(25, len(frames))]

    saturations = []
    brightness_values = []
    edge_densities = []
    motion_scores = []

    prev_gray = None

    for frame in sample_frames:

        if not isinstance(frame, np.ndarray):
            continue

        if frame.size == 0:
            continue

        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception:
            continue

        saturations.append(np.mean(hsv[:, :, 1]))
        brightness_values.append(np.mean(hsv[:, :, 2]))

        edges = cv2.Canny(gray, 100, 200)
        edge_densities.append(np.sum(edges > 0) / edges.size)

        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            motion_scores.append(np.mean(diff))

        prev_gray = gray

    if len(saturations) == 0:

        print("[Task 5 WARNING] No valid frames detected.")

        return {
            "context_type": "unknown",
            "visual_tone": "unknown",
            "motion_level": "unknown",
            "metrics": {}
        }

    avg_sat = float(np.mean(saturations))
    avg_brightness = float(np.mean(brightness_values))
    avg_edge = float(np.mean(edge_densities))
    avg_motion = float(np.mean(motion_scores)) if motion_scores else 0.0

    if avg_motion < 3 and avg_edge > 0.05:
        context_type = "screen_recording"
    elif avg_motion > 15:
        context_type = "fast_motion_video"
    elif avg_motion > 6:
        context_type = "dynamic_scene"
    else:
        context_type = "static_scene"

    if avg_sat > 150:
        visual_tone = "vibrant"
    elif avg_sat < 50:
        visual_tone = "low_saturation"
    elif avg_brightness < 70:
        visual_tone = "dark"
    elif avg_brightness > 200:
        visual_tone = "very_bright"
    else:
        visual_tone = "balanced"

    if avg_motion > 15:
        motion_level = "high"
    elif avg_motion > 6:
        motion_level = "medium"
    else:
        motion_level = "low"

    style_output = {
        "context_type": context_type,
        "visual_tone": visual_tone,
        "motion_level": motion_level,
        "metrics": {
            "avg_saturation": round(avg_sat, 3),
            "avg_brightness": round(avg_brightness, 3),
            "avg_edge_density": round(avg_edge, 5),
            "avg_motion": round(avg_motion, 3)
        }
    }

    print("[Task 5] Context Detection Complete.")
    print(style_output)

    return style_output