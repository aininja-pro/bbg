"""
Generate per-builder Usage Report XLSM files from the Master Builder List.

Uses a byte-copy + string replacement approach to preserve ALL template elements
including VBA macros, form control buttons, drawings, images, and formatting.
Only the 3 target cells (B6, B7, C7) on the Usage-Reporting sheet are modified
via direct string replacement — no XML parsing, zero risk of mangling the file.

Adapted from generate_reports.py to run entirely in memory (no disk writes).
"""

import io
import zipfile
from xml.sax.saxutils import escape

import openpyxl

# The Usage-Reporting sheet is sheet2.xml in the ZIP
SHEET_PATH = "xl/worksheets/sheet2.xml"

# Exact XML strings for the 3 cells in the template (verified by inspection)
# B6: empty numeric cell  ->  replace with numeric value
B6_TEMPLATE = '<c r="B6" s="131"/>'
# B7: shared string ref (index 44 = " ")  ->  replace with inline string
B7_TEMPLATE = '<c r="B7" s="2" t="s"><v>44</v></c>'
# C7: empty cell  ->  replace with inline string
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


def generate_single_report(template_bytes, member_id, builder_name, state):
    """
    Generate a single XLSM report by rewriting the ZIP in memory.

    Replaces only the 3 target cell strings in sheet2.xml.
    All other content (buttons, drawings, macros, etc.) is preserved byte-for-byte.

    Returns the modified XLSM file as bytes.
    """
    # Escape XML-special characters in string values
    safe_name = escape(str(builder_name))
    safe_state = escape(str(state))

    output_buffer = io.BytesIO()

    with zipfile.ZipFile(io.BytesIO(template_bytes), "r") as zin:
        with zipfile.ZipFile(output_buffer, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == SHEET_PATH:
                    xml_str = data.decode("utf-8")
                    xml_str = xml_str.replace(B6_TEMPLATE, make_b6_xml(member_id), 1)
                    xml_str = xml_str.replace(B7_TEMPLATE, make_b7_xml(safe_name), 1)
                    xml_str = xml_str.replace(C7_TEMPLATE, make_c7_xml(safe_state), 1)
                    data = xml_str.encode("utf-8")

                zout.writestr(item, data, compress_type=item.compress_type)

    return output_buffer.getvalue()


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


def generate_all_reports(master_list_bytes, template_bytes):
    """
    Orchestrate full report generation: parse the master list, generate each
    report, and bundle everything into a single ZIP file.

    Returns dict with:
      - success: bool
      - zip_bytes: bytes (the ZIP archive) or None on total failure
      - files_generated: int
      - rows_skipped: int
      - warnings: list of strings
    """
    # Parse the master list
    builders, warnings = parse_master_list(master_list_bytes)

    if not builders:
        return {
            "success": False,
            "zip_bytes": None,
            "files_generated": 0,
            "rows_skipped": len(warnings),
            "warnings": warnings or ["No valid builder rows found in the Master Builder List."],
        }

    # Generate reports and bundle into a ZIP
    zip_buffer = io.BytesIO()
    files_generated = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        for builder in builders:
            try:
                report_bytes = generate_single_report(
                    template_bytes,
                    builder["member_id"],
                    builder["builder_name"],
                    builder["state"],
                )
                filename = f"{builder['file_name']}.xlsm"
                zout.writestr(filename, report_bytes)
                files_generated += 1
            except Exception as exc:
                warnings.append(
                    f"Row for '{builder['builder_name']}' (ID {builder['member_id']}): "
                    f"Failed to generate report — {exc}"
                )

    return {
        "success": files_generated > 0,
        "zip_bytes": zip_buffer.getvalue(),
        "files_generated": files_generated,
        "rows_skipped": len(warnings),
        "warnings": warnings,
    }
