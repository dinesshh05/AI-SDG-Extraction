import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from retrieval_core.vector_store import fetch_all_embeddings


chunks = fetch_all_embeddings()

print(f"\nTotal Chunks : {len(chunks)}")

for chunk in chunks:

    text = chunk["chunk_text"]

    words = text.split()

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]

    # ---------- Statistics ----------

    word_count = len(words)

    line_count = len(lines)

    paragraph_count = len(paragraphs)

    avg_line_length = (
        sum(len(line) for line in lines) / line_count
        if line_count else 0
    )

    numeric_words = sum(
        1
        for word in words
        if any(ch.isdigit() for ch in word)
    )

    numeric_ratio = (
        numeric_words / word_count
        if word_count else 0
    )

    unique_lines = len(set(lines))

    repeated_lines = line_count - unique_lines

    print("\n" + "=" * 90)

    print(f"Chunk ID      : {chunk['chunk_id']}")

    print(
        f"Pages         : {chunk['start_page']} - {chunk['end_page']}"
    )

    print(
        f"Section       : {chunk.get('section','Unknown')}"
    )

    print(
        f"Heading Found : {chunk.get('section','Unknown') != 'Unknown'}"
    )

    print()

    print(f"Words         : {word_count}")

    print(f"Lines         : {line_count}")

    print(f"Paragraphs    : {paragraph_count}")

    print(
        f"Average Line Length : {avg_line_length:.2f}"
    )

    print(
        f"Numeric Ratio : {numeric_ratio:.2f}"
    )

    print(
        f"Repeated Lines : {repeated_lines}"
    )

    print(
        f"Characters      : {len(text)}"
    )

    print("\nPreview\n")

    print(text[:800])

    input("\nPress ENTER for next chunk...")