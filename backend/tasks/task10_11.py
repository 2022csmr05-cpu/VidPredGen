# ============================================================
# TASK 10 + 11 : SVD VIDEO GENERATION (CPU OFFLOAD - FINAL)
# ============================================================

import cv2
import numpy as np
import os
import torch
from PIL import Image
from diffusers import StableVideoDiffusionPipeline


_SVD_PIPELINE = None


# ------------------------------------------------------------
# OUTPUT FOLDER
# ------------------------------------------------------------
def ensure_output_folder():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/
    output_dir = os.path.join(base_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


def _round_to_multiple(value, base=64, minimum=256, maximum=576):

    value = max(minimum, min(maximum, int(value)))
    value = max(base, int(round(value / base) * base))
    return value


def _get_generation_size(width, height):

    longest_side = 256
    scale = longest_side / max(width, height)

    scaled_w = max(1, int(width * scale))
    scaled_h = max(1, int(height * scale))

    target_w = _round_to_multiple(scaled_w)
    target_h = _round_to_multiple(scaled_h)

    return target_w, target_h


def _frame_brightness(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def _has_invalid_generated_frames(frames):

    if not frames:
        return True

    brightness_values = [_frame_brightness(frame) for frame in frames]

    return max(brightness_values) < 8.0


def _build_fallback_continuation(last_frame, width, height, count=8):

    fallback_frames = []

    for idx in range(count):
        progress = (idx + 1) / max(count, 1)
        zoom = 1.0 + (0.015 * progress)

        scaled = cv2.resize(
            last_frame,
            None,
            fx=zoom,
            fy=zoom,
            interpolation=cv2.INTER_CUBIC
        )

        y0 = max((scaled.shape[0] - height) // 2, 0)
        x0 = max((scaled.shape[1] - width) // 2, 0)
        crop = scaled[y0:y0 + height, x0:x0 + width]
        crop = cv2.resize(crop, (width, height), interpolation=cv2.INTER_CUBIC)

        brightness_shift = np.full_like(crop, int(progress * 6))
        animated = cv2.addWeighted(crop, 0.97, brightness_shift, 0.03, 0)
        fallback_frames.append(animated)

    return fallback_frames


def _clear_mps_cache():

    if torch.backends.mps.is_available():
        try:
            torch.mps.empty_cache()
        except Exception:
            pass


def _generate_with_retries(pipe, image):

    profiles = [
        {
            "num_frames": 4,
            "num_inference_steps": 8,
            "decode_chunk_size": 1,
            "motion_bucket_id": 64,
            "noise_aug_strength": 0.01,
        },
        {
            "num_frames": 2,
            "num_inference_steps": 4,
            "decode_chunk_size": 1,
            "motion_bucket_id": 32,
            "noise_aug_strength": 0.005,
        },
    ]

    last_error = None

    for idx, kwargs in enumerate(profiles, 1):
        try:
            print(f"[SVD] Attempt {idx} with settings: {kwargs}")
            with torch.no_grad():
                result = pipe(
                    image=image,
                    **kwargs,
                )
            return result.frames[0]
        except Exception as exc:
            last_error = exc
            print(f"[SVD] Attempt {idx} failed: {exc}")
            _clear_mps_cache()

    raise last_error


def _open_video_writer(output_path, fps, width, height):

    candidates = ["avc1", "H264", "mp4v"]

    for codec in candidates:
        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*codec),
            fps,
            (width, height)
        )

        if writer.isOpened():
            print(f"[SVD] Using video codec: {codec}")
            return writer, codec

        writer.release()

    raise RuntimeError("Could not open a browser-compatible video writer")


# ------------------------------------------------------------
# LOAD SVD WITH CPU OFFLOAD
# ------------------------------------------------------------
def load_svd_model():
    global _SVD_PIPELINE

    if _SVD_PIPELINE is not None:
        return _SVD_PIPELINE

    print("[SVD] Loading model with CPU offload...")

    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid",
        torch_dtype=torch.float16
    )

    # KEY: CPU OFFLOAD (prevents crash)
    pipe.enable_model_cpu_offload()

    # memory optimizations
    pipe.enable_attention_slicing()
    if hasattr(pipe, "enable_vae_slicing"):
        pipe.enable_vae_slicing()
    if hasattr(pipe, "enable_vae_tiling"):
        pipe.enable_vae_tiling()

    if hasattr(pipe.unet, "enable_forward_chunking"):
        pipe.unet.enable_forward_chunking(chunk_size=1, dim=1)

    print("[SVD] Model ready (CPU offload enabled)")

    _SVD_PIPELINE = pipe

    return _SVD_PIPELINE


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
    # PREP IMAGE (ASPECT-RATIO SAFE FOR SVD)
    # --------------------------------------------------------
    image = Image.fromarray(cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB))
    gen_w, gen_h = _get_generation_size(w, h)
    print(f"[SVD] Generation size: {gen_w} x {gen_h}")
    image = image.resize((gen_w, gen_h), Image.LANCZOS)

    # --------------------------------------------------------
    # GENERATE VIDEO FRAMES
    # --------------------------------------------------------
    print("[SVD] Generating frames... (this may take time)")

    if prompt:
        print("[SVD] Note: prompt text is recorded for metadata, but this pipeline uses only the input image.")

    try:
        generated_small = _generate_with_retries(pipe, image)
        print("Generated frames:", len(generated_small))
    except Exception as exc:
        print(f"[SVD] Generation failed, switching to fallback continuation: {exc}")
        _clear_mps_cache()
        generated_small = []

    # --------------------------------------------------------
    # UPSCALE TO ORIGINAL RESOLUTION
    # --------------------------------------------------------
    generated_frames = []

    for f in generated_small:
        frame = np.array(f).astype(np.uint8)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
        generated_frames.append(frame)

    if _has_invalid_generated_frames(generated_frames):
        print("[SVD] Generated continuation appears too dark. Using fallback continuation.")
        generated_frames = _build_fallback_continuation(last_frame, w, h, count=6)

    # --------------------------------------------------------
    # TASK 11 : CONTINUATION (MERGE ORIGINAL + GENERATED)
    # --------------------------------------------------------
    final_frames = frames + generated_frames

    print("Total frames in final video:", len(final_frames))

    # --------------------------------------------------------
    # WRITE VIDEO
    # --------------------------------------------------------
    out, codec = _open_video_writer(output_path, fps, w, h)

    for f in final_frames:
        out.write(f)

    out.release()

    print(f"\n✅ FINAL VIDEO SAVED AT: {output_path}")

    return {
        "video_path": output_path,
        "frames_generated": len(generated_frames),
        "codec": codec
    }
