# ============================================================
# TASK 6_2 : GENERIC VIDEO UNDERSTANDING (CLEAN OPTIMIZED)
# ============================================================

import os
import gc
import time
import torch
import numpy as np
import cv2
from PIL import Image
from transformers import AutoProcessor, LlavaNextForConditionalGeneration

os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

CHUNK_SIZE = 4


# ------------------------------------------------------------
# FRAME CHUNKING
# ------------------------------------------------------------

def chunk_frames(frames, chunk_size=CHUNK_SIZE):

    chunks = []

    for i in range(0, len(frames), chunk_size):

        chunk = frames[i:i+chunk_size]

        valid = [f for f in chunk if isinstance(f, np.ndarray)]

        if len(valid) == chunk_size:
            chunks.append(valid)

    return chunks


# ------------------------------------------------------------
# MOTION ESTIMATION
# ------------------------------------------------------------

def estimate_motion(frames):

    prev = None
    motion_vals = []

    for f in frames:

        gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

        if prev is not None:
            diff = cv2.absdiff(prev, gray)
            motion_vals.append(np.mean(diff))

        prev = gray

    if not motion_vals:
        return "static"

    avg = np.mean(motion_vals)

    if avg > 20:
        return "high motion"
    elif avg > 8:
        return "moderate motion"
    else:
        return "low motion"


# ------------------------------------------------------------
# YOLO OBJECT DETECTION
# ------------------------------------------------------------

def detect_objects(frames, yolo_model):

    objects = set()

    for frame in frames:

        results = yolo_model(frame)[0]

        for box in results.boxes:

            cls = int(box.cls[0])
            label = yolo_model.names[cls]
            objects.add(label)

    return list(objects)


# ------------------------------------------------------------
# CHUNK SIMILARITY CHECK
# ------------------------------------------------------------

def chunk_is_similar(prev_chunk, curr_chunk, prev_objects, curr_objects, prev_motion, curr_motion):

    if set(prev_objects) != set(curr_objects):
        return False

    if prev_motion != curr_motion:
        return False

    diffs = []

    for f1, f2 in zip(prev_chunk, curr_chunk):

        g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(g1, g2)
        diffs.append(np.mean(diff))

    avg_diff = np.mean(diffs)

    return avg_diff < 6


# ------------------------------------------------------------
# LOAD LLaVA MODEL
# ------------------------------------------------------------

def load_llava(device):

    model_id = "llava-hf/llava-v1.6-mistral-7b-hf"

    print("[Task 6] Loading LLaVA model...")

    processor = AutoProcessor.from_pretrained(model_id, use_fast=False)

    model = LlavaNextForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        low_cpu_mem_usage=True
    )

    model.config.use_cache = False

    model.to(device)
    model.eval()

    print("[Task 6] Model ready")

    return processor, model


# ------------------------------------------------------------
# CHUNK SUMMARIZATION (LLaVA)
# ------------------------------------------------------------

def summarize_chunk(frames, objects, motion, processor, model, device):

    resized = [cv2.resize(f, (336, 336)) for f in frames]
    images = [Image.fromarray(f[:, :, ::-1]) for f in resized]

    obj_string = ", ".join(objects) if objects else "none"

    prompt = f"""
These images are consecutive frames from a short video segment.

Detected objects: {obj_string}
Estimated motion level: {motion}

Describe briefly what is happening across these frames.
Focus on actions and scene changes.
Respond in 1–3 concise sentences.
"""

    messages = [{
        "role": "user",
        "content":
        [{"type": "image"} for _ in images] +
        [{"type": "text", "text": prompt}]
    }]

    text = processor.apply_chat_template(messages, add_generation_prompt=True)

    inputs = processor(text=text, images=images, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=False
        )

    decoded = processor.batch_decode(output, skip_special_tokens=True)[0]

    if "[/INST]" in decoded:
        decoded = decoded.split("[/INST]")[-1]

    decoded = decoded.strip()

    if len(decoded.split()) < 2:
        decoded = "Minimal visible activity."

    del inputs
    del output
    gc.collect()

    if device == "mps":
        torch.mps.empty_cache()

    return decoded


# ------------------------------------------------------------
# SIMPLE SUMMARY MERGE (FAST)
# ------------------------------------------------------------

def merge_summaries(previous, new):

    if previous is None:
        return new

    if new in previous:
        return previous

    if previous in new:
        return new

    merged = previous + " " + new

    words = merged.split()

    if len(words) > 80:
        merged = " ".join(words[-80:])

    return merged


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------

def task6_test(frames, yolo_model, device="cpu"):

    print("\n[Task 6_2] Starting video understanding")

    start_time = time.time()

    chunks = chunk_frames(frames)

    print(f"Total chunks: {len(chunks)}")

    processor, model = load_llava(device)

    rolling_summary = None
    prev_chunk = None
    prev_objects = None
    prev_motion = None
    prev_summary = None

    all_objects = set()
    motion_levels = []

    for i, chunk in enumerate(chunks):

        print(f"\nProcessing chunk {i+1}/{len(chunks)}")

        motion = estimate_motion(chunk)
        motion_levels.append(motion)

        objects = detect_objects(chunk, yolo_model)
        all_objects.update(objects)

        skip = False

        if prev_chunk is not None:

            skip = chunk_is_similar(
                prev_chunk,
                chunk,
                prev_objects,
                objects,
                prev_motion,
                motion
            )

        if skip:

            print("Chunk similar to previous → skipped")

            summary = prev_summary

        else:

            summary = summarize_chunk(
                chunk,
                objects,
                motion,
                processor,
                model,
                device
            )

            prev_summary = summary

        rolling_summary = merge_summaries(
            rolling_summary,
            summary
        )

        print("Chunk summary:", summary)
        print("Rolling summary:", rolling_summary)

        prev_chunk = chunk
        prev_objects = objects
        prev_motion = motion

        gc.collect()

        if device == "mps":
            torch.mps.empty_cache()

    total_time = time.time() - start_time

    print("\n[Task 6_2] Completed")
    print(f"[Task 6_2] Total time: {total_time:.2f} sec")

    return {
        "video_summary": rolling_summary,
        "detected_objects": list(all_objects),
        "motion_level": max(set(motion_levels), key=motion_levels.count),
        "frames_analyzed": len(frames),
        "model": "llava-v1.6-mistral-7b"
    }