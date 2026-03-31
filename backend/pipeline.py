# ============================================================
# FULL PIPELINE TEST (TASK 3 → 10) — FINAL FIXED
# ============================================================

from ultralytics import YOLO
import torch

from .tasks.task3 import load_media
from .tasks.task4 import preprocess_frames
from .tasks.task5 import detect_style

from .tasks.task6_1 import sample_frames_for_understanding
from .tasks.task6_2 import task6_test, load_llava
from .tasks.task6_3 import merge_context_and_video_understanding

# TASK 7
from .tasks.task7_1 import scene_segmentation
from .tasks.task7_2 import actor_object_analysis
from .tasks.task7_3 import event_extraction
from .tasks.task7_4 import video_intent_analysis
from .tasks.task7_5 import future_prediction_7_5

# TASK 8, 9, 10
from .tasks.task8 import select_future_option
from .tasks.task9 import generate_prompt_from_selection
from .tasks.task10_11 import generate_future_video


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
    # TASK 6.2 (SKIP FOR IMAGE)
    # =====================================================

    processor, model = load_llava(device)

    # Detect image input
    is_image_input = (len(frames) == 1)

    if is_image_input:
        print("\n[INFO] Image input detected → Skipping Task 6.2")

        video_output = {
            "video_summary": context_summary,
            "detected_objects": [],
            "motion_level": "static",
            "frames_analyzed": 1,
            "model": "blip-only"
        }

    else:
        video_output = task6_test(
            last_frames,
            yolo_model,
            device=device,
            processor=processor,
            model=model
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


# ---------------------------------------------------------------------------
# PROGRAMMATIC PIPELINE API (for backend integration)
# ---------------------------------------------------------------------------

_MODEL_CACHE = {}


def _get_cached_models(device="cpu"):
    """Load and cache heavy models to avoid reloading between requests."""
    global _MODEL_CACHE

    if "yolo" not in _MODEL_CACHE:
        print("[Pipeline] Loading YOLO model...")
        _MODEL_CACHE["yolo"] = YOLO("yolov8n.pt")

    if "llava" not in _MODEL_CACHE:
        _MODEL_CACHE["processor"], _MODEL_CACHE["model"] = load_llava(device)

    return _MODEL_CACHE["yolo"], _MODEL_CACHE["processor"], _MODEL_CACHE["model"]


def run_analysis(video_path, device=None, status_callback=None):
    """Run analysis steps (Tasks 3 → 7.5) and return structured results."""
    if device is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"

    def progress(p):
        if callable(status_callback):
            status_callback(p)

    progress(10)
    frames, fps, input_type = load_media(video_path)

    progress(25)
    frames, metadata = preprocess_frames(frames)

    progress(35)
    style_output = detect_style(frames)

    progress(45)
    yolo_model, processor, model = _get_cached_models(device)

    context_summary, last_frames = sample_frames_for_understanding(
        frames,
        fps,
        yolo_model,
        device=device
    )

    progress(55)
    is_image_input = len(frames) == 1

    if is_image_input:
        video_output = {
            "video_summary": context_summary,
            "detected_objects": [],
            "motion_level": "static",
            "frames_analyzed": 1,
            "model": "blip-only"
        }
    else:
        video_output = task6_test(
            last_frames,
            yolo_model,
            device=device,
            processor=processor,
            model=model
        )

    progress(65)
    final_reasoning = merge_context_and_video_understanding(
        context_summary,
        video_output,
        processor,
        model,
        device
    )

    progress(70)
    detected_objects = video_output.get("detected_objects", [])

    progress(75)
    scenes = scene_segmentation(context_summary, final_reasoning)

    progress(80)
    roles = actor_object_analysis(detected_objects)

    progress(85)
    events = event_extraction(scenes)

    progress(88)
    intent = video_intent_analysis(context_summary, final_reasoning)

    if last_frames and hasattr(last_frames[-1], "shape"):
        last_frame = last_frames[-1]
    else:
        last_frame = frames[-1]

    progress(92)

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

    progress(98)

    return {
        "frames": frames,
        "fps": fps,
        "input_type": input_type,
        "style_output": style_output,
        "context_summary": context_summary,
        "final_reasoning": final_reasoning,
        "detected_objects": detected_objects,
        "scenes": scenes,
        "roles": roles,
        "events": events,
        "intent": intent,
        "future_output": future_output,
    }


def generate_video_for_analysis(analysis_result, selected_option_id, output_filename=None):
    """Generate an output video given analysis results and a selected option."""
    future_options = analysis_result.get("future_output", {}).get("future_options", [])
    selected_option = next(
        (o for o in future_options if o.get("id") == selected_option_id),
        None
    )

    if not selected_option:
        raise ValueError(f"Invalid option id: {selected_option_id}")

    prompt_data = generate_prompt_from_selection(
        selected_option,
        analysis_result.get("final_reasoning", ""),
        analysis_result.get("style_output", {}),
        analysis_result.get("intent", {}),
    )

    prompt_text = prompt_data.get("prompt") if prompt_data else ""

    out_filename = output_filename or f"output_{selected_option_id}.mp4"

    video_result = generate_future_video(
        analysis_result["frames"],
        selected_option,
        analysis_result.get("fps", 12),
        output_filename=out_filename,
        prompt=prompt_text,
    )

    return {
        "prompt": prompt_text,
        "video_result": video_result,
        "output_filename": out_filename,
    }


if __name__ == "__main__":
    main()

def run_pipeline(video_path, selected_option_id=None, output_filename=None, device=None):
    results = run_analysis(video_path, device=device)
    if selected_option_id is None:
        return results

    generated = generate_video_for_analysis(
        results,
        selected_option_id,
        output_filename=output_filename,
    )

    return {
        'analysis': results,
        'generation': generated,
    }
