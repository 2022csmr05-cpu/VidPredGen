# ============================================================
# TASK 6.3 : MERGE CONTEXT + VIDEO UNDERSTANDING (ROLLING)
# ============================================================

import gc
import time
import torch


def merge_context_and_video_understanding(
        context_summary,
        video_output,
        processor,
        model,
        device="cpu",
        task6_start_time=None):

    print("\n[Task 6_3] Merging context and deep video understanding...")

    task63_start = time.time()

    # ------------------------------------------------------------
    # Context summary from Task 6.1
    # ------------------------------------------------------------

    if context_summary:
        context_text = context_summary
    else:
        context_text = "No earlier context frames were available."

    # ------------------------------------------------------------
    # Video summary from Task 6.2
    # ------------------------------------------------------------

    video_summary = video_output.get("video_summary", "")

    if not video_summary:
        video_summary = "No chunk summaries available."

    # ------------------------------------------------------------
    # Objects + motion
    # ------------------------------------------------------------

    detected_objects = video_output.get("detected_objects", [])
    motion_level = video_output.get("motion_level", "unknown")

    obj_string = ", ".join(sorted(detected_objects)) if detected_objects else "none"

    # ------------------------------------------------------------
    # Final reasoning prompt
    # ------------------------------------------------------------

    prompt = f"""
You are analyzing a video using two levels of understanding.

EARLIER CONTEXT OBSERVATIONS (sampled frames):
{context_text}

VIDEO ACTION SUMMARY:
{video_summary}

Detected objects across the video: {obj_string}
Estimated overall motion: {motion_level}

Create a structured explanation of the entire video.

Use the following sections:

SCENE OVERVIEW
ENVIRONMENT
SUBJECTS
OBJECTS
ACTIONS
EMOTIONS / EXPRESSIONS
MOTION
CAMERA
TEMPORAL FLOW (describe how events evolve)

The explanation should allow someone to understand the video
even without watching it.
"""

    inputs = processor(
        text=prompt,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=400,
            do_sample=False
        )

    decoded = processor.batch_decode(output, skip_special_tokens=True)[0]

    # ------------------------------------------------------------
    # 🔥 ONLY FIX: REMOVE PROMPT FROM OUTPUT
    # ------------------------------------------------------------
    if "SCENE OVERVIEW" in decoded:
        decoded = decoded.split("SCENE OVERVIEW", 1)[-1]
        decoded = "SCENE OVERVIEW" + decoded

    decoded = decoded.strip()

    # ------------------------------------------------------------
    # CLEANUP
    # ------------------------------------------------------------

    del inputs
    del output
    gc.collect()

    if device == "mps":
        torch.mps.empty_cache()

    # ------------------------------------------------------------
    # TIME CALCULATIONS
    # ------------------------------------------------------------

    task63_time = time.time() - task63_start

    print(f"[Task 6_3] Time taken: {task63_time:.2f} sec")

    if task6_start_time is not None:

        total_task6_time = time.time() - task6_start_time

        print(f"[Task 6] TOTAL PIPELINE TIME (6.1 → 6.3): {total_task6_time:.2f} sec")

    print("[Task 6_3] Final merged reasoning generated.")

    return decoded