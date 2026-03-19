# ============================================================
# FULL PIPELINE TEST (TASK 3 → 10) — FINAL FIXED
# ============================================================

from ultralytics import YOLO
import torch

from tasks.task3 import load_media
from tasks.task4 import preprocess_frames
from tasks.task5 import detect_style

from tasks.task6_1 import sample_frames_for_understanding
from tasks.task6_2 import task6_test, load_llava
from tasks.task6_3 import merge_context_and_video_understanding

# TASK 7
from tasks.task7_1 import scene_segmentation
from tasks.task7_2 import actor_object_analysis
from tasks.task7_3 import event_extraction
from tasks.task7_4 import video_intent_analysis
from tasks.task7_5 import future_prediction_7_5

# TASK 8, 9, 10
from tasks.task8 import select_future_option
from tasks.task9 import generate_prompt_from_selection
from tasks.task10 import generate_future_video


def main():

    print("\n================================================")
    print(" FULL PIPELINE: TASK 3 → 10 ")
    print("================================================\n")

    video_path = "test.mp4"

    device = "mps" if torch.backends.mps.is_available() else "cpu"

    # =====================================================
    # TASK 3
    # =====================================================
    frames, fps, input_type = load_media(video_path)

    # =====================================================
    # TASK 4
    # =====================================================
    frames, metadata = preprocess_frames(frames)

    # =====================================================
    # TASK 5
    # =====================================================
    style_output = detect_style(frames)

    print("\n[INFO] Style Detection Output:")
    print(style_output)

    # =====================================================
    # YOLO
    # =====================================================
    print("\n[INFO] Loading YOLO model...")
    yolo_model = YOLO("yolov8n.pt")

    # =====================================================
    # TASK 6.1
    # =====================================================
    context_summary, last_frames = sample_frames_for_understanding(
        frames,
        fps,
        yolo_model,
        device=device
    )

    print("\n[INFO] Context summary generated")
    print(context_summary)

    # =====================================================
    # TASK 6.2
    # =====================================================
    processor, model = load_llava(device)

    video_output = task6_test(
        last_frames,
        yolo_model,
        device=device
    )

    # =====================================================
    # TASK 6.3
    # =====================================================
    final_reasoning = merge_context_and_video_understanding(
        context_summary,
        video_output,
        processor,
        model,
        device
    )

    print("\n========== FINAL VIDEO UNDERSTANDING ==========\n")
    print(final_reasoning)

    detected_objects = video_output["detected_objects"]

    # =====================================================
    # ================= TASK 7 ==============================
    # =====================================================

    print("\n================================================")
    print(" STARTING TASK 7 ANALYSIS ")
    print("================================================\n")

    scenes = scene_segmentation(context_summary, final_reasoning)

    print("\n========== SCENES ==========\n")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene}")

    roles = actor_object_analysis(detected_objects)

    print("\n========== OBJECT SEMANTICS ==========\n")
    print(roles)

    events = event_extraction(scenes)

    print("\n========== EVENTS ==========\n")
    print(events)

    intent = video_intent_analysis(context_summary, final_reasoning)

    print("\n========== VIDEO INTENT ==========\n")
    print(intent)

    # =====================================================
    # ================= TASK 7.5 ============================
    # =====================================================

    print("\n================================================")
    print(" STARTING TASK 7.5 FUTURE PREDICTION ")
    print("================================================\n")

    # 🔥 SAFE FRAME EXTRACTION
    if last_frames and hasattr(last_frames[-1], "shape"):
        last_frame = last_frames[-1]
    else:
        print("[WARNING] Using fallback frame")
        last_frame = frames[-1]

    future_output = future_prediction_7_5(
        style_output,
        final_reasoning,
        scenes,
        roles,
        events,
        intent,
        processor,
        model,
        last_frame=last_frame,
        device=device
    )

    # =====================================================
    # ================= TASK 8 ==============================
    # =====================================================

    print("\n================================================")
    print(" STARTING TASK 8 USER SELECTION ")
    print("================================================\n")

    selected_option = select_future_option(future_output)

    # =====================================================
    # ================= TASK 9 ==============================
    # =====================================================

    print("\n================================================")
    print(" STARTING TASK 9 PROMPT GENERATION ")
    print("================================================\n")

    final_prompt = generate_prompt_from_selection(
        selected_option,
        final_reasoning,
        style_output,
        intent
    )

    print("\n========== FINAL PROMPT ==========\n")
    print(final_prompt["prompt"])

    # =====================================================
    # ================= TASK 10 =============================
    # =====================================================

    print("\n================================================")
    print(" STARTING TASK 10 VIDEO GENERATION ")
    print("================================================\n")

    video_result = generate_future_video(
        frames,                      
        selected_option,
        fps           
    )

    print("\n========== GENERATED VIDEO ==========\n")
    print(video_result)

    # =====================================================
    print("\n================================================")
    print(" FULL PIPELINE COMPLETED SUCCESSFULLY ")
    print("================================================\n")


if __name__ == "__main__":
    main()