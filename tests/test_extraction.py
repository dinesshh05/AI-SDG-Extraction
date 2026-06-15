from src.validator import validate_initiatives

from src.excel_writer import (
    export_to_excel
)

from src.retrieval import (
    retrieve_sustainability_chunks
)

from src.query_bank import (
    SUSTAINABILITY_QUERIES
)

from src.extractor import (
    extract_initiatives
)

# Retrieve sustainability-related chunks
results = retrieve_sustainability_chunks(
    SUSTAINABILITY_QUERIES,
    top_k_per_query=5
)

# Build context for the LLM
context = ""

for result in results[:8]:

    chunk = result["chunk"]

    context += f"""

PAGES: {chunk['start_page']}-{chunk['end_page']}

TEXT:
{chunk['chunk_text']}

"""

print("Retrieved Chunks:", len(results))

print("\nSending Context To LLM...\n")

print(
    f"\nContext Length: {len(context)} characters"
)

initiatives = extract_initiatives(
    context
)

validated = validate_initiatives(
    initiatives
)

print(
    f"\nValidated Records: {len(validated)}"
)

import json

print(
    json.dumps(
        validated,
        indent=4,
        ensure_ascii=False
    )
)

export_to_excel(
    validated
)