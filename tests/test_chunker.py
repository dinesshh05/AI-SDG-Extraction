import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from src.parser import extract_pages
from src.chunker import chunk_pages

pages = extract_pages(
    "input\Adani Port FY22.pdf"
)

chunks = chunk_pages(
    pages,
    chunk_size=500,
    overlap=100
)

print(f"Pages: {len(pages)}")

print(f"Chunks: {len(chunks)}")

print("\nFirst Chunk:\n")

print(
    chunks[0]["chunk_text"][:1000]
)

print("\nChunk Metadata:\n")

print("\nChunk Metadata:\n")

print(
    {
        "chunk_id":
        chunks[0]["chunk_id"],

        "start_page":
        chunks[0]["start_page"],

        "end_page":
        chunks[0]["end_page"]
    }
)

print(
    "\nWords:",
    len(
        chunks[0]["chunk_text"].split()
    )
)

print("\nChunk Lengths:\n")

for i in range(5):
    print(
        chunks[i]["chunk_id"],
        len(chunks[i]["chunk_text"].split())
    )