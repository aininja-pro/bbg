"""
Generate per-builder Usage Report XLSM files from the Master Builder List.

Uses a byte-copy + string replacement approach to preserve ALL template elements
including VBA macros, form control buttons, drawings, images, and formatting.
Only the 3 target cells (B6, B7, C7) on the Usage-Reporting sheet are modified
via direct string replacement — no XML parsing, zero risk of mangling the file.

Memory-optimised for constrained environments (Render 2 GB).  All ZIP I/O is
file-backed — Python's heap never holds more than one decompressed entry at a
time, avoiding malloc fragmentation that would otherwise blow past 2 GB over
700+ iterations.
"""

import io
import os
import re
import tempfile
import zipfile
from xml.sax.saxutils import escape

import openpyxl

# The Usage-Reporting sheet is sheet2.xml in the ZIP
SHEET_PATH = "xl/worksheets/sheet2.xml"
WORKBOOK_PATH = "xl/workbook.xml"

# Exact XML byte strings for the 3 cells in the template (verified by inspection).
# Using bytes avoids a decode/encode round-trip on the large sheet XML.
B6_TEMPLATE = b'<c r="B6" s="131"/>'
B7_TEMPLATE = b'<c r="B7" s="2" t="s"><v>44</v></c>'
C7_TEMPLATE = b'<c r="C7" s="2"/>'

_CALC_PR_RE = re.compile(rb'<calcPr([^/]*)/>')


def _make_b6(member_id):
    return f'<c r="B6" s="131"><v>{member_id}</v></c>'.encode()


def _make_b7(builder_name):
    safe = escape(str(builder_name))
    return f'<c r="B7" s="2" t="inlineStr"><is><t>{safe}</t></is></c>'.encode()


def _make_c7(state):
    safe = escape(str(state))
    return f'<c r="C7" s="2" t="inlineStr"><is><t>{safe}</t></is></c>'.encode()


def _build_report_to_file(template_path, xlsm_path, member_id, builder_name, state):
    """Build a single XLSM from the template on disk, write result to xlsm_path.

    All ZIP I/O is file-backed.  The only Python-heap allocations are individual
    decompressed entries (one at a time) and the small replacement byte strings.
    """
    b6 = _make_b6(member_id)
    b7 = _make_b7(builder_name)
    c7 = _make_c7(state)

    with zipfile.ZipFile(template_path, "r") as zin:
        with zipfile.ZipFile(xlsm_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == SHEET_PATH:
                    data = data.replace(B6_TEMPLATE, b6, 1)
                    data = data.replace(B7_TEMPLATE, b7, 1)
                    data = data.replace(C7_TEMPLATE, c7, 1)
                elif item.filename == WORKBOOK_PATH:
                    data = _CALC_PR_RE.sub(rb'<calcPr\1 fullCalcOnLoad="1"/>', data, count=1)

                zout.writestr(item, data)
                del data


def generate_single_report(template_bytes, member_id, builder_name, state):
    """Generate a single XLSM report (legacy interface for standalone use)."""
    # Write template to a temp file for the file-backed path
    tfd, tpath = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_tpl_")
    ofd, opath = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_out_")
    try:
        os.write(tfd, template_bytes)
        os.close(tfd)
        os.close(ofd)
        _build_report_to_file(tpath, opath, member_id, builder_name, state)
        with open(opath, "rb") as f:
            return f.read()
    finally:
        for p in (tpath, opath):
            try:
                os.unlink(p)
            except OSError:
                pass


def parse_master_list(master_list_bytes):
    """
    Parse the Master Builder List XLSX and return validated builder rows.

    Returns (builders, warnings) where:
      - builders: list of dicts with member_id, builder_name, state, file_name
      - warnings: list of human-readable warning strings for skipped rows
    """
    wb = openpyxl.load_workbook(io.BytesIO(master_list_bytes), data_only=True)
    ws = wb.active

    builders = []
    warnings = []

    for row_num, row in enumerate(ws.iter_rows(min_row=2, max_col=6, values_only=True), start=2):
        member_id, builder_name, state, name, tm, file_name = row

        # Skip completely empty rows
        if member_id is None and builder_name is None:
            continue

        # Validate required fields
        missing = []
        if member_id is None:
            missing.append("Member ID")
        if builder_name is None:
            missing.append("Builder Name")
        if state is None:
            missing.append("State")
        if file_name is None:
            missing.append("File Name")

        if missing:
            warnings.append(f"Row {row_num}: Skipped — missing {', '.join(missing)}")
            continue

        builders.append({
            "member_id": member_id,
            "builder_name": str(builder_name),
            "state": str(state),
            "file_name": str(file_name),
        })

    wb.close()
    return builders, warnings


def generate_all_reports(master_list_bytes, template_bytes, on_progress=None):
    """
    Orchestrate full report generation: parse the master list, generate each
    report sequentially, and bundle everything into a single ZIP on disk.

    Memory profile: the template lives on disk as a temp file.  Each builder's
    XLSM is written to a reusable temp file then copied into the outer ZIP.
    Python's heap never holds more than one decompressed ZIP entry at a time.

    Args:
        on_progress: optional callback(files_generated: int) called after each
                     builder so the caller can report live progress.
    """
    # Parse the master list then free the bytes
    builders, warnings = parse_master_list(master_list_bytes)
    del master_list_bytes

    if not builders:
        return {
            "success": False,
            "zip_path": None,
            "files_generated": 0,
            "rows_skipped": len(warnings),
            "warnings": warnings or ["No valid builder rows found in the Master Builder List."],
        }

    # Write template to a temp file so all ZIP reads are file-backed
    tpl_fd, tpl_path = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_tpl_")
    os.write(tpl_fd, template_bytes)
    os.close(tpl_fd)
    del template_bytes

    # Reusable temp file for each inner XLSM
    xlsm_fd, xlsm_path = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_xlsm_")
    os.close(xlsm_fd)

    # Outer ZIP written to disk
    zip_fd, zip_path = tempfile.mkstemp(suffix=".zip", prefix="bbg_reports_")
    os.close(zip_fd)

    try:
        files_generated = 0

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zout:
            for builder in builders:
                try:
                    _build_report_to_file(
                        tpl_path,
                        xlsm_path,
                        builder["member_id"],
                        builder["builder_name"],
                        builder["state"],
                    )
                    # Add the file-backed XLSM to the outer ZIP (no Python bytes copy)
                    zout.write(xlsm_path, arcname=f"{builder['file_name']}.xlsm")
                    files_generated += 1

                    if on_progress:
                        on_progress(files_generated)
                except Exception as exc:
                    warnings.append(
                        f"Row for '{builder['builder_name']}' (ID {builder['member_id']}): "
                        f"Failed to generate report — {exc}"
                    )
    except Exception:
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        raise
    finally:
        # Clean up working temp files
        for p in (tpl_path, xlsm_path):
            try:
                os.unlink(p)
            except OSError:
                pass

    if files_generated == 0:
        os.unlink(zip_path)
        zip_path = None

    return {
        "success": files_generated > 0,
        "zip_path": zip_path,
        "files_generated": files_generated,
        "rows_skipped": len(warnings),
        "warnings": warnings,
    }
