from typing import List, Dict
import re


NUMBERED_HEADING_RE = re.compile(r"^\(?\d{1,3}\)?[\.\)]\s+\S")


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 500,
    overlap_blocks: int = 2,
    min_words_before_section_break: int = 150
):
    """
    Chunks a document by walking text blocks in order, instead of
    flattening the whole document into one word stream.

    Improvements over the old word-sliding-window approach:

    - Chunks are built from whole blocks (paragraphs), never cut
      mid-sentence.
    - A heading is never separated from the body text that follows it,
      as long as the current chunk already has reasonable content
      (controlled by min_words_before_section_break). This stops a
      chunk from straddling two unrelated sections (e.g. BRSR and
      Credit Rating ending up in the same chunk).
    - Each chunk is tagged with the section heading it falls under,
      giving retrieval/filtering a much stronger signal than raw
      keyword counting over chunk text.
    - Overlap is block-level, not word-count-level, so it can never
      slice a sentence in half.
    """

    flat = []
    current_section = "Document Start"

    for page in pages:
        for block in page["blocks"]:

            if block["is_heading"]:
                current_section = block["text"]

            flat.append(
                {
                    "text": block["text"],
                    "page_no": page["page_no"],
                    "is_heading": block["is_heading"],
                    "section": current_section
                }
            )

    chunks = []
    chunk_counter = 0
    i = 0
    n = len(flat)

    while i < n:

        current_blocks = []
        word_count = 0
        start_i = i

        while i < n:

            block = flat[i]
            block_words = len(block["text"].split())

            is_numbered_heading = bool(
                NUMBERED_HEADING_RE.match(block["text"])
            )

            # A numbered section heading always starts a new chunk -
            # it's the reliable signal for this report family, and
            # letting a short section get silently absorbed into the
            # previous chunk causes its content to be mislabeled
            # under the wrong section.
            if current_blocks and block["is_heading"] and is_numbered_heading:
                break

            # Weaker bold-only headings only force a break once the
            # current chunk already has substantial content, so we
            # don't fragment on every noisy bold label.
            if (
                current_blocks
                and block["is_heading"]
                and not is_numbered_heading
                and word_count >= min_words_before_section_break
            ):
                break

            if current_blocks and (word_count + block_words) > chunk_size:
                break

            current_blocks.append(block)
            word_count += block_words
            i += 1

        if not current_blocks:
            # A single block alone exceeds chunk_size; include it as
            # its own chunk rather than dropping it.
            current_blocks.append(flat[i])
            i += 1

        chunk_text = "\n".join(
            b["text"] for b in current_blocks
        )

        start_page = current_blocks[0]["page_no"]
        end_page = current_blocks[-1]["page_no"]

        section = (
            current_blocks[0]["section"]
            or current_blocks[-1]["section"]
        )

        chunks.append(
            {
                "chunk_id": f"chunk_{chunk_counter}",
                "start_page": start_page,
                "end_page": end_page,
                "section": section,
                "chunk_text": chunk_text
            }
        )

        chunk_counter += 1

        # Block-level overlap: step back a couple of blocks so context
        # carries across the boundary, but always make forward progress.
        i = max(start_i + 1, i - overlap_blocks)

    return chunks