import fitz  #type:ignore

def extract_pages(pdf_path: str):
    doc = fitz.open(pdf_path)

    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        text = page.get_text("text").strip()

        pages.append(
            {
                "page_no": page_index + 1,
                "text": text
            }
        )

    doc.close()

    return pages


