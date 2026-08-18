"""
Domain keyword list used to boost sustainability-relevant chunks during
retrieval. Split out from retrieval.py (now generic in retrieval_core)
since this list is SDG-extraction-specific, not something the chatbot's
general queries need.
"""

SUSTAINABILITY_KEYWORDS = [
    "sustainability",
    "esg",
    "environment",
    "renewable",
    "solar",
    "energy",
    "water",
    "waste",
    "recycling",
    "carbon",
    "emission",
    "emissions",
    "climate",
    "csr",
    "green",
    "pollution",
    "biodiversity",
    "greenhouse",
    "occupational health",
    "safety",
    "zero liquid discharge",
]