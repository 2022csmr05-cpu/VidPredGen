# ============================================================
# TASK 10 + 11 : SVD VIDEO GENERATION (CPU OFFLOAD - FINAL)
# ============================================================

import cv2
import numpy as np
import os
import torch
from PIL import Image
from diffusers import StableVideoDiffusionPipeline


# ------------------------------------------------------------
# OUTPUT FOLDER
# ------------------------------------------------------------
def ensure_output_folder():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/
    output_dir = os.path.join(base_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


# ------------------------------------------------------------
# LOAD SVD WITH CPU OFFLOAD
# ------------------------------------------------------------
def load_svd_model():

    print("[SVD] Loading model with CPU offload...")

    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid",
        torch_dtype=torch.float16
    )

    # KEY: CPU OFFLOAD (prevents crash)
    pipe.enable_model_cpu_offload()

    # memory optimizations
    pipe.enable_attention_slicing()

    if hasattr(pipe.unet, "enable_forward_chunking"):
        pipe.unet.enable_forward_chunking(chunk_size=1, dim=1)

    print("[SVD] Model ready (CPU offload enabled)")

    return pipe


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------
def generate_future_video(
    frames,
    selected_option,
    fps,
    output_filename="final_output.mp4",
    prompt=None
):

    print("\n================================================")
    print(" STARTING TASK 10 + 11 (SVD CPU OFFLOAD) ")
    print("================================================\n")

    if not frames:
        raise ValueError("No frames provided")

    # --------------------------------------------------------
    # OUTPUT PATH
    # --------------------------------------------------------
    output_dir = ensure_output_folder()
    output_path = os.path.join(output_dir, output_filename)

    # --------------------------------------------------------
    # FPS + RESOLUTION
    # --------------------------------------------------------
    fps = int(fps) if fps and fps > 5 else 12
    h, w, _ = frames[0].shape

    print("FPS:", fps)
    print("Resolution:", w, "x", h)

    # --------------------------------------------------------
    # LAST FRAME
    # --------------------------------------------------------
    last_frame = frames[-1]

    if not isinstance(last_frame, np.ndarray):
        raise ValueError("Invalid last frame")

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------
    pipe = load_svd_model()

    # --------------------------------------------------------
    # PREP IMAGE (LOW RES FOR MEMORY SAFETY)
    # --------------------------------------------------------
    image = Image.fromarray(cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB))
    image = image.resize((192, 192))   # SAFE SIZE

    # --------------------------------------------------------
    # GENERATE VIDEO FRAMES
    # --------------------------------------------------------
    print("[SVD] Generating frames... (this may take time)")

    with torch.no_grad():
        result = pipe(
            prompt=prompt or "",
            image=image,
            num_frames=4,               
            num_inference_steps=12,     
            decode_chunk_size=1
        )

    generated_small = result.frames[0]

    print("Generated frames:", len(generated_small))

    # --------------------------------------------------------
    # UPSCALE TO ORIGINAL RESOLUTION
    # --------------------------------------------------------
    generated_frames = []

    for f in generated_small:
        frame = np.array(f).astype(np.uint8)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
        generated_frames.append(frame)

    # --------------------------------------------------------
    # TASK 11 : CONTINUATION (MERGE ORIGINAL + GENERATED)
    # --------------------------------------------------------
    final_frames = frames + generated_frames

    print("Total frames in final video:", len(final_frames))

    # --------------------------------------------------------
    # WRITE VIDEO
    # --------------------------------------------------------
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    for f in final_frames:
        out.write(f)

    out.release()

    print(f"\n✅ FINAL VIDEO SAVED AT: {output_path}")

    return {
        "video_path": output_path,
        "frames_generated": len(generated_frames)
    }