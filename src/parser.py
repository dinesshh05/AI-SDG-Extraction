import re
import fitz #type:ignore

NUMBERED_HEADING_RE = re.compile(
    r"^\s*\d+(\.\d+)*[\.\)]?\s+[A-Za-z]"
)

ROMAN_HEADING_RE = re.compile(
    r"^\s*[IVXLCDM]+\.\s+[A-Za-z]",
    re.IGNORECASE
)

SECTION_KEYWORDS = {

    "business responsibility",
    "sustainability report",
    "management discussion",
    "corporate governance",
    "board report",
    "director report",
    "directors report",
    "annexure",
    "appendix",
    "principle",
    "section",
    "chapter",
    "csr",
    "esg",
    "risk management",
    "environment",
    "health and safety",
    "human resources",
    "financial statements",
    "notes to accounts"

}

BAD_HEADINGS = {

    "iso",
    "as 9100",
    "registered office",
    "corporate office",
    "telephone",
    "phone",
    "fax",
    "email",
    "website",
    "cin",
    "bse",
    "nse"

}


def _is_heading(text: str):

    text = " ".join(
        text.strip().split()
    )

    if not text:
        return False

    lower = text.lower()

    # ------------------------------------
    # Reject obvious non-headings first
    # ------------------------------------

    for phrase in BAD_HEADINGS:

        if phrase in lower:
            return False

    # ------------------------------------
    # Numbered headings
    # ------------------------------------

    if NUMBERED_HEADING_RE.match(text):
        return True

    # ------------------------------------
    # Roman numeral headings
    # ------------------------------------

    if ROMAN_HEADING_RE.match(text):
        return True

    # ------------------------------------
    # Known section names
    # ------------------------------------

    for keyword in SECTION_KEYWORDS:

        if keyword in lower:
            return True

    return False

def extract_pages(pdf_path):

    doc = fitz.open(pdf_path)

    pages = []

    for page_number in range(len(doc)):

        page = doc[page_number]

        raw_blocks = page.get_text(
            "blocks"
        )

        raw_blocks = sorted(
            raw_blocks,
            key=lambda x: (
                round(x[1], 1),
                x[0]
            )
        )

        blocks = []

        for block in raw_blocks:

            text = block[4].strip()

            if not text:
                continue

            if text.isdigit():
                continue

            blocks.append(
                {
                    "text": text,

                    "is_heading": _is_heading(
                        text
                    )
                }
            )

        pages.append(
            {
                "page_no": page_number + 1,

                "blocks": blocks
            }
        )

    doc.close()

    return pages