import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from extractor.parser import extract_pages
from extractor.chunker import chunk_pages

from extractor.filtering import (
    filter_chunks,
)

# ==========================================================
# LOAD PDF
# ==========================================================

PDF_PATH = "input/Adani Port FY22.pdf"

pages = extract_pages(PDF_PATH)

chunks = chunk_pages(pages)

kept_chunks, skipped_chunks = filter_chunks(chunks)

# ==========================================================
# BASIC STATISTICS
# ==========================================================

print("\n" + "=" * 80)

print("FILTERING SUMMARY")

print("=" * 80)

print(f"Pages          : {len(pages)}")

print(f"Total Chunks   : {len(chunks)}")

print(f"Kept Chunks    : {len(kept_chunks)}")

print(f"Skipped Chunks : {len(skipped_chunks)}")

retention = (
    len(kept_chunks) /
    len(chunks)
) * 100

print(f"Retention Rate : {retention:.2f}%")

# ==========================================================
# REASON BREAKDOWN
# ==========================================================

print("\n")

print("=" * 80)

print("SKIP REASON BREAKDOWN")

print("=" * 80)

reason_count = {}

for chunk in skipped_chunks:

    reason = chunk["_filter_reason"]

    reason_count[reason] = (

        reason_count.get(reason, 0)

        + 1

    )

for reason, count in sorted(

    reason_count.items(),

    key=lambda x: x[1],

    reverse=True

):

    print(f"{reason:<30}{count}")

# ==========================================================
# PROTECTED SECTION AUDIT
# ==========================================================

print("\n")

print("=" * 80)

print("PROTECTED SECTION AUDIT")

print("=" * 80)

protected_keywords = [

    "business responsibility",

    "sustainability",

    "csr",

    "esg",

    "environment",

    "climate"

]

for keyword in protected_keywords:

    total = 0

    skipped = 0

    for chunk in chunks:

        section = chunk.get(

            "section",

            ""

        ).lower()

        if keyword in section:

            total += 1

            if chunk.get("_filter_keep") is False:

                skipped += 1

    status = "PASS"

    if skipped > 0:

        status = "FAIL"

    print(

        f"{keyword:<30}"

        f"Total={total:<3}"

        f"Skipped={skipped:<3}"

        f"{status}"

    )

# ==========================================================
# FALSE POSITIVE CHECK
# ==========================================================

print("\n")

print("=" * 80)

print("FALSE POSITIVE CHECK")

print("=" * 80)

false_positive_found = False

for chunk in skipped_chunks:

    section = chunk.get(

        "section",

        ""

    ).lower()

    for keyword in protected_keywords:

        if keyword in section:

            false_positive_found = True

            print("\nWARNING")

            print("-" * 40)

            print(

                f"Chunk ID : {chunk['chunk_id']}"

            )

            print(

                f"Section  : {chunk['section']}"

            )

            print(

                f"Reason   : {chunk['_filter_reason']}"

            )

            print()

            print(

                chunk["chunk_text"][:500]

            )

if not false_positive_found:

    print(

        "No protected chunks were removed."

    )

# ==========================================================
# REVIEW SKIPPED CHUNKS
# ==========================================================

choice = input(

    "\nReview skipped chunks? (y/n): "

).lower()

if choice == "y":

    for chunk in skipped_chunks:

        print("\n")

        print("=" * 80)

        print(

            f"Chunk ID : {chunk['chunk_id']}"

        )

        print(

            f"Pages    : "

            f"{chunk['start_page']}"

            f" - "

            f"{chunk['end_page']}"

        )

        print(

            f"Section  : "

            f"{chunk.get('section','Unknown')}"

        )

        print(

            f"Reason   : "

            f"{chunk['_filter_reason']}"

        )

        print()

        print("-" * 80)

        print(

            chunk["chunk_text"][:1000]

        )

        input(

            "\nPress ENTER for next..."

        )

# ==========================================================
# REVIEW KEPT CHUNKS
# ==========================================================

choice = input(

    "\nReview kept chunks? (y/n): "

).lower()

if choice == "y":

    for chunk in kept_chunks:

        print("\n")

        print("=" * 80)

        print(

            f"Chunk ID : {chunk['chunk_id']}"

        )

        print(

            f"Pages    : "

            f"{chunk['start_page']}"

            f" - "

            f"{chunk['end_page']}"

        )

        print(

            f"Section  : "

            f"{chunk.get('section','Unknown')}"

        )

        print()

        print("-" * 80)

        print(

            chunk["chunk_text"][:1000]

        )

        input(

            "\nPress ENTER for next..."

        )

print("\n")

print("=" * 80)

print("FILTER TEST COMPLETED")

print("=" * 80)