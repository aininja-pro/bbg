import io
import os
import time
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.routers import usage_reports
from app.services.usage_report_generator import (
    MANIFEST_FILENAME,
    SHEET_PATH,
    STATUS_FILENAME,
    WORKBOOK_PATH,
    generate_all_reports,
    make_job_state,
    write_job_state,
)


def _create_master_list(path):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Member ID", "Builder Name", "State", "Name", "TM", "File Name"])
    worksheet.append([101, "Alpha Builders", "TX", "Name", "TM", "alpha-report"])
    worksheet.append([None, "Missing Member", "CA", "Name", "TM", "missing-report"])
    worksheet.append([202, "Beta Builders", "CA", "Name", "TM", "beta-report"])
    workbook.save(path)
    workbook.close()


def _create_template(path):
    sheet_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<worksheet><sheetData>'
        b'<row r="6"><c r="B6" s="131"/></row>'
        b'<row r="7"><c r="B7" s="2" t="s"><v>44</v></c><c r="C7" s="2"/></row>'
        b"</sheetData></worksheet>"
    )
    workbook_xml = b'<workbook><calcPr calcId="123"/></workbook>'

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("_rels/.rels", "<Relationships/>")
        archive.writestr("xl/_rels/workbook.xml.rels", "<Relationships/>")
        archive.writestr(WORKBOOK_PATH, workbook_xml)
        archive.writestr(SHEET_PATH, sheet_xml)


@pytest.fixture(autouse=True)
def isolate_usage_jobs(tmp_path, monkeypatch):
    monkeypatch.setattr(usage_reports.tempfile, "gettempdir", lambda: str(tmp_path))
    yield


def test_generate_all_reports_batches_in_subprocesses(tmp_path):
    master_list_path = tmp_path / "master_list.xlsx"
    template_path = tmp_path / "template.xlsm"
    job_dir = tmp_path / "job"

    _create_master_list(master_list_path)
    _create_template(template_path)

    progress_updates = []
    result = generate_all_reports(
        master_list_path=str(master_list_path),
        template_path=str(template_path),
        job_dir=str(job_dir),
        batch_size=1,
        on_progress=progress_updates.append,
    )

    assert result["success"] is True
    assert result["files_generated"] == 2
    assert result["rows_skipped"] == 1
    assert progress_updates == [1, 2]
    assert result["zip_path"] == str(job_dir / "reports.zip")
    assert not (job_dir / MANIFEST_FILENAME).exists()
    assert not any(path.name.startswith("batch_") for path in job_dir.iterdir())

    with zipfile.ZipFile(result["zip_path"]) as outer_archive:
        assert sorted(outer_archive.namelist()) == ["alpha-report.xlsm", "beta-report.xlsm"]

        alpha_bytes = outer_archive.read("alpha-report.xlsm")
        beta_bytes = outer_archive.read("beta-report.xlsm")

    with zipfile.ZipFile(io.BytesIO(alpha_bytes)) as alpha_archive:
        alpha_sheet = alpha_archive.read(SHEET_PATH)
        alpha_workbook = alpha_archive.read(WORKBOOK_PATH)

    with zipfile.ZipFile(io.BytesIO(beta_bytes)) as beta_archive:
        beta_sheet = beta_archive.read(SHEET_PATH)

    assert b"Alpha Builders" in alpha_sheet
    assert b"<v>101</v>" in alpha_sheet
    assert b"TX" in alpha_sheet
    assert b"Beta Builders" in beta_sheet
    assert b"<v>202</v>" in beta_sheet
    assert b'fullCalcOnLoad="1"' in alpha_workbook


def test_generate_reports_endpoint_keeps_job_api_and_streams_uploads_to_disk(monkeypatch, tmp_path):
    app = FastAPI()
    app.include_router(usage_reports.router)

    captured = {}

    def fake_start_background_generation(job_id, master_list_path, template_path, job_dir, status_path):
        captured["master_list_path"] = master_list_path
        captured["template_path"] = template_path
        captured["job_dir"] = job_dir
        captured["status_path"] = status_path

        with open(master_list_path, "rb") as master_file:
            captured["master_bytes"] = master_file.read()
        with open(template_path, "rb") as template_file:
            captured["template_bytes"] = template_file.read()

        zip_path = os.path.join(job_dir, "reports.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as archive:
            archive.writestr("dummy.txt", b"ok")

        write_job_state(
            status_path,
            make_job_state(
                status_value="complete",
                zip_path=zip_path,
                files_generated=3,
                rows_skipped=1,
                warnings=["skipped one row"],
                error=None,
            ),
        )

    async def forbidden_read(self, *args, **kwargs):
        raise AssertionError("UploadFile.read() should not be called by the usage report endpoint")

    monkeypatch.setattr(usage_reports, "_start_background_generation", fake_start_background_generation)
    monkeypatch.setattr(usage_reports.UploadFile, "read", forbidden_read)

    client = TestClient(app)
    response = client.post(
        "/api/generate-reports",
        files={
            "master_list": (
                "builders.xlsx",
                b"master-bytes",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            "template": (
                "template.xlsm",
                b"template-bytes",
                "application/vnd.ms-excel.sheet.macroEnabled.12",
            ),
        },
    )

    assert response.status_code == 200
    job_id = response.json()["job_id"]

    status_payload = None
    for _ in range(20):
        status_response = client.get(f"/api/generate-reports/{job_id}/status")
        assert status_response.status_code == 200
        status_payload = status_response.json()
        if status_payload["status"] == "complete":
            break
        time.sleep(0.05)

    assert status_payload == {
        "status": "complete",
        "files_generated": 3,
        "rows_skipped": 1,
        "warnings": ["skipped one row"],
        "error": None,
    }
    assert captured["master_bytes"] == b"master-bytes"
    assert captured["template_bytes"] == b"template-bytes"
    assert captured["master_list_path"].endswith("master_list.xlsx")
    assert captured["template_path"].endswith("template.xlsm")
    assert captured["status_path"].endswith(STATUS_FILENAME)

    download_response = client.get(f"/api/generate-reports/{job_id}/download")
    assert download_response.status_code == 200

    with zipfile.ZipFile(io.BytesIO(download_response.content)) as archive:
        assert archive.read("dummy.txt") == b"ok"

    assert not os.path.exists(captured["job_dir"])
    assert client.get(f"/api/generate-reports/{job_id}/status").status_code == 404
