# ============================================================
# LLaVA AUTO FRAME LIMIT TEST
# Finds maximum frames your system can process at once
# ============================================================

import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoProcessor, LlavaNextForConditionalGeneration


MODEL_ID = "llava-hf/llava-v1.6-mistral-7b-hf"
VIDEO_PATH = "test.mp4"


# ------------------------------------------------------------
# LOAD VIDEO
# ------------------------------------------------------------
def load_frames(video_path):

    cap = cv2.VideoCapture(video_path)

    frames = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frames.append(frame)

    cap.release()

    print(f"[INFO] Loaded {len(frames)} frames")

    return frames


# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------
def load_model(device):

    print("[INFO] Loading LLaVA model...")

    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        use_fast=False
    )

    model = LlavaNextForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        low_cpu_mem_usage=True
    )

    model.to(device)
    model.eval()

    print("[INFO] Model ready")

    return processor, model


# ------------------------------------------------------------
# TEST FRAME COUNT
# ------------------------------------------------------------
def test_frame_count(frames, n, processor, model, device):

    selected = frames[:n]

    images = [Image.fromarray(f[:, :, ::-1]) for f in selected]

    prompt = "Describe the scene briefly."

    messages = [{
        "role": "user",
        "content":
        [{"type": "image"} for _ in images] +
        [{"type": "text", "text": prompt}]
    }]

    input_text = processor.apply_chat_template(
        messages,
        add_generation_prompt=True
    )

    inputs = processor(
        text=input_text,
        images=images,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=20,
            do_sample=False
        )

    return True


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    device = "mps" if torch.backends.mps.is_available() else "cpu"

    frames = load_frames(VIDEO_PATH)

    processor, model = load_model(device)

    max_safe = 0

    step = 1

    for n in range(1, len(frames)+1, step):

        print(f"\n[TEST] Trying {n} frames")

        try:

            test_frame_count(frames, n, processor, model, device)

            print(f"[SUCCESS] {n} frames worked")

            max_safe = n

        except RuntimeError as e:

            print(f"[CRASH] at {n} frames")
            print(str(e))

            break

    print("\n==============================")
    print(f"MAX SAFE FRAMES = {max_safe}")
    print("==============================")


if __name__ == "__main__":
    main()