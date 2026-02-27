"""API endpoints for generating per-builder Usage Report XLSM files."""

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

import app.services.usage_report_generator as usage_report_generator
from app.services.usage_report_generator import (
    STATUS_FILENAME,
    make_job_state,
    read_job_state,
    write_job_state,
)

router = APIRouter(prefix="/api", tags=["Usage Reports"])
logger = logging.getLogger(__name__)


def _job_dir(job_id: str) -> str:
    return os.path.join(tempfile.gettempdir(), f"bbg_usage_job_{job_id}")


def _status_path(job_id: str) -> str:
    return os.path.join(_job_dir(job_id), STATUS_FILENAME)


def _remove_tree(path: str | None) -> None:
    if path:
        shutil.rmtree(path, ignore_errors=True)


def _copy_upload_to_path(upload: UploadFile, destination_path: str) -> None:
    with open(destination_path, "wb") as destination:
        shutil.copyfileobj(upload.file, destination, length=1024 * 1024)


def _load_job(job_id: str):
    status_path = _status_path(job_id)
    if not os.path.exists(status_path):
        return None
    return read_job_state(status_path)


def _run_generation_subprocess(job_id: str, master_list_path: str, template_path: str, job_dir: str, status_path: str):
    command = [
        sys.executable,
        "-u",
        os.path.abspath(usage_report_generator.__file__),
        "run-job",
        "--job-id",
        job_id,
        "--master-list",
        master_list_path,
        "--template",
        template_path,
        "--job-dir",
        job_dir,
        "--status-path",
        status_path,
    ]

    logger.info("Usage report job %s launching worker subprocess", job_id)

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        message = f"job exited with code {exc.returncode}"
        current_state = _load_job(job_id)
        if current_state and current_state["status"] == "processing":
            write_job_state(
                status_path,
                make_job_state(
                    status_value="failed",
                    zip_path=None,
                    files_generated=current_state["files_generated"],
                    rows_skipped=current_state["rows_skipped"],
                    warnings=current_state["warnings"],
                    error=message,
                ),
            )
        logger.error("Usage report job %s subprocess failed: %s", job_id, message)


def _start_background_generation(job_id: str, master_list_path: str, template_path: str, job_dir: str, status_path: str) -> None:
    thread = threading.Thread(
        target=_run_generation_subprocess,
        args=(job_id, master_list_path, template_path, job_dir, status_path),
        daemon=True,
    )
    thread.start()


@router.post("/generate-reports")
async def generate_reports(
    master_list: UploadFile = File(...),
    template: UploadFile = File(...),
):
    """Start per-builder report generation in the background."""
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

    job_id = str(uuid.uuid4())
    job_dir = _job_dir(job_id)
    status_path = _status_path(job_id)
    master_list_path = os.path.join(job_dir, "master_list.xlsx")
    template_path = os.path.join(job_dir, "template.xlsm")

    if os.path.exists(job_dir):
        _remove_tree(job_dir)
    os.makedirs(job_dir, exist_ok=True)

    try:
        _copy_upload_to_path(master_list, master_list_path)
        _copy_upload_to_path(template, template_path)
        write_job_state(status_path, make_job_state(status_value="processing"))
    except Exception:
        _remove_tree(job_dir)
        raise
    finally:
        await master_list.close()
        await template.close()

    logger.info(
        "Usage report job %s queued: master_list=%s template=%s job_dir=%s",
        job_id,
        master_list.filename,
        template.filename,
        job_dir,
    )

    _start_background_generation(job_id, master_list_path, template_path, job_dir, status_path)
    return {"job_id": job_id}


@router.get("/generate-reports/{job_id}/status")
async def report_status(job_id: str):
    """Poll this endpoint until status is 'complete' or 'failed'."""
    job = _load_job(job_id)
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
    """Download the completed ZIP. Cleans up temp files afterward."""
    job = _load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job["status"] != "complete":
        raise HTTPException(status_code=409, detail="Job is not complete yet.")

    zip_path = job["zip_path"]
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(status_code=410, detail="ZIP file no longer available.")

    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    year_short = now.strftime("%y")
    zip_filename = f"BBG_Usage_Reports_Q{quarter}_{year_short}.zip"

    def _cleanup():
        _remove_tree(_job_dir(job_id))

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename,
        background=BackgroundTask(_cleanup),
    )
