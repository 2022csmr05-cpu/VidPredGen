# ============================================================
# TASK 11 : FINAL VIDEO MERGE
# ============================================================

import cv2
import os


def merge_videos(
    input_video_path,
    generated_video_path,
    output_filename="final_output.mp4"
):

    print("\n[Task 11] Merging videos...")

    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_filename)

    cap1 = cv2.VideoCapture(input_video_path)
    cap2 = cv2.VideoCapture(generated_video_path)

    fps = int(cap1.get(cv2.CAP_PROP_FPS))
    w = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps if fps > 0 else 12,
        (w, h)
    )

    # Write original video
    while True:
        ret, frame = cap1.read()
        if not ret:
            break
        out.write(frame)

    # Write generated video
    while True:
        ret, frame = cap2.read()
        if not ret:
            break

        frame = cv2.resize(frame, (w, h))
        out.write(frame)

    cap1.release()
    cap2.release()
    out.release()

    print(f"[Task 11] Final video saved at: {output_path}")

    return output_path