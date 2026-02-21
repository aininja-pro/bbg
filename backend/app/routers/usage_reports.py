"""API endpoint for generating per-builder Usage Report XLSM files."""

import io
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse

from app.services.usage_report_generator import generate_all_reports

router = APIRouter(prefix="/api", tags=["Usage Reports"])


@router.post("/generate-reports")
async def generate_reports(
    master_list: UploadFile = File(...),
    template: UploadFile = File(...),
):
    """Generate per-builder Usage Report XLSM files.

    Accepts a Master Builder List (.xlsx) and a template (.xlsm),
    returns a ZIP archive containing one XLSM per builder row.
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

    try:
        result = generate_all_reports(master_list_bytes, template_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {exc}",
        )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["warnings"][0] if result["warnings"] else "No reports generated.",
        )

    # Build dynamic filename based on current quarter/year
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    year_short = now.strftime("%y")
    zip_filename = f"BBG_Usage_Reports_Q{quarter}_{year_short}.zip"

    # Pass summary info via custom response headers
    headers = {
        "Content-Disposition": f"attachment; filename={zip_filename}",
        "X-Files-Generated": str(result["files_generated"]),
        "X-Rows-Skipped": str(result["rows_skipped"]),
        "X-Warnings": json.dumps(result["warnings"]),
    }

    return StreamingResponse(
        io.BytesIO(result["zip_bytes"]),
        media_type="application/zip",
        headers=headers,
    )
