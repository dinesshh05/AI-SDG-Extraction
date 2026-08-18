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
from src.extractor import extract_initiatives_batched
from src.validator import validate_initiatives
from src.excel_writer import export_to_excel


TOTAL_STEPS = 6


def _report(progress_callback, step, label):
    print(f"\n[{step}/{TOTAL_STEPS}] {label}")

    if progress_callback:
        progress_callback(step, TOTAL_STEPS, label)


def _log_batch_section_coverage(results, max_tokens_per_batch=4000, max_batches=8):

    from src.extractor import estimate_tokens

    batches = []
    current_batch = []
    current_tokens = 0

    for result in results:

        chunk = result["chunk"]
        section = chunk.get("section", "Unknown")

        chunk_text_for_estimate = f"""
SECTION: {chunk.get('section', '')}
PAGES: {chunk['start_page']}-{chunk['end_page']}

TEXT:
{chunk['chunk_text']}
"""
        chunk_tokens = estimate_tokens(chunk_text_for_estimate)

        if current_batch and (current_tokens + chunk_tokens) > max_tokens_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

            if len(batches) >= max_batches:
                break

        current_batch.append(section)
        current_tokens += chunk_tokens

    if current_batch and len(batches) < max_batches:
        batches.append(current_batch)

    processed_sections = set()
    for batch in batches:
        processed_sections.update(batch)

    all_sections = set(
        result["chunk"].get("section", "Unknown")
        for result in results
    )

    dropped_sections = all_sections - processed_sections

    print(f"\n--- Batch Coverage Debug ---")
    print(f"Total unique sections in retrieved pool : {len(all_sections)}")
    print(f"Sections reaching processed batches      : {len(processed_sections)}")
    print(f"Sections dropped (never reach LLM)        : {len(dropped_sections)}")

    if dropped_sections:
        print("Dropped section examples (up to 15):")
        for s in list(dropped_sections)[:15]:
            print(f"  - {s}")

    print("----------------------------\n")


def build_embeddings(progress_callback=None):

    global PDF_PATH

    DB_PATH = "cache/embeddings.db"

    if os.path.exists(DB_PATH):
        print("\nRemoving old embeddings database...")
        os.remove(DB_PATH)

    _report(progress_callback, 1, "Parsing PDF...")

    pages = extract_pages(PDF_PATH)

    print(f"Pages Found: {len(pages)}")

    _report(progress_callback, 2, "Chunking...")

    chunks = chunk_pages(pages)

    print(f"Chunks Created: {len(chunks)}")

    _report(progress_callback, 3, "Filtering...")

    kept_chunks, skipped_chunks = filter_chunks(chunks)

    print(f"Chunks Kept   : {len(kept_chunks)}")
    print(f"Chunks Skipped: {len(skipped_chunks)}")

    _report(progress_callback, 4, "Building Embeddings...")

    init_db()

    total = len(kept_chunks)

    
    update_every = max(1, total // 20)

    for i, chunk in enumerate(kept_chunks):

        embedding = generate_embedding(chunk["chunk_text"])

        store_embedding(
            chunk["chunk_id"],
            chunk["start_page"],
            chunk["end_page"],
            chunk.get("section", ""),
            chunk["chunk_text"],
            embedding
        )

        if progress_callback and ((i + 1) % update_every == 0 or i + 1 == total):
            progress_callback(
                4,
                TOTAL_STEPS,
                f"Building Embeddings... ({i + 1}/{total})"
            )

    print(f"Embeddings Stored: {len(kept_chunks)}")


def run_extraction(progress_callback=None):

    _report(progress_callback, 5, "Retrieving Sustainability Chunks...")

    results = retrieve_sustainability_chunks(
        SUSTAINABILITY_QUERIES,
        top_k_per_query=10
    )

    print(f"Retrieved Chunks: {len(results)}")

    _log_batch_section_coverage(
        results,
        max_tokens_per_batch=4000,
        max_batches=8
    )

    _report(progress_callback, 6, "Extracting Initiatives...")

    initiatives, batch_errors = extract_initiatives_batched(
        results,
        max_tokens_per_batch=4000,
        max_batches=8,
        delay_seconds=2
    )

    print(f"\nRaw Extracted Records: {len(initiatives)}")

    if batch_errors:
        print(f"Batch Failures: {len(batch_errors)}")
        for err in batch_errors:
            print(f"  - {err}")

    if not initiatives and batch_errors:
        raise RuntimeError(
            f"All {len(batch_errors)} extraction batch(es) failed. "
            f"First error: {batch_errors[0]}"
        )

    validated, validation_errors = validate_initiatives(initiatives)

    print(f"Validated Records: {len(validated)}")

    if validation_errors:
        print(f"Validation Failures: {len(validation_errors)}")
        for err in validation_errors:
            print(f"  - {err['reason']}")

    print("\nExporting Excel...")

    output_file = export_to_excel(validated)

    print("\nPipeline Completed Successfully.")

    return output_file, validation_errors


def run_pipeline(pdf_path, progress_callback=None):

    global PDF_PATH

    PDF_PATH = pdf_path

    build_embeddings(progress_callback)

    output_file, validation_errors = run_extraction(progress_callback)

    return output_file, validation_errors


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

    output_file, validation_errors = run_extraction()

    if validation_errors:
        print(f"\n{len(validation_errors)} record(s) failed validation and were excluded.")