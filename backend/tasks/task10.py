# ============================================================
# TASK 10 : HYBRID VIDEO GENERATION (FINAL FIXED)
# ============================================================

import cv2
import numpy as np
import os


# ------------------------------------------------------------
# OUTPUT FOLDER
# ------------------------------------------------------------
def ensure_output_folder():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


# ------------------------------------------------------------
# APPLY FORWARD MOTION
# ------------------------------------------------------------
def apply_forward_motion(frame, step):
    shift = int(3 + step * 2)
    return np.roll(frame, -shift, axis=1)


# ------------------------------------------------------------
# APPLY INTERACTION EFFECT
# ------------------------------------------------------------
def apply_interaction(frame, step):
    h, w, _ = frame.shape

    overlay = frame.copy()
    radius = int(30 + step * 5)

    cv2.circle(overlay, (w // 2, h // 2), radius, (0, 255, 255), -1)

    return cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)


# ------------------------------------------------------------
# APPLY STUMBLE EFFECT
# ------------------------------------------------------------
def apply_stumble(frame, step):
    h, w, _ = frame.shape

    dy = int(np.sin(step * 0.5) * 4)

    M = np.float32([[1, 0, 0], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (w, h))


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------
def generate_future_video(
    frames,
    selected_option,
    fps,
    output_filename="predicted_output.mp4",
    duration=2
):

    print("\n[Task 10] Generating HYBRID video...")

    if not frames:
        raise ValueError("No frames provided")

    # --------------------------------------------------------
    # OPTION TEXT
    # --------------------------------------------------------
    if isinstance(selected_option, dict):
        option_text = selected_option.get("text", "").lower()
    else:
        option_text = str(selected_option).lower()

    # --------------------------------------------------------
    # OUTPUT PATH
    # --------------------------------------------------------
    output_dir = ensure_output_folder()
    output_path = os.path.join(output_dir, output_filename)

    # --------------------------------------------------------
    # VIDEO SETUP
    # --------------------------------------------------------
    h, w, _ = frames[0].shape

    fps_int = int(fps) if fps else 24   # 🔥 FIX HERE

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps_int,
        (w, h)
    )

    # --------------------------------------------------------
    # 1. SEED FRAMES
    # --------------------------------------------------------
    seed_frames = frames[-15:] if len(frames) >= 15 else frames

    for f in seed_frames:
        out.write(f)

    # --------------------------------------------------------
    # 2. FUTURE FRAMES
    # --------------------------------------------------------
    total_frames = int(duration * fps_int)   # 🔥 FIX HERE

    prev_frame = seed_frames[-1].copy()

    for i in range(total_frames):

        new_frame = prev_frame.copy()

        # FORWARD MOTION
        if any(word in option_text for word in ["run", "move", "collect", "forward"]):
            new_frame = apply_forward_motion(new_frame, i)

        # INTERACTION
        if "interact" in option_text:
            new_frame = apply_interaction(new_frame, i)

        # STUMBLE
        if any(word in option_text for word in ["balance", "stumble", "fall"]):
            new_frame = apply_stumble(new_frame, i)

        # slight noise
        noise = np.random.randint(0, 2, new_frame.shape, dtype='uint8')
        new_frame = cv2.add(new_frame, noise)

        out.write(new_frame)
        prev_frame = new_frame.copy()

    out.release()

    print(f"[Task 10] Video saved at: {output_path}")

    return {
        "video_path": output_path,
        "frames_generated": total_frames
    }