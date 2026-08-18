import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from chatbot.session import handle_message
from backend.status_store import get_status

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    document_id: str | None = None
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = []


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
        reply, sources = handle_message(req.document_id, get_status, history_dicts, req.message)

    except Exception as e:
        logger.exception(
            f"Chat request failed for document_id={req.document_id!r}: {e}"
        )
        raise HTTPException(
            status_code=502,
            detail="The chatbot is temporarily unavailable. Please try again shortly."
        )

    return ChatResponse(reply=reply, sources=sources)