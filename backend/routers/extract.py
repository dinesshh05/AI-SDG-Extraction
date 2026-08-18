import os
import uuid
import json

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from extractor.extractor import run_extraction
from backend.status_store import set_status, update_phase, get_full

router = APIRouter(prefix="/extract", tags=["extract"])

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./cache/uploads")
REPORT_DIR = os.environ.get("REPORT_DIR", "./cache/reports")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _run_and_track(document_id: str, file_path: str) -> None:
    def progress_callback(step, total, label):
        update_phase(document_id, step, total, label)

    try:
        report_path, validation_errors = run_extraction(
            document_id, file_path, progress_callback=progress_callback
        )
        set_status(document_id, "ready", report_path=report_path, warnings=len(validation_errors))
    except Exception as e:
        set_status(document_id, "failed", error=str(e))


@router.post("")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    set_status(document_id, "processing")
    background_tasks.add_task(_run_and_track, document_id, file_path)

    return {"document_id": document_id, "status": "processing"}


@router.get("/{document_id}/download")
async def download_report(document_id: str):
    info = get_full(document_id)
    if not info or info["status"] != "ready" or not info["report_path"]:
        raise HTTPException(status_code=404, detail="Report not available")
    return FileResponse(
        info["report_path"],
        filename=f"sustainability_report_{document_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/{document_id}/results")
async def get_results(document_id: str):
    info = get_full(document_id)
    if not info or info["status"] != "ready":
        raise HTTPException(status_code=404, detail="Results not available")

    results_path = os.path.join(REPORT_DIR, f"{document_id}.json")

    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Results file missing")

    with open(results_path) as f:
        return json.load(f)