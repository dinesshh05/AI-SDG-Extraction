from src.parser import extract_pages
from src.chunker import chunk_pages

from src.embeddings import generate_embedding

from src.vector_store import (
    init_db,
    store_embedding,
    fetch_all_embeddings
)

from src.filtering import is_noise_chunk


pages = extract_pages(
    "input\Adani Port FY22.pdf"
)

chunks = chunk_pages(pages)

print(f"Pages: {len(pages)}")
print(f"Chunks: {len(chunks)}")

# -----------------------------------
# TEST EMBEDDING GENERATION
# -----------------------------------

embedding = generate_embedding(
    chunks[0]["chunk_text"]
)

print("\nEmbedding Shape:")
print(embedding.shape)

# -----------------------------------
# SQLITE INITIALIZATION
# -----------------------------------

init_db()

stored_count = 0
skipped_count = 0

for chunk in chunks:

    # Skip noisy chunks
    if is_noise_chunk(
        chunk["chunk_text"]
    ):
        skipped_count += 1
        continue

    embedding = generate_embedding(
        chunk["chunk_text"]
    )

    store_embedding(
        chunk["chunk_id"],
        chunk["start_page"],
        chunk["end_page"],
        chunk["chunk_text"],
        embedding
    )

    stored_count += 1

# -----------------------------------
# VERIFY STORAGE
# -----------------------------------

rows = fetch_all_embeddings()

print(f"\nStored Rows: {len(rows)}")

print("\nEmbedding Statistics")

print(
    f"Stored Chunks: {stored_count}"
)

print(
    f"Skipped Chunks: {skipped_count}"
)

print("\nFirst Stored Record:\n")

print(
    {
        "chunk_id":
        rows[0]["chunk_id"],

        "start_page":
        rows[0]["start_page"],

        "end_page":
        rows[0]["end_page"]
    }
)

print("\nEmbedding Info:\n")

print(
    type(rows[0]["embedding"])
)

print(
    rows[0]["embedding"].shape
)