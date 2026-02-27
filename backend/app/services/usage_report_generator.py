"""
Generate per-builder Usage Report XLSM files from the Master Builder List.

The generation path is optimized for constrained environments:
- uploads are parsed from disk
- builder reports are created in short-lived subprocess batches
- batch output is staged on disk and zipped incrementally

That keeps the API server process from accumulating allocator fragmentation
across hundreds of XLSM generations on Render's 2 GB instances.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Callable
from xml.sax.saxutils import escape

import openpyxl

logger = logging.getLogger(__name__)

# The Usage-Reporting sheet is sheet2.xml in the ZIP
SHEET_PATH = "xl/worksheets/sheet2.xml"
WORKBOOK_PATH = "xl/workbook.xml"
MANIFEST_FILENAME = "builders.json"
FINAL_ZIP_FILENAME = "reports.zip"
STATUS_FILENAME = "status.json"

# Exact XML byte strings for the 3 cells in the template (verified by inspection).
# Using bytes avoids a decode/encode round-trip on the large sheet XML.
B6_TEMPLATE = b'<c r="B6" s="131"/>'
B7_TEMPLATE = b'<c r="B7" s="2" t="s"><v>44</v></c>'
C7_TEMPLATE = b'<c r="C7" s="2"/>'

_CALC_PR_RE = re.compile(rb'<calcPr([^/]*)/>')


def _get_default_batch_size() -> int:
    try:
        return max(1, int(os.getenv("USAGE_REPORT_BATCH_SIZE", "50")))
    except ValueError:
        logger.warning("Invalid USAGE_REPORT_BATCH_SIZE value %r; defaulting to 20", os.getenv("USAGE_REPORT_BATCH_SIZE"))
        return 20


DEFAULT_BATCH_SIZE = _get_default_batch_size()


def _make_b6(member_id):
    return f'<c r="B6" s="131"><v>{member_id}</v></c>'.encode()


def _make_b7(builder_name):
    safe = escape(str(builder_name))
    return f'<c r="B7" s="2" t="inlineStr"><is><t>{safe}</t></is></c>'.encode()


def _make_c7(state):
    safe = escape(str(state))
    return f'<c r="C7" s="2" t="inlineStr"><is><t>{safe}</t></is></c>'.encode()


def _build_report_to_file(template_path, xlsm_path, member_id, builder_name, state):
    """Build a single XLSM from the template on disk, write result to xlsm_path."""
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


def generate_single_report(template_bytes, member_id, builder_name, state):
    """Generate a single XLSM report (legacy interface for standalone use)."""
    tfd, tpath = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_tpl_")
    ofd, opath = tempfile.mkstemp(suffix=".xlsm", prefix="bbg_out_")
    try:
        os.write(tfd, template_bytes)
        os.close(tfd)
        os.close(ofd)
        _build_report_to_file(tpath, opath, member_id, builder_name, state)
        with open(opath, "rb") as generated_file:
            return generated_file.read()
    finally:
        for path in (tpath, opath):
            try:
                os.unlink(path)
            except OSError:
                pass


def parse_master_list(master_list_path):
    """
    Parse the Master Builder List XLSX on disk and return validated builder rows.

    Returns (builders, warnings) where:
      - builders: list of dicts with member_id, builder_name, state, file_name
      - warnings: list of human-readable warning strings for skipped rows
    """
    wb = openpyxl.load_workbook(master_list_path, data_only=True, read_only=True)
    ws = wb.active

    builders = []
    warnings = []

    for row_num, row in enumerate(ws.iter_rows(min_row=2, max_col=6, values_only=True), start=2):
        member_id, builder_name, state, _name, _tm, file_name = row

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
            warnings.append(f"Row {row_num}: Skipped - missing {', '.join(missing)}")
            continue

        builders.append({
            "member_id": member_id,
            "builder_name": str(builder_name),
            "state": str(state),
            "file_name": str(file_name),
        })

    wb.close()
    return builders, warnings


def _write_json(path: str, payload) -> None:
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file)
    os.replace(temp_path, path)


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def make_job_state(
    *,
    status_value: str,
    zip_path: str | None = None,
    files_generated: int = 0,
    rows_skipped: int = 0,
    warnings: list[str] | None = None,
    error: str | None = None,
):
    return {
        "status": status_value,
        "zip_path": zip_path,
        "files_generated": files_generated,
        "rows_skipped": rows_skipped,
        "warnings": warnings or [],
        "error": error,
    }


def read_job_state(status_path: str):
    return _read_json(status_path)


def write_job_state(status_path: str, payload) -> None:
    _write_json(status_path, payload)


def update_job_state(status_path: str, **updates):
    state = read_job_state(status_path)
    state.update(updates)
    write_job_state(status_path, state)
    return state


def _load_builders_slice(manifest_path: str, start: int, end: int):
    builders = _read_json(manifest_path)
    return builders[start:end]


def _batch_result_path(job_dir: str, batch_index: int) -> str:
    return os.path.join(job_dir, f"batch_{batch_index:04d}.json")


def _batch_output_dir(job_dir: str, batch_index: int) -> str:
    return os.path.join(job_dir, f"batch_{batch_index:04d}")


def _run_batch_subprocess(
    template_path: str,
    manifest_path: str,
    output_dir: str,
    result_path: str,
    start: int,
    end: int,
) -> dict:
    command = [
        sys.executable,
        "-u",
        os.path.abspath(__file__),
        "batch",
        "--template",
        template_path,
        "--manifest",
        manifest_path,
        "--output-dir",
        output_dir,
        "--result-path",
        result_path,
        "--start",
        str(start),
        "--end",
        str(end),
    ]

    logger.info(
        "Launching usage report batch subprocess for builders %s-%s",
        start + 1,
        end,
    )

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        message = f"batch exited with code {exc.returncode}"
        logger.error(
            "Usage report batch subprocess failed for builders %s-%s: %s",
            start + 1,
            end,
            message,
        )
        raise RuntimeError(message) from exc

    if not os.path.exists(result_path):
        raise RuntimeError("batch completed without a result file")

    return _read_json(result_path)


def _write_batch_reports(
    template_path: str,
    manifest_path: str,
    output_dir: str,
    start: int,
    end: int,
) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    builders = _load_builders_slice(manifest_path, start, end)

    warnings = []
    generated_files = []

    for builder in builders:
        output_name = f"{builder['file_name'].replace('/', '-')}.xlsm"
        output_path = os.path.join(output_dir, output_name)

        try:
            _build_report_to_file(
                template_path,
                output_path,
                builder["member_id"],
                builder["builder_name"],
                builder["state"],
            )
            generated_files.append(output_name)
        except Exception as exc:
            warnings.append(
                f"Row for '{builder['builder_name']}' (ID {builder['member_id']}): "
                f"Failed to generate report - {exc}"
            )

    return {
        "files_generated": len(generated_files),
        "generated_files": generated_files,
        "warnings": warnings,
    }


def generate_all_reports(
    master_list_path: str,
    template_path: str,
    job_dir: str,
    on_progress: Callable[[int], None] | None = None,
    batch_size: int | None = None,
):
    """
    Orchestrate full report generation from disk-backed inputs.

    Each batch runs in a short-lived subprocess and writes its XLSMs into a
    batch directory. The parent process then streams those files into the final
    ZIP and deletes the batch directory before launching the next subprocess.
    """
    os.makedirs(job_dir, exist_ok=True)

    builders, warnings = parse_master_list(master_list_path)
    logger.info(
        "Usage report job staging complete: builders=%s skipped_rows=%s batch_size=%s job_dir=%s",
        len(builders),
        len(warnings),
        max(1, batch_size or DEFAULT_BATCH_SIZE),
        job_dir,
    )
    if not builders:
        return {
            "success": False,
            "zip_path": None,
            "files_generated": 0,
            "rows_skipped": len(warnings),
            "warnings": warnings or ["No valid builder rows found in the Master Builder List."],
        }

    manifest_path = os.path.join(job_dir, MANIFEST_FILENAME)
    _write_json(manifest_path, builders)

    zip_path = os.path.join(job_dir, FINAL_ZIP_FILENAME)
    effective_batch_size = max(1, batch_size or DEFAULT_BATCH_SIZE)
    files_generated = 0
    total_batches = (len(builders) + effective_batch_size - 1) // effective_batch_size

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as batch_archive:
            for batch_index, start in enumerate(range(0, len(builders), effective_batch_size)):
                end = min(start + effective_batch_size, len(builders))
                output_dir = _batch_output_dir(job_dir, batch_index)
                result_path = _batch_result_path(job_dir, batch_index)
                batch_number = batch_index + 1

                logger.info(
                    "Usage report batch %s/%s starting: builders=%s-%s current_files_generated=%s",
                    batch_number,
                    total_batches,
                    start + 1,
                    end,
                    files_generated,
                )

                try:
                    batch_result = _run_batch_subprocess(
                        template_path=template_path,
                        manifest_path=manifest_path,
                        output_dir=output_dir,
                        result_path=result_path,
                        start=start,
                        end=end,
                    )
                finally:
                    try:
                        os.unlink(result_path)
                    except OSError:
                        pass

                warnings.extend(batch_result["warnings"])

                for output_name in batch_result["generated_files"]:
                    output_path = os.path.join(output_dir, output_name)
                    if os.path.exists(output_path):
                        batch_archive.write(output_path, arcname=output_name)

                files_generated += batch_result["files_generated"]
                if on_progress:
                    on_progress(files_generated)

                logger.info(
                    "Usage report batch %s/%s complete: batch_files=%s total_files=%s batch_warnings=%s",
                    batch_number,
                    total_batches,
                    batch_result["files_generated"],
                    files_generated,
                    len(batch_result["warnings"]),
                )

                shutil.rmtree(output_dir, ignore_errors=True)
    except Exception:
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        raise
    finally:
        try:
            os.unlink(manifest_path)
        except OSError:
            pass

    if files_generated == 0:
        os.unlink(zip_path)
        zip_path = None

    logger.info(
        "Usage report job finished: success=%s files_generated=%s rows_skipped=%s zip_path=%s",
        files_generated > 0,
        files_generated,
        len(warnings),
        zip_path,
    )

    return {
        "success": files_generated > 0,
        "zip_path": zip_path,
        "files_generated": files_generated,
        "rows_skipped": len(warnings),
        "warnings": warnings,
    }


def run_generation_job(
    job_id: str,
    master_list_path: str,
    template_path: str,
    job_dir: str,
    status_path: str,
) -> int:
    def _on_progress(files_generated):
        update_job_state(status_path, files_generated=files_generated)
        logger.info("Usage report job %s progress update: files_generated=%s", job_id, files_generated)

    try:
        logger.info(
            "Usage report job %s started in subprocess: master_list_path=%s template_path=%s job_dir=%s",
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
        final_status = "complete" if result["success"] else "failed"
        write_job_state(
            status_path,
            make_job_state(
                status_value=final_status,
                zip_path=result.get("zip_path"),
                files_generated=result["files_generated"],
                rows_skipped=result["rows_skipped"],
                warnings=result["warnings"],
                error=result["warnings"][0] if final_status == "failed" and result["warnings"] else None,
            ),
        )
        logger.info(
            "Usage report job %s finished in subprocess: status=%s files_generated=%s rows_skipped=%s warnings=%s",
            job_id,
            final_status,
            result["files_generated"],
            result["rows_skipped"],
            len(result["warnings"]),
        )
        return 0
    except Exception as exc:
        write_job_state(
            status_path,
            make_job_state(
                status_value="failed",
                zip_path=None,
                warnings=[],
                error=str(exc),
            ),
        )
        logger.exception("Usage report job %s crashed in subprocess", job_id)
        return 1
    finally:
        for path in (master_list_path, template_path):
            try:
                os.unlink(path)
            except OSError:
                pass


def _parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(description="Usage report batch worker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    batch_parser = subparsers.add_parser("batch", help="Generate one batch of XLSM files")
    batch_parser.add_argument("--template", required=True)
    batch_parser.add_argument("--manifest", required=True)
    batch_parser.add_argument("--output-dir", required=True)
    batch_parser.add_argument("--result-path", required=True)
    batch_parser.add_argument("--start", required=True, type=int)
    batch_parser.add_argument("--end", required=True, type=int)

    run_job_parser = subparsers.add_parser("run-job", help="Run a full usage report job")
    run_job_parser.add_argument("--job-id", required=True)
    run_job_parser.add_argument("--master-list", required=True)
    run_job_parser.add_argument("--template", required=True)
    run_job_parser.add_argument("--job-dir", required=True)
    run_job_parser.add_argument("--status-path", required=True)

    return parser.parse_args(argv)


def _run_cli(argv: list[str]) -> int:
    args = _parse_args(argv)

    if args.command == "batch":
        result = _write_batch_reports(
            template_path=args.template,
            manifest_path=args.manifest,
            output_dir=args.output_dir,
            start=args.start,
            end=args.end,
        )
        _write_json(args.result_path, result)
        return 0

    if args.command == "run-job":
        return run_generation_job(
            job_id=args.job_id,
            master_list_path=args.master_list,
            template_path=args.template,
            job_dir=args.job_dir,
            status_path=args.status_path,
        )

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    sys.exit(_run_cli(sys.argv[1:]))
