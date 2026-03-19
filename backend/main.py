# ============================================================
# MAIN ENTRY POINT
# ============================================================

from pipeline import run_pipeline


if __name__ == "__main__":

    video_path = "test.mp4"  # Change this to your file

    result = run_pipeline(video_path)

    print("\nFinal Output Summary:")
    print(f"Input Type : {result['input_type']}")
    print(f"Style      : {result['style']}")