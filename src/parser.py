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


if __name__ == "__main__":

    pdf_path = "input\Adani Port FY22.pdf"

    pages = extract_pages(pdf_path)

    print(f"Total Pages: {len(pages)}")

    print("\nFirst Page Preview:\n")
    print(pages[0]["text"][:1000])

    empty_pages = [
        page["page_no"]
        for page in pages
        if not page["text"]
    ]

    print(f"\nEmpty Pages: {empty_pages}")