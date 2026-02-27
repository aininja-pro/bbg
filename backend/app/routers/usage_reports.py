"""API endpoints for generating per-builder Usage Report XLSM files.

Uses a background-job pattern so the POST returns immediately with a job_id.
The frontend polls GET /status/{job_id} until complete, then fetches the ZIP
from GET /download/{job_id}.  This avoids Render's request-timeout limit.
"""

import os
import shutil
import threading
import tempfile
import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.services.usage_report_generator import generate_all_reports

router = APIRouter(prefix="/api", tags=["Usage Reports"])
logger = logging.getLogger(__name__)

# In-memory job store.  Keyed by job_id (str).
# Values: {"status": "processing"|"complete"|"failed",
#          "zip_path": str|None, "files_generated": int,
#          "rows_skipped": int, "warnings": list, "error": str|None}
_jobs: dict = {}
_jobs_lock = threading.Lock()


def _remove_path(path: str | None) -> None:
    if not path:
        return

    try:
        os.unlink(path)
    except OSError:
        pass


def _remove_tree(path: str | None) -> None:
    if path:
        shutil.rmtree(path, ignore_errors=True)


def _copy_upload_to_path(upload: UploadFile, destination_path: str) -> None:
    with open(destination_path, "wb") as destination:
        shutil.copyfileobj(upload.file, destination, length=1024 * 1024)


def _run_generation(job_id: str, master_list_path: str, template_path: str, job_dir: str):
    """Run report generation in a background thread and update the job store."""
    def _on_progress(files_generated):
        with _jobs_lock:
            _jobs[job_id]["files_generated"] = files_generated
        logger.info("Usage report job %s progress update: files_generated=%s", job_id, files_generated)

    try:
        logger.info(
            "Usage report job %s started: master_list_path=%s template_path=%s job_dir=%s",
            job_id,
            master_list_path,
            template_path,
            job_dir,
        )
        result = generate_all_reports(
            master_list_path=master_list_path,
            template_path=template_path,
            job_dir=job_dir,
            on_progress=_on_progress,
        )

        with _jobs_lock:
            _jobs[job_id].update({
                "status": "complete" if result["success"] else "failed",
                "zip_path": result.get("zip_path"),
                "files_generated": result["files_generated"],
                "rows_skipped": result["rows_skipped"],
                "warnings": result["warnings"],
                "error": result["warnings"][0] if not result["success"] and result["warnings"] else None,
            })
        logger.info(
            "Usage report job %s finished: status=%s files_generated=%s rows_skipped=%s warnings=%s",
            job_id,
            "complete" if result["success"] else "failed",
            result["files_generated"],
            result["rows_skipped"],
            len(result["warnings"]),
        )
    except Exception as exc:
        _remove_path(os.path.join(job_dir, "reports.zip"))
        _remove_tree(job_dir)
        with _jobs_lock:
            _jobs[job_id].update({
                "status": "failed",
                "error": str(exc),
                "zip_path": None,
            })
        logger.exception("Usage report job %s crashed", job_id)
    else:
        _remove_path(master_list_path)
        _remove_path(template_path)

        with _jobs_lock:
            status_value = _jobs[job_id]["status"]

        if status_value != "complete":
            _remove_tree(job_dir)


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

    # Create job and kick off background thread
    job_id = str(uuid.uuid4())
    job_dir = tempfile.mkdtemp(prefix=f"bbg_usage_job_{job_id}_")
    master_list_path = os.path.join(job_dir, "master_list.xlsx")
    template_path = os.path.join(job_dir, "template.xlsm")

    try:
        _copy_upload_to_path(master_list, master_list_path)
        _copy_upload_to_path(template, template_path)
    except Exception:
        _remove_tree(job_dir)
        raise
    finally:
        await master_list.close()
        await template.close()

    with _jobs_lock:
        _jobs[job_id] = {
            "status": "processing",
            "zip_path": None,
            "job_dir": job_dir,
            "files_generated": 0,
            "rows_skipped": 0,
            "warnings": [],
            "error": None,
        }

    logger.info(
        "Usage report job %s queued: master_list=%s template=%s job_dir=%s",
        job_id,
        master_list.filename,
        template.filename,
        job_dir,
    )

    thread = threading.Thread(
        target=_run_generation,
        args=(job_id, master_list_path, template_path, job_dir),
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
        _remove_tree(job["job_dir"])
        with _jobs_lock:
            _jobs.pop(job_id, None)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename,
        background=BackgroundTask(_cleanup),
    )
