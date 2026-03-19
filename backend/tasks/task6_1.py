# ============================================================
# TASK 6.1 : TEMPORAL CONTEXT (YOLO-GROUNDED BLIP CAPTIONING)
# ============================================================

import numpy as np
import torch
import cv2
import time
import gc
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


# ------------------------------------------------------------
# LOAD BLIP
# ------------------------------------------------------------

def load_blip(device):

    print("[Task 6.1] Loading BLIP model...")

    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        use_fast=True
    )

    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    model.to(device)
    model.eval()

    print("[Task 6.1] BLIP ready")

    return processor, model


# ------------------------------------------------------------
# YOLO OBJECT DETECTION
# ------------------------------------------------------------

def detect_objects(frame, yolo_model):

    results = yolo_model(frame)[0]

    objects = set()

    for box in results.boxes:

        cls = int(box.cls[0])
        label = yolo_model.names[cls]

        objects.add(label)

    return list(objects)


# ------------------------------------------------------------
# BLIP CAPTION
# ------------------------------------------------------------

def caption_frame(frame, processor, model, device):

    resized = cv2.resize(frame, (384, 384))
    image = Image.fromarray(resized[:, :, ::-1])

    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=25
        )

    caption = processor.decode(output[0], skip_special_tokens=True)
    caption = caption.lower().strip()

    del inputs
    del output
    gc.collect()

    if device == "mps":
        torch.mps.empty_cache()

    return caption


# ------------------------------------------------------------
# CLEAN CAPTION
# ------------------------------------------------------------

def clean_caption(caption):

    if caption is None:
        return None

    words = caption.split()

    if len(words) < 3:
        return None

    unique_ratio = len(set(words)) / max(len(words), 1)

    if unique_ratio < 0.45:
        return None

    cleaned = []
    prev = None

    for w in words:
        if w != prev:
            cleaned.append(w)
        prev = w

    return " ".join(cleaned)


# ------------------------------------------------------------
# EXTRACT ACTION FROM BLIP
# ------------------------------------------------------------

def extract_action(caption):

    if caption is None:
        return None

    banned_words = {
        "a","an","the","this","that","these","those",
        "he","she","they","them","their","his","her",
        "person","man","woman","boy","girl",
        "cat","dog","animal","someone","something"
    }

    tokens = caption.split()

    action_words = [t for t in tokens if t not in banned_words]

    if len(action_words) == 0:
        return None

    return " ".join(action_words[:6])


# ------------------------------------------------------------
# BUILD FINAL CAPTION
# ------------------------------------------------------------

def grounded_caption(blip_caption, objects):

    action_text = extract_action(blip_caption)

    subject = None

    if len(objects) > 0:
        subject = objects[0]

    if subject and action_text:
        return f"{subject} {action_text}"

    if subject:
        return f"scene containing {subject}"

    return action_text


# ------------------------------------------------------------
# MERGE CONTEXT
# ------------------------------------------------------------

def merge_summaries(previous_summary, new_caption):

    if new_caption is None:
        return previous_summary

    if previous_summary is None:
        return new_caption

    if new_caption in previous_summary:
        return previous_summary

    merged = previous_summary + ". " + new_caption

    words = merged.split()

    if len(words) > 70:
        merged = " ".join(words[-70:])

    return merged


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------

def sample_frames_for_understanding(
        frames,
        fps,
        yolo_model,
        device="cpu"):

    print("\n[Task 6.1] Starting Frame Sampling Controller...")

    task_start_time = time.time()

    total_frames = len(frames)
    video_seconds = total_frames / fps

    print(f"[Task 6.1] Video Length: {video_seconds:.2f} seconds")

    processor, model = load_blip(device)

    if video_seconds <= 5:
        return None, frames


    # ------------------------------------------------------------
    # SPLIT VIDEO
    # ------------------------------------------------------------

    last_5_frame_count = int(fps * 5)

    early_frames = frames[:-last_5_frame_count]
    last_5_seconds_frames = frames[-last_5_frame_count:]

    print(f"[Task 6.1] Early frames: {len(early_frames)}")
    print(f"[Task 6.1] Last 5 seconds frames: {len(last_5_seconds_frames)}")


    # ------------------------------------------------------------
    # SAMPLE FRAMES
    # ------------------------------------------------------------

    step = int(fps)

    context_frames = []

    for i in range(0, len(early_frames), step):

        frame = early_frames[i]

        if isinstance(frame, np.ndarray):
            context_frames.append(frame)

    print(f"[Task 6.1] Context frames sampled: {len(context_frames)}")


    final_context_summary = None

    print("\n[Task 6.1] Generating context summary...")


    for i, frame in enumerate(context_frames):

        start = time.time()

        blip_caption = caption_frame(frame, processor, model, device)

        cleaned = clean_caption(blip_caption)

        objects = detect_objects(frame, yolo_model)

        caption = grounded_caption(cleaned, objects)

        final_context_summary = merge_summaries(
            final_context_summary,
            caption
        )

        print(f"[Frame {i+1} Caption] {blip_caption}")
        print(f"[Objects] {objects}")
        print(f"[Summary] {caption}")
        print(f"[Frame Time] {time.time()-start:.2f} sec")


    print("\n[Task 6.1] Context Summary Completed")

    return final_context_summary, last_5_seconds_frames