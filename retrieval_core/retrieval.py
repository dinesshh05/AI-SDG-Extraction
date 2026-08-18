"""
The shared retrieval interface — this is the ONE place that defines how
chunks get indexed and how a query gets scored against them. Both the
extractor (indexing + the 50 query_bank scans, via
extractor/retrieval_orchestration.py) and the chatbot
(chatbot/session.py, one query per message) call these functions and
never touch vector_store.py or embeddings.py directly.

Scoring logic (hybrid semantic + BM25 + optional keyword boost) is
ported from the original retrieval.py, generalized so the domain
keyword list is passed in by the caller instead of hardcoded — the
extractor passes its SUSTAINABILITY_KEYWORDS list, the chatbot passes
none (plain semantic + BM25).
"""

import numpy as np
from rank_bm25 import BM25Okapi

from .embeddings import generate_embedding
from .vector_store import init_db, store_embedding, fetch_all_embeddings, delete_namespace

# BGE models are trained with an asymmetric query/passage convention:
# queries need this instruction prefix, passages (chunks) do not.
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2))


def normalize_scores(scores):
    scores = np.array(scores)
    if scores.max() == scores.min():
        return np.ones_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())


def index_chunks(namespace: str, chunks: list[dict], clear_existing: bool = True) -> None:
    """Embed and store a document's chunks under its namespace. Called
    once per document by the extractor, right after chunking/filtering.
    chunks must have: chunk_id, start_page, end_page, section, chunk_text."""
    init_db()
    if clear_existing:
        delete_namespace(namespace)

    for chunk in chunks:
        embedding = generate_embedding(chunk["chunk_text"])
        store_embedding(
            namespace,
            chunk["chunk_id"],
            chunk["start_page"],
            chunk["end_page"],
            chunk.get("section", ""),
            chunk["chunk_text"],
            embedding,
        )


def build_retrieval_context(namespace: str) -> dict:
    """Fetch a namespace's chunks and build a BM25 index once. The
    extractor builds this once and reuses it across all 50 query_bank
    queries; the chatbot builds it once per message (cheap — one
    document's chunk count, not a whole corpus)."""
    chunks = fetch_all_embeddings(namespace)
    tokenized_corpus = [c["chunk_text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus) if chunks else None
    return {"chunks": chunks, "bm25": bm25}


def retrieve_top_chunks(
    context: dict,
    query_text: str,
    top_k: int = 10,
    semantic_weight: float = 0.6,
    keyword_weight: float = 0.25,
    boost_weight: float = 0.15,
    boost_keywords: list[str] | None = None,
):
    """Hybrid semantic + BM25 + optional domain-keyword boost, scored
    against a prebuilt context (see build_retrieval_context). Weights
    should sum to 1.0. Pass boost_keywords=None for plain semantic+BM25
    with no domain boost — how the chatbot uses this."""

    chunks = context["chunks"]
    bm25 = context["bm25"]

    if not chunks:
        return []

    query_embedding = generate_embedding(BGE_QUERY_PREFIX + query_text)
    tokenized_query = query_text.lower().split()

    if bm25:
        bm25_scores = normalize_scores(bm25.get_scores(tokenized_query))
    else:
        bm25_scores = np.zeros(len(chunks))

    results = []
    for idx, chunk in enumerate(chunks):
        embedding_score = cosine_similarity(query_embedding, chunk["embedding"])

        if boost_keywords:
            text = chunk["chunk_text"].lower()
            matches = sum(kw in text for kw in boost_keywords)
            relevance_boost = min(matches / 6.0, 1.0)
        else:
            relevance_boost = 0.0

        final_score = (
            semantic_weight * embedding_score
            + keyword_weight * float(bm25_scores[idx])
            + boost_weight * relevance_boost
        )

        results.append(
            {
                "score": final_score,
                "semantic_score": embedding_score,
                "bm25_score": float(bm25_scores[idx]),
                "relevance_boost": relevance_boost,
                "chunk": chunk,
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]