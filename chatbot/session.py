from retrieval_core.retrieval import build_retrieval_context, retrieve_top_chunks
from .faq_context import FAQ_CONTEXT
from .groq_client import generate_reply

TOP_K = 5

SYSTEM_INSTRUCTIONS = """
You are the Sustain Planet assistant. You help users understand the UN
Sustainable Development Goals and answer questions about a specific
uploaded annual report when one is available.

Rules:
- Answer only using the background/FAQ knowledge and document excerpts
  provided below. Do not invent facts not present in that context.
- If a question is about the uploaded document but the answer isn't in
  the provided excerpts, say you couldn't find that in the retrieved
  sections rather than guessing.
- When you reference something from the document, mention which page
  it came from if the excerpt includes a page number.
- Keep answers concise and conversational, not a wall of text.
"""


def build_context(document_id: str | None, get_status_fn, user_message: str):
    """
    Returns (context_text, sources) where sources is a list of page
    references used to build the context (empty if no document, or no
    matches found).
    """
    context = SYSTEM_INSTRUCTIONS + "\n\n" + FAQ_CONTEXT
    sources = []

    if document_id is None:
        return context, sources

    status = get_status_fn(document_id)

    if status == "unknown":
        context += (
            "\n\nNote: the document_id provided does not correspond to any "
            "known document. If the user asks about a document, tell them "
            "it could not be found and to try uploading again."
        )
        return context, sources

    if status != "ready":
        context += (
            "\n\nNote: a document has been uploaded but SDG extraction is "
            "still in progress. If the user asks about the document, tell "
            "them it's still processing and to check back shortly."
        )
        return context, sources

    namespace = f"doc_{document_id}"
    retrieval_context = build_retrieval_context(namespace)
    matches = retrieve_top_chunks(retrieval_context, user_message, top_k=TOP_K)

    if matches:
        excerpt_blocks = []
        for m in matches:
            chunk = m["chunk"]
            page_ref = f"Page {chunk.get('start_page', '?')}"
            excerpt_blocks.append(f"[{page_ref}]\n{chunk['chunk_text']}")
            sources.append(page_ref)

        context += "\n\nRelevant excerpts from the uploaded document:\n" + "\n---\n".join(excerpt_blocks)

    return context, sources


def handle_message(document_id: str | None, get_status_fn, history: list[dict], user_message: str):
    """
    Returns (reply, sources).
    history: list of {"role": "user"|"assistant", "content": str} from
    the current chat session, oldest first — passed in by the caller
    (the frontend keeps the running conversation, backend is stateless
    per request).
    """
    context, sources = build_context(document_id, get_status_fn, user_message)
    reply = generate_reply(context, history, user_message)
    return reply, sources