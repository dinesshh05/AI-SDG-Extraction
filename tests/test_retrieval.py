from src.retrieval import retrieve_top_chunks

query = "renewable energy"

results = retrieve_top_chunks(
    query=query,
    top_k=5
)

for i, result in enumerate(results, start=1):

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
        "\nPreview:\n"
    )

    print(
        chunk["chunk_text"][:1000]
    )