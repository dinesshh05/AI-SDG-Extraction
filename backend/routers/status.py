from fastapi import APIRouter, HTTPException

from backend.status_store import get_full

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/{document_id}")
async def get_document_status(document_id: str):
    result = get_full(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Unknown document_id")
    return {"document_id": document_id, **result}