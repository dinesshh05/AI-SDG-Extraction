"""
Runs every query in query_bank against one document's namespace and
merges the results via stratified round-robin (by rank across queries,
not global score) — ported from the original retrieve_sustainability_chunks.

Why round-robin: with 40+ queries covering all 17 SDGs, broad topics
(climate, energy) get partially matched by many queries and would
dominate a pure global-score ranking. Narrow SDGs with only one or two
dedicated queries could score well on their own query but rank low in
a merged global pool — and with a fixed batch ceiling downstream in
llm_extraction.py, those chunks might never reach the LLM at all.
Round-robin by rank fixes this: every query's #1 result is placed
before any query's #2 result.

This orchestration is extractor-specific — the chatbot never runs more
than one query per message, so it calls retrieval_core directly instead
(see chatbot/session.py).
"""

from retrieval_core.retrieval import build_retrieval_context, retrieve_top_chunks
from .sdg_keywords import SUSTAINABILITY_KEYWORDS


def retrieve_sustainability_chunks(namespace: str, queries: list[str], top_k_per_query: int = 10):
    context = build_retrieval_context(namespace)

    per_query_results = []
    for q in queries:
        results = retrieve_top_chunks(
            context,
            q,
            top_k=top_k_per_query,
            boost_keywords=SUSTAINABILITY_KEYWORDS,
        )
        per_query_results.append(results)

    combined = {}
    ordered = []

    max_rank = max((len(r) for r in per_query_results), default=0)

    for rank in range(max_rank):
        for results in per_query_results:
            if rank >= len(results):
                continue

            result = results[rank]
            chunk_id = result["chunk"]["chunk_id"]

            if chunk_id not in combined:
                combined[chunk_id] = result
                ordered.append(result)
            elif result["score"] > combined[chunk_id]["score"]:
                combined[chunk_id]["score"] = result["score"]

    return ordered