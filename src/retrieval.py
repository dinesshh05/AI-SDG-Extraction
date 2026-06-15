import numpy as np #type:ignore

from src.embeddings import generate_embedding
from src.vector_store import fetch_all_embeddings

def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2))


def retrieve_top_chunks_for_query(
    query: str,
    chunks,
    top_k=10
):
    query_embedding = generate_embedding(query)

    results = []

    for chunk in chunks:

        score = cosine_similarity(
            query_embedding,
            chunk["embedding"]
        )

        results.append(
            {
                "score": score,
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

    combined = {}

    for query in queries:

        results = retrieve_top_chunks_for_query(
            query,
            chunks,
            top_k_per_query
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