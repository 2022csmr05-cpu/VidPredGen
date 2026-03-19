# ============================================================
# CONFIGURATION FILE
# Handles device selection and global runtime settings
# ============================================================

import torch

def get_device():
    """
    Detect available hardware acceleration.
    Priority:
    1. Apple MPS (for Mac)
    2. CUDA (for NVIDIA GPU)
    3. CPU fallback
    """
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

DEVICE = get_device()

# Set dtype based on device
DTYPE = torch.float16 if DEVICE in ["cuda", "mps"] else torch.float32

print(f"[CONFIG] Using device: {DEVICE}")
print(f"[CONFIG] Using dtype: {DTYPE}")