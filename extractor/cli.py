"""
Local CLI runner, for testing the pipeline directly without the backend
running — mirrors the old main.py's __main__ block. Picks the most
recently modified PDF in ./input.

Usage:
    python -m extractor.cli
"""

import glob
import os
import uuid

from .extractor import run_extraction


def main():
    pdf_files = sorted(glob.glob("input/*.pdf"), key=os.path.getmtime, reverse=True)

    if not pdf_files:
        raise FileNotFoundError("No PDF found in input folder.")

    pdf_path = pdf_files[0]
    document_id = str(uuid.uuid4())

    print(f"Using PDF: {pdf_path}")
    print(f"Document ID: {document_id}")

    def progress_callback(step, total, label):
        print(f"[{step}/{total}] {label}")

    report_path, validation_errors = run_extraction(document_id, pdf_path, progress_callback)

    print(f"\nReport written to: {report_path}")
    if validation_errors:
        print(f"{len(validation_errors)} record(s) failed validation and were excluded.")


if __name__ == "__main__":
    main()