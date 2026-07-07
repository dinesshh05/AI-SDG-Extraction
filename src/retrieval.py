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
# Skipping this measurably weakens semantic retrieval quality with
# BGE-small-en-v1.5 specifically - it's not a generic nicety, it's
# how the model was fine-tuned to be used.
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Sustainability boost is folded into the same weighted scale as the
# semantic/BM25 scores, not stacked on top of them. Previously the
# boost (up to +0.20) was added AFTER the 0.7/0.3 weighted sum, which
# could let a keyword-dense but semantically weak chunk (e.g. mediocre
# similarity but 6+ keyword hits) outrank a genuinely more relevant
# chunk. Treating it as a third weighted component keeps everything on
# the same 0-1 scale, so it can nudge rankings but can't override a
# real semantic/BM25 gap.
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

    # 6+ keyword matches saturates the boost at 1.0; scales linearly
    # below that, same shape as before, just normalized to 0-1 instead
    # of 0-0.20 so it can be weighted like the other two signals.
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
    chunks = fetch_all_embeddings()

    tokenized_corpus = [
        chunk["chunk_text"].lower().split()
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    combined = {}

    for query in queries:

        results = retrieve_top_chunks_for_query(
            query=query,
            chunks=chunks,
            bm25=bm25,
            top_k=top_k_per_query
        )

        for result in results:

            chunk = result["chunk"]
            chunk_id = chunk["chunk_id"]

            if (
                chunk_id not in combined
                or result["score"] > combined[chunk_id]["score"]
            ):
                combined[chunk_id] = result

    results = list(combined.values())

    results.sort(key=lambda x: x["score"], reverse=True)

    return results