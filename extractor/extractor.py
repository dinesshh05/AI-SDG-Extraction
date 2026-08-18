"""
The extractor orchestrator — replaces the old main.py's build_embeddings()
+ run_extraction() split and its module-level PDF_PATH global. That global
worked for a single-user local Streamlit app processing one PDF at a time,
but a web backend can have several documents' extractions running as
background tasks concurrently — so document_id and file_path are now
threaded through as arguments instead.

Same 6 stages as the original main.py, same order:
  1. Parse            (parser.py)
  2. Chunk             (chunker.py)
  3. Filter            (filtering.py)
  4. Index             (retrieval_core, namespaced)
  5. Retrieve          (retrieval_orchestration.py — round-robin over query_bank)
  6. Extract + validate + export (llm_extraction.py, validator.py, excel_writer.py)
"""

import os
import json

from retrieval_core.retrieval import index_chunks

from .parser import extract_pages
from .chunker import chunk_pages
from .filtering import filter_chunks
from .query_bank import SUSTAINABILITY_QUERIES
from .retrieval_orchestration import retrieve_sustainability_chunks
from .llm_extraction import extract_initiatives_batched
from .validator import validate_initiatives
from .excel_writer import export_to_excel, build_sdg_report

REPORT_DIR = os.environ.get("REPORT_DIR", "./cache/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

TOTAL_STEPS = 6


def run_extraction(document_id: str, file_path: str, progress_callback=None):
    """
    Runs the full pipeline for one uploaded document.

    progress_callback(step: int, total: int, label: str), if provided,
    is called at each stage — the backend wires this to status_store's
    update_phase() so the website can poll granular progress instead of
    Streamlit's old inline progress bar.

    Returns (report_path, validation_errors).
    """

    def _step(n, label):
        print(f"\n[{n}/{TOTAL_STEPS}] {label}")
        if progress_callback:
            progress_callback(n, TOTAL_STEPS, label)

    namespace = f"doc_{document_id}"

    _step(1, "Parsing PDF...")
    pages = extract_pages(file_path)
    print(f"Pages Found: {len(pages)}")

    _step(2, "Chunking...")
    chunks = chunk_pages(pages)
    print(f"Chunks Created: {len(chunks)}")

    _step(3, "Filtering...")
    kept_chunks, skipped_chunks = filter_chunks(chunks)
    print(f"Chunks Kept   : {len(kept_chunks)}")
    print(f"Chunks Skipped: {len(skipped_chunks)}")

    _step(4, "Indexing...")
    index_chunks(namespace, kept_chunks)
    print(f"Embeddings Stored: {len(kept_chunks)}")

    _step(5, "Retrieving sustainability chunks...")
    results = retrieve_sustainability_chunks(namespace, SUSTAINABILITY_QUERIES, top_k_per_query=10)
    print(f"Retrieved Chunks: {len(results)}")

    _step(6, "Extracting, validating, and exporting...")
    initiatives, batch_errors = extract_initiatives_batched(
        results, max_tokens_per_batch=4000, max_batches=8, delay_seconds=2
    )
    print(f"Raw Extracted Records: {len(initiatives)}")

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

    report_path = os.path.join(REPORT_DIR, f"{document_id}.xlsx")
    export_to_excel(validated, output_path=report_path)

    # Also persist a JSON sidecar of the same grouped report, so the
    # backend can serve GET /extract/{id}/results without re-running
    # extraction or re-parsing the Excel file.
    report_data = build_sdg_report(validated)
    results_json_path = os.path.join(REPORT_DIR, f"{document_id}.json")
    with open(results_json_path, "w") as f:
        json.dump(report_data, f)

    print("\nPipeline Completed Successfully.")
    return report_path, validation_errors