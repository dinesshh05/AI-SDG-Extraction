NOISE_TERMS = [
    "disclaimer",
    "abbreviations",
    "corporate snapshot",
    "notice",
    "financial statements",
    "standalone accounts",
    "consolidated accounts",
    "chairman's message",
    "ceo's message",
]


def is_noise_chunk(text: str):

    text = text.lower()

    matches = 0

    for term in NOISE_TERMS:

        if term in text:
            matches += 1

    return matches >= 2