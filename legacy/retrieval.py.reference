import numpy as np  # type:ignore

from rank_bm25 import BM25Okapi  # type:ignore

from src.embeddings import generate_embedding
from src.vector_store import fetch_all_embeddings

SUSTAINABILITY_KEYWORDS = [
    "sustainability",
    "esg",
    "environment",
    "renewable",
    "solar",
    "energy",
    "water",
    "waste",
    "recycling",
    "carbon",
    "emission",
    "emissions",
    "climate",
    "csr",
    "green",
    "pollution",
    "biodiversity",
    "greenhouse",
    "occupational health",
    "safety",
    "zero liquid discharge"
]

# BGE models are trained with an asymmetric query/passage convention:
# queries need this instruction prefix, passages (chunks) do not.
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Sustainability boost is folded into the same weighted scale as the
# semantic/BM25 scores, not stacked on top of them.
BOOST_WEIGHT = 0.15


def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2))


def normalize_scores(scores):

    scores = np.array(scores)

    if scores.max() == scores.min():
        return np.ones_like(scores)

    return (
        scores - scores.min()
    ) / (
        scores.max() - scores.min()
    )


def sustainability_boost(text):
    """
    Returns a 0-1 normalized keyword-density signal (not a raw score
    add-on). Capped at 1.0 so it can be weighted consistently
    alongside semantic_score and bm25_score, both also 0-1.
    """

    text = text.lower()

    matches = sum(
        keyword in text
        for keyword in SUSTAINABILITY_KEYWORDS
    )

    return min(matches / 6.0, 1.0)


def retrieve_top_chunks_for_query(
    query: str,
    chunks,
    bm25,
    top_k=10,
    semantic_weight=0.6,
    keyword_weight=0.25,
    boost_weight=BOOST_WEIGHT
):
    """
    semantic_weight + keyword_weight + boost_weight should sum to 1.0
    so all three signals live on the same comparable scale. Defaults:
    0.6 + 0.25 + 0.15 = 1.0.
    """

    query_embedding = generate_embedding(
        BGE_QUERY_PREFIX + query
    )

    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_scores = normalize_scores(bm25_scores)

    results = []

    for idx, chunk in enumerate(chunks):

        embedding_score = cosine_similarity(
            query_embedding,
            chunk["embedding"]
        )

        relevance_boost = sustainability_boost(
            chunk["chunk_text"]
        )

        final_score = (
            semantic_weight * embedding_score
            + keyword_weight * bm25_scores[idx]
            + boost_weight * relevance_boost
        )

        results.append(
            {
                "score": final_score,
                "semantic_score": embedding_score,
                "bm25_scores": float(bm25_scores[idx]),
                "relevance_boost": relevance_boost,
                "chunk": chunk
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


def retrieve_sustainability_chunks(
    queries,
    top_k_per_query=10
):
    """
    Retrieves and orders chunks using stratified round-robin selection
    across queries, instead of pure global score sorting.

    Why: with 40+ queries covering all 17 SDGs, broad topics (climate,
    energy, renewables) get partially matched by many different
    queries and dominate a pure global-score ranking. Narrow SDGs with
    only one or two dedicated queries can score well on THEIR OWN
    query but still rank low in the merged global pool - and with a
    fixed batch ceiling downstream, those chunks may never reach the
    LLM at all, even though retrieval technically found them.

    Round-robin by rank fixes this: every query's #1 result is placed
    before any query's #2 result, so batch construction downstream
    sees broad SDG coverage early instead of topic-dominant chunks
    crowding out narrow ones.
    """

    chunks = fetch_all_embeddings()

    tokenized_corpus = [
        chunk["chunk_text"].lower().split()
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    per_query_results = []

    for query in queries:

        results = retrieve_top_chunks_for_query(
            query=query,
            chunks=chunks,
            bm25=bm25,
            top_k=top_k_per_query
        )

        per_query_results.append(results)

    combined = {}
    ordered = []

    max_rank = max(
        (len(r) for r in per_query_results),
        default=0
    )

    for rank in range(max_rank):

        for results in per_query_results:

            if rank >= len(results):
                continue

            result = results[rank]
            chunk = result["chunk"]
            chunk_id = chunk["chunk_id"]

            if chunk_id not in combined:
                combined[chunk_id] = result
                ordered.append(result)

            elif result["score"] > combined[chunk_id]["score"]:
                combined[chunk_id]["score"] = result["score"]

    return ordered