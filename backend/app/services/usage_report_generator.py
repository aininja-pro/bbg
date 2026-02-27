"""
Generate per-builder Usage Report XLSM files from the Master Builder List.

Uses a byte-copy + string replacement approach to preserve ALL template elements
including VBA macros, form control buttons, drawings, images, and formatting.
Only the 3 target cells (B6, B7, C7) on the Usage-Reporting sheet are modified
via direct string replacement — no XML parsing, zero risk of mangling the file.

Memory-optimised: streams through the template ZIP entry-by-entry so only one
decompressed entry is in RAM at a time.  The outer ZIP is written to a temp file.
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

# Exact XML strings for the 3 cells in the template (verified by inspection)
B6_TEMPLATE = '<c r="B6" s="131"/>'
B7_TEMPLATE = '<c r="B7" s="2" t="s"><v>44</v></c>'
C7_TEMPLATE = '<c r="C7" s="2"/>'


def make_b6_xml(member_id):
    """Build replacement XML for B6 with a numeric Member ID value."""
    return f'<c r="B6" s="131"><v>{member_id}</v></c>'


def make_b7_xml(builder_name):
    """Build replacement XML for B7 with an inline string builder name."""
    return f'<c r="B7" s="2" t="inlineStr"><is><t>{builder_name}</t></is></c>'


def make_c7_xml(state):
    """Build replacement XML for C7 with an inline string state value."""
    return f'<c r="C7" s="2" t="inlineStr"><is><t>{state}</t></is></c>'


def _build_report(template_bytes, member_id, builder_name, state):
    """Build a single XLSM by streaming through the template ZIP.

    Reads one entry at a time from the template, optionally modifies it,
    and writes it to the output.  Only one decompressed entry is in memory
    at any point — total peak RAM is the size of the largest single entry.
    """
    safe_name = escape(str(builder_name))
    safe_state = escape(str(state))

    output_buffer = io.BytesIO()

    with zipfile.ZipFile(io.BytesIO(template_bytes), "r") as zin:
        with zipfile.ZipFile(output_buffer, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == SHEET_PATH:
                    xml_str = data.decode("utf-8")
                    del data
                    xml_str = xml_str.replace(B6_TEMPLATE, make_b6_xml(member_id), 1)
                    xml_str = xml_str.replace(B7_TEMPLATE, make_b7_xml(safe_name), 1)
                    xml_str = xml_str.replace(C7_TEMPLATE, make_c7_xml(safe_state), 1)
                    data = xml_str.encode("utf-8")
                    del xml_str
                elif item.filename == WORKBOOK_PATH:
                    xml_str = data.decode("utf-8")
                    del data
                    xml_str = re.sub(
                        r'<calcPr([^/]*)/>',
                        r'<calcPr\1 fullCalcOnLoad="1"/>',
                        xml_str,
                        count=1,
                    )
                    data = xml_str.encode("utf-8")
                    del xml_str

                zout.writestr(item, data)
                del data

    xlsm_bytes = output_buffer.getvalue()
    output_buffer.close()
    return xlsm_bytes


def generate_single_report(template_bytes, member_id, builder_name, state):
    """Generate a single XLSM report (legacy interface for standalone use)."""
    return _build_report(template_bytes, member_id, builder_name, state)


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

    Memory profile: only one builder's XLSM is in memory at a time (~1.5 MB).
    The template ZIP (7.6 MB compressed) is re-read from a bytes buffer per
    builder — fast since it's in-memory, and avoids caching 75-150 MB of
    decompressed XML.

    Args:
        on_progress: optional callback(files_generated: int) called after each
                     builder so the caller can report live progress.

    Returns dict with:
      - success: bool
      - zip_path: str (path to temp ZIP file) or None on total failure
      - files_generated: int
      - rows_skipped: int
      - warnings: list of strings
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

    # Create a temp file for the outer ZIP (avoids holding everything in RAM)
    fd, zip_path = tempfile.mkstemp(suffix=".zip", prefix="bbg_reports_")
    os.close(fd)

    try:
        files_generated = 0

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zout:
            for builder in builders:
                try:
                    report_bytes = _build_report(
                        template_bytes,
                        builder["member_id"],
                        builder["builder_name"],
                        builder["state"],
                    )
                    filename = f"{builder['file_name']}.xlsm"
                    zout.writestr(filename, report_bytes)
                    del report_bytes
                    files_generated += 1

                    if on_progress:
                        on_progress(files_generated)
                except Exception as exc:
                    warnings.append(
                        f"Row for '{builder['builder_name']}' (ID {builder['member_id']}): "
                        f"Failed to generate report — {exc}"
                    )
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        raise

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
