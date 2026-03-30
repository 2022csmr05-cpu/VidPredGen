# ============================================================
# FastAPI backend for VideoGenerationAI
# ============================================================

import os
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .pipeline import generate_video_for_analysis, run_analysis
from .tasks.task3 import load_media


ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(title="VideoGenerationAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory job store; simple and non-persistent.
JOBS = {}


def _run_analysis_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return

    def update_progress(pct):
        job["progress"] = min(100, max(0, int(pct)))

    try:
        analysis = run_analysis(job["file_path"], status_callback=update_progress)
        job["analysis"] = analysis
        job["status"] = "done"
        job["progress"] = 100
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    """Upload a file and start the analysis pipeline."""
    suffix = Path(file.filename).suffix or ".mp4"
    job_id = uuid.uuid4().hex
    save_path = INPUT_DIR / f"{job_id}{suffix}"

    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Run minimal analysis to get fps + type quickly.
    frames, fps, input_type = load_media(str(save_path))

    JOBS[job_id] = {
        "id": job_id,
        "file_path": str(save_path),
        "status": "running",
        "progress": 10,
        "fps": fps,
        "input_type": input_type,
    }

    thread = threading.Thread(target=_run_analysis_job, args=(job_id,), daemon=True)
    thread.start()

    return {
        "analysisId": job_id,
        "fps": fps,
        "inputType": input_type,
        "status": "running",
    }


@app.get("/api/status/{analysis_id}")
def status(analysis_id: str):
    job = JOBS.get(analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "analysisId": analysis_id,
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "fps": job.get("fps"),
        "inputType": job.get("input_type"),
    }

    if job.get("status") == "done":
        analysis = job.get("analysis", {})
        response.update({
            "summary": analysis.get("final_reasoning"),
            "futureOptions": analysis.get("future_output", {}).get("future_options", []),
        })

    if job.get("status") == "error":
        response["error"] = job.get("error")

    return response


@app.post("/api/generate")
def generate(analysisId: str, optionId: int):
    """Generate an output video for a selected future option."""
    job = JOBS.get(analysisId)
    if not job or job.get("status") != "done":
        raise HTTPException(status_code=400, detail="Analysis not completed or job not found")

    analysis = job["analysis"]
    out_name = f"output_{analysisId}.mp4"

    result = generate_video_for_analysis(analysis, optionId, output_filename=out_name)
    job["output"] = result

    return {
        "outputUrl": f"/output/{out_name}",
        "prompt": result.get("prompt"),
    }


@app.get("/output/{filename}")
def get_output(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
