import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from src.retrieval import retrieve_sustainability_chunks
from src.query_bank import SUSTAINABILITY_QUERIES

results = retrieve_sustainability_chunks(
    queries=SUSTAINABILITY_QUERIES,
    top_k_per_query=10
)

for i, result in enumerate(results[:20], start=1):

    chunk = result["chunk"]

    print("\n" + "=" * 100)

    print(
        f"Rank: {i}"
    )

    print(
        f"Final Score: {result['score']:.4f}"
    )

    print(
        f"Semantic Score: {result['semantic_score']:.4f}"
    )

    print(
        f"BM25 Score: {result['bm25_scores']:.4f}"
    )
    print(
        f"Relevance Boost: {result['relevance_boost']:.4f}"
    )

    print(
        f"Pages: {chunk['start_page']} - {chunk['end_page']}"
    )

    print(
        "\nPreview:\n"
    )

    print(
        chunk["chunk_text"][:1000]
    )

    print("\n")