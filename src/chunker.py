from typing import List, Dict


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 500,
    overlap: int = 100
):
    
    all_words = []

    for page in pages:

        words = page["text"].split()

        for word in words:
            all_words.append(
                (
                    word,
                    page["page_no"]
                )
            )

    chunks = []

    chunk_counter = 0

    start = 0

    while start < len(all_words):

        end = start + chunk_size

        chunk_slice = all_words[start:end]

        if not chunk_slice:
            break

        chunk_text = " ".join(
            word
            for word, _
            in chunk_slice
        )

        start_page = chunk_slice[0][1]
        end_page = chunk_slice[-1][1]

        chunks.append(
            {
                "chunk_id": f"chunk_{chunk_counter}",
                "start_page": start_page,
                "end_page": end_page,
                "chunk_text": chunk_text
            }
        )

        chunk_counter += 1

        start += (chunk_size - overlap)

    return chunks