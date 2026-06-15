import os

from src.parser import extract_pages
from src.chunker import chunk_pages

from src.embeddings import generate_embedding

from src.vector_store import (
    init_db,
    store_embedding,
    fetch_all_embeddings
)

from src.filtering import (
    is_noise_chunk
)

from src.retrieval import (
    retrieve_sustainability_chunks
)

from src.query_bank import (
    SUSTAINABILITY_QUERIES
)

from src.extractor import (
    extract_initiatives
)

from src.validator import (
    validate_initiatives
)

from src.excel_writer import (
    export_to_excel
)


PDF_PATH = None


def build_embeddings():

    global PDF_PATH

    DB_PATH = "cache/embeddings.db"

    if os.path.exists(DB_PATH):

        try:

            existing = fetch_all_embeddings()

            if len(existing) > 0:

                print(
                    f"\nEmbeddings already exist ({len(existing)} records)."
                )

                print(
                    "Skipping embedding generation."
                )

                return

        except Exception:

            print(
                "\nExisting DB found but could not be read."
            )

            print(
                "Rebuilding embeddings..."
            )

    print("\n[1/6] Parsing PDF...")

    pages = extract_pages(
        PDF_PATH
    )

    print(
        f"Pages Found: {len(pages)}"
    )

    print("\n[2/6] Chunking...")

    chunks = chunk_pages(
        pages
    )

    print(
        f"Chunks Created: {len(chunks)}"
    )

    print("\n[3/6] Building Embeddings...")

    init_db()

    stored = 0

    for chunk in chunks:

        if is_noise_chunk(
            chunk["chunk_text"]
        ):
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

        stored += 1

    print(
        f"Embeddings Stored: {stored}"
    )


def run_extraction():

    print("\n[4/6] Retrieving Sustainability Chunks...")

    results = retrieve_sustainability_chunks(
        SUSTAINABILITY_QUERIES,
        top_k_per_query=10
    )

    print(
        f"Retrieved Chunks: {len(results)}"
    )

    context = ""

    for result in results[:20]:

        chunk = result["chunk"]

        context += f"""

PAGES: {chunk['start_page']}-{chunk['end_page']}

TEXT:
{chunk['chunk_text']}

"""

    print(
        f"\nContext Length: {len(context)} characters"
    )

    print("\n[5/6] Extracting Initiatives...")

    initiatives = extract_initiatives(
        context
    )

    validated = validate_initiatives(
        initiatives
    )

    print(
        f"\nValidated Records: {len(validated)}"
    )

    print("\n[6/6] Exporting Excel...")

    output_file=export_to_excel(
        validated
    )

    print(
        "\nPipeline Completed Successfully."
    )

    return output_file

def run_pipeline(pdf_path):

    global PDF_PATH

    PDF_PATH = pdf_path

    build_embeddings()

    output_file = run_extraction()

    return output_file

if __name__ == "__main__":

    print(
        "Run the application using: streamlit run app.py"
    )