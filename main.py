import os
import glob

PDF_PATH = None

from src.parser import extract_pages
from src.chunker import chunk_pages
from src.embeddings import generate_embedding

from src.vector_store import (
    init_db,
    store_embedding,
    fetch_all_embeddings
)

from src.filtering import filter_chunks

from src.retrieval import retrieve_sustainability_chunks
from src.query_bank import SUSTAINABILITY_QUERIES
from src.extractor import extract_initiatives
from src.validator import validate_initiatives
from src.excel_writer import export_to_excel


def build_embeddings():

    global PDF_PATH

    DB_PATH = "cache/embeddings.db"

    if os.path.exists(DB_PATH):
        print("\nRemoving old embeddings database...")
        os.remove(DB_PATH)

    print("\n[1/6] Parsing PDF...")

    pages = extract_pages(PDF_PATH)

    print(f"Pages Found: {len(pages)}")

    print("\n[2/6] Chunking...")

    chunks = chunk_pages(pages)

    print(f"Chunks Created: {len(chunks)}")

    print("\n[3/6] Filtering...")

    kept_chunks, skipped_chunks = filter_chunks(chunks)

    print(f"Chunks Kept   : {len(kept_chunks)}")
    print(f"Chunks Skipped: {len(skipped_chunks)}")

    print("\n[4/6] Building Embeddings...")

    init_db()

    for chunk in kept_chunks:

        embedding = generate_embedding(chunk["chunk_text"])

        store_embedding(
            chunk["chunk_id"],
            chunk["start_page"],
            chunk["end_page"],
            chunk.get("section", ""),   # now stored, no longer dropped
            chunk["chunk_text"],
            embedding
        )

    print(f"Embeddings Stored: {len(kept_chunks)}")


def run_extraction():

    print("\n[5/6] Retrieving Sustainability Chunks...")

    results = retrieve_sustainability_chunks(
        SUSTAINABILITY_QUERIES,
        top_k_per_query=10
    )

    print(f"Retrieved Chunks: {len(results)}")

    context = ""

    for result in results[:12]:

        chunk = result["chunk"]

        context += f"""
SECTION: {chunk.get('section', '')}
PAGES: {chunk['start_page']}-{chunk['end_page']}

TEXT:
{chunk['chunk_text']}

"""

    print(f"\nContext Length: {len(context)} characters")

    print("\n[6/6] Extracting Initiatives...")

    initiatives = extract_initiatives(context)

    validated = validate_initiatives(initiatives)

    print(f"\nValidated Records: {len(validated)}")

    print("\nExporting Excel...")

    output_file = export_to_excel(validated)

    print("\nPipeline Completed Successfully.")

    return output_file


def run_pipeline(pdf_path):

    global PDF_PATH

    PDF_PATH = pdf_path

    build_embeddings()

    output_file = run_extraction()

    return output_file


if __name__ == "__main__":

    pdf_files = sorted(
        glob.glob("input/*.pdf"),
        key=os.path.getmtime,
        reverse=True
    )

    if not pdf_files:
        raise FileNotFoundError("No PDF found in input folder.")

    PDF_PATH = pdf_files[0]

    print(f"Using PDF: {PDF_PATH}")

    build_embeddings()

    run_extraction()