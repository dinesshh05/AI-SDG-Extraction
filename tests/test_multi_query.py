import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from src.retrieval import (
    retrieve_sustainability_chunks
)

from src.query_bank import (
    SUSTAINABILITY_QUERIES
)

results = retrieve_sustainability_chunks(
    SUSTAINABILITY_QUERIES,
    top_k_per_query=10
)

print(
    f"Retrieved: {len(results)} chunks"
)

for i, result in enumerate(
    results[:10],
    start=1
):

    chunk = result["chunk"]

    print("\n" + "=" * 80)

    print(
        f"Rank: {i}"
    )

    print(
        f"Score: {result['score']:.4f}"
    )

    print(
        f"Pages: {chunk['start_page']} - {chunk['end_page']}"
    )

    print(
        chunk["chunk_text"][:500]
    )