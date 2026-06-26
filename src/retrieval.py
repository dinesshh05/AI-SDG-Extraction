import numpy as np #type:ignore

from rank_bm25 import BM25Okapi

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

def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2))

def normalize_scores(scores):

    scores=np.array(scores)

    if scores.max()== scores.min():
        return np.ones_like(scores)
    
    return(
        scores-scores.min()
    )/(
        scores.max()-scores.min()
    )

def sustainability_boost(text):

    text = text.lower()

    matches = sum(
        keyword in text
        for keyword in SUSTAINABILITY_KEYWORDS
    )

    return min(
        matches * 0.03,
        0.20
    )


def retrieve_top_chunks_for_query(
    query: str,
    chunks,
    bm25,
    top_k=10,
    semantic_weight=0.7,
    keyword_weight=0.3
):
    query_embedding = generate_embedding(query)

    tokenized_query = query.lower().split()

    bm25_scores=bm25.get_scores(
        tokenized_query
    )

    bm25_scores= normalize_scores(bm25_scores)

    results = []

    for idx,chunk in enumerate(chunks):

        embedding_score = cosine_similarity(
            query_embedding,
            chunk["embedding"]
        )

        relevance_boost=sustainability_boost(
            chunk["chunk_text"]
        )

        final_scores=(
                    semantic_weight*embedding_score
                    +
                    keyword_weight*bm25_scores[idx]
                    +
                    relevance_boost
                    )

        results.append(
            {
                "score": final_scores,
                "semantic_score": embedding_score,
                "bm25_scores":float(
                    bm25_scores[idx]
                ),
                "relevance_boost":relevance_boost,
                "chunk": chunk
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_k]


def retrieve_sustainability_chunks(
    queries,
    top_k_per_query=10
):
    chunks = fetch_all_embeddings()

    tokenized_corpus=[
        chunk["chunk_text"].lower().split()
        for chunk in chunks
    ]

    bm25= BM25Okapi(
        tokenized_corpus
    )

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
                or result["score"] >
                combined[chunk_id]["score"]
            ):
                combined[chunk_id] = result

    results = list(combined.values())

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results