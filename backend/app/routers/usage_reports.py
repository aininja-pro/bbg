"""API endpoints for generating per-builder Usage Report XLSM files.

Uses a background-job pattern so the POST returns immediately with a job_id.
The frontend polls GET /status/{job_id} until complete, then fetches the ZIP
from GET /download/{job_id}.  This avoids Render's request-timeout limit.
"""

import os
import threading
import uuid
from datetime import datetime
from functools import partial

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.services.usage_report_generator import generate_all_reports

router = APIRouter(prefix="/api", tags=["Usage Reports"])

# In-memory job store.  Keyed by job_id (str).
# Values: {"status": "processing"|"complete"|"failed",
#          "zip_path": str|None, "files_generated": int,
#          "rows_skipped": int, "warnings": list, "error": str|None}
_jobs: dict = {}
_jobs_lock = threading.Lock()


def _run_generation(job_id: str, master_list_bytes: bytes, template_bytes: bytes):
    """Run report generation in a background thread and update the job store."""
    try:
        result = generate_all_reports(master_list_bytes, template_bytes)

        with _jobs_lock:
            _jobs[job_id].update({
                "status": "complete" if result["success"] else "failed",
                "zip_path": result.get("zip_path"),
                "files_generated": result["files_generated"],
                "rows_skipped": result["rows_skipped"],
                "warnings": result["warnings"],
                "error": result["warnings"][0] if not result["success"] and result["warnings"] else None,
            })
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id].update({
                "status": "failed",
                "error": str(exc),
            })


@router.post("/generate-reports")
async def generate_reports(
    master_list: UploadFile = File(...),
    template: UploadFile = File(...),
):
    """Start per-builder report generation in the background.

    Returns a job_id immediately.  Poll /generate-reports/{job_id}/status
    until status is 'complete', then GET /generate-reports/{job_id}/download.
    """
    # Validate file types
    if not master_list.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master Builder List must be an .xlsx file.",
        )

    if not template.filename.endswith(".xlsm"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template must be an .xlsm file.",
        )

    # Read both files into memory
    master_list_bytes = await master_list.read()
    template_bytes = await template.read()

    # Create job and kick off background thread
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {
            "status": "processing",
            "zip_path": None,
            "files_generated": 0,
            "rows_skipped": 0,
            "warnings": [],
            "error": None,
        }

    thread = threading.Thread(
        target=_run_generation,
        args=(job_id, master_list_bytes, template_bytes),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id}


@router.get("/generate-reports/{job_id}/status")
async def report_status(job_id: str):
    """Poll this endpoint until status is 'complete' or 'failed'."""
    with _jobs_lock:
        job = _jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return {
        "status": job["status"],
        "files_generated": job["files_generated"],
        "rows_skipped": job["rows_skipped"],
        "warnings": job["warnings"],
        "error": job["error"],
    }


@router.get("/generate-reports/{job_id}/download")
async def report_download(job_id: str):
    """Download the completed ZIP.  Cleans up temp file + job entry afterward."""
    with _jobs_lock:
        job = _jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job["status"] != "complete":
        raise HTTPException(status_code=409, detail="Job is not complete yet.")

    zip_path = job["zip_path"]
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(status_code=410, detail="ZIP file no longer available.")

    # Build dynamic filename based on current quarter/year
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    year_short = now.strftime("%y")
    zip_filename = f"BBG_Usage_Reports_Q{quarter}_{year_short}.zip"

    def _cleanup():
        try:
            os.unlink(zip_path)
        except OSError:
            pass
        with _jobs_lock:
            _jobs.pop(job_id, None)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename,
        background=BackgroundTask(_cleanup),
    )
