"""
Chunk Quality Filter

This is not a relevance classifier. It does not try to decide whether
a chunk is "about SDGs." It only answers one narrow question:

    "Is this chunk obviously useless for retrieval?"

Design rule: when in doubt, KEEP the chunk. A false positive (dropping
something useful) is far more costly than a false negative (keeping a
few noisy chunks) - retrieval and the LLM can ignore noise later, but
they can never recover a chunk that never made it into the vector
store.

Five noise categories are checked, in order. The first match wins.
Anything that matches none of them is kept by default.

IMPORTANT: categories 1-3 (contact info, AGM/legal notices, table of
contents) are anchored to the chunk's SECTION LABEL first, not its raw
body text. This matters because real sustainability content sometimes
shares a page - or even a numbered list - with excluded topics (e.g.
a BRSR section sitting right next to "Dividend Distribution Policy"
in the same Director's Report). Matching on section label is precise;
matching on raw text would risk killing the BRSR chunk too, just
because it happens to mention "notice" somewhere. Raw-text matching is
only used as a narrow fallback when no section label is available,
and only for genuinely unambiguous boilerplate shapes (e.g. a chunk
that's nothing but "Phone / Fax / Email / Website").
"""

from typing import Dict, List, Optional, Tuple


SECTION_INCLUDE_PATTERNS = [
    "business responsibility", "sustainability", "csr",
    "corporate social responsibility", "esg", "environment",
    "energy", "waste", "water", "emission", "carbon", "climate",
    "biodiversity","health and safety",
    "diversity", "human rights", "ethics", 
    
]

CONTACT_SECTION_PATTERNS = [
    "registered office", "corporate office", "corporate information",
    "investor information", "registrar",
]

CONTACT_LABEL_WORDS = {
    "phone", "fax", "email", "website", "cin", "tel", "telephone",
    "pin", "gstin", "din",
}

NOTICE_SECTION_PATTERNS = [
    "notice of", "agm", "annual general meeting", "e-voting", "proxy",
    "attendance slip", "route map", "postal ballot",
]

TOC_SECTION_PATTERNS = ["contents", "index", "abbreviations"]

MAX_DIGIT_RATIO = 0.60
MIN_WORD_COUNT = 12

BLANK_PAGE_PHRASES = {
    "this page is intentionally left blank",
    "intentionally left blank",
}


def _section_text(chunk: Dict) -> str:
    return (chunk.get("section") or "").lower()


def _matches_any(text: str, patterns: List[str]) -> Optional[str]:
    for pattern in patterns:
        if pattern in text:
            return pattern
    return None


def _digit_ratio(text: str) -> float:
    if not text:
        return 0.0
    digits = sum(c.isdigit() for c in text)
    return digits / len(text)


def _is_section_included(chunk: Dict) -> Optional[str]:
    """Sustainability section override - checked before every exclude rule."""
    return _matches_any(_section_text(chunk), SECTION_INCLUDE_PATTERNS)


def _is_contact_boilerplate(chunk: Dict) -> Optional[str]:

    section = _section_text(chunk)

    match = _matches_any(section, CONTACT_SECTION_PATTERNS)
    if match:
        return match

    if section in ("", "document start"):

        words = [w.strip(":.,").lower() for w in chunk["chunk_text"].split()]
        words = [w for w in words if w]

        if not words:
            return None

        label_hits = sum(1 for w in words if w in CONTACT_LABEL_WORDS)

        if len(words) <= 12 and label_hits >= 2:
            return "contact_label_pattern"

    return None


def _is_agm_notice(chunk: Dict) -> Optional[str]:
    return _matches_any(_section_text(chunk), NOTICE_SECTION_PATTERNS)


def _is_table_of_contents(chunk: Dict) -> Optional[str]:
    return _matches_any(_section_text(chunk), TOC_SECTION_PATTERNS)


def _is_blank_or_tiny(chunk: Dict) -> Optional[str]:

    text = chunk["chunk_text"].strip()
    lowered = text.lower()

    for phrase in BLANK_PAGE_PHRASES:
        if phrase in lowered:
            return "blank_page"

    word_count = len(text.split())

    if word_count < MIN_WORD_COUNT:
        return f"too_short:{word_count}_words"

    return None


def _is_numeric_heavy(chunk: Dict) -> Optional[str]:

    ratio = _digit_ratio(chunk["chunk_text"])

    if ratio > MAX_DIGIT_RATIO:
        return f"high_digit_ratio:{ratio:.2f}"

    return None


def evaluate_chunk(chunk: Dict) -> Dict:
    """
    Returns an explainable keep/skip decision for a single chunk.
    """

    include_match = _is_section_included(chunk)
    if include_match:
        return {"keep": True, "reason": f"section_override:{include_match}"}

    checks = [
        ("contact_boilerplate", _is_contact_boilerplate),
        ("agm_notice", _is_agm_notice),
        ("table_of_contents", _is_table_of_contents),
        ("blank_or_tiny", _is_blank_or_tiny),
        ("numeric_heavy", _is_numeric_heavy),
    ]

    for label, check_fn in checks:

        match = check_fn(chunk)

        if match:
            return {"keep": False, "reason": f"{label}:{match}"}

    return {"keep": True, "reason": "meaningful_content"}


def filter_chunks(chunks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Splits chunks into (kept, skipped), annotating each with the
    reason for its decision so nothing disappears silently.
    """

    kept = []
    skipped = []

    for chunk in chunks:

        decision = evaluate_chunk(chunk)
        chunk["_filter_reason"] = decision["reason"]

        if decision["keep"]:
            kept.append(chunk)
        else:
            skipped.append(chunk)

    return kept, skipped