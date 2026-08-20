"""
LLM-based initiative extraction.

Uses the OpenAI SDK pointed at Groq's OpenAI-compatible endpoint.
This module handles structured JSON extraction from sustainability
report text.
"""

import os
import json
import time

from dotenv import load_dotenv  # type: ignore
from openai import OpenAI  # type: ignore

load_dotenv()

LLM_API_KEY = os.getenv("GROQ_API_KEY")

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "https://api.groq.com/openai/v1"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama-3.3-70b-versatile"
)

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

_BAD_METRIC_VALUES = {
    "none",
    "n/a",
    "na",
    "null",
    "not applicable",
    "-",
    "",
}


def _clean_metric(value):
    if not value:
        return ""

    if str(value).strip().lower() in _BAD_METRIC_VALUES:
        return ""

    return value


def extract_initiatives(text: str):
    prompt = f"""
You are an ESG and Sustainability analyst.

Your task is to extract sustainability initiatives from the provided
annual report text.

Return ONLY a valid JSON object with an "initiatives" array.

Do NOT:
- Return markdown
- Return explanations
- Return notes
- Wrap the response in ```json blocks
- Add any text before or after the JSON object

Schema:

{{
  "initiatives": [
    {{
      "initiative_name": "",
      "description": "",
      "metric": "",
      "sdg_ids": [],
      "sdg_names": [],
      "evidence": "",
      "page_reference": ""
    }}
  ]
}}

Rules:

- Extract every sustainability initiative.
- Include renewable energy initiatives.
- Include climate action initiatives.
- Include biodiversity initiatives.
- Include waste management initiatives.
- Include water conservation initiatives.
- Include community development initiatives.
- Include CSR initiatives.
- Include employee wellbeing initiatives.
- Include governance and ESG initiatives if relevant.

- Map each initiative to the relevant UN SDGs.
- sdg_ids must contain only SDG numbers.
- sdg_names must contain the corresponding SDG names.

- Map each initiative to AT MOST 2-3 SDGs - only the ones it most
  directly and specifically addresses. Do not map an initiative to
  every SDG it could loosely be connected to.

- Generic administrative, compliance, or governance facts (e.g.
  "CSR Committee constituted under Section 135", "Company complies
  with the Companies Act, 2013", board meeting attendance records)
  are NOT initiatives on their own. Do not extract them as
  standalone initiatives, and never map them to environmental SDGs
  (6, 7, 12, 13, 14, 15) unless the surrounding text describes an
  actual environmental action, not just a compliance statement.

- Before assigning an SDG, check that the initiative's actual
  content - not just its category - matches that SDG's subject
  matter. A CSR committee being formed is not evidence for
  "Life Below Water" or "Partnerships for the Goals" just because
  CSR activities are discussed nearby in the report.

- For biodiversity initiatives involving coastal or marine ecosystems
  (e.g. mangrove afforestation, coral reef restoration): choose the
  SINGLE most appropriate SDG based on how the text frames the
  initiative, rather than tagging both SDG 14 (Life Below Water) and
  SDG 15 (Life on Land) by default. If the text frames it primarily
  as a climate mitigation or carbon sequestration effort, SDG 13
  (Climate Action) may be more appropriate than either 14 or 15.

- The "metric" field must contain the specific quantifiable figure
  from the evidence (a percentage, amount, tonnage, currency value,
  count, MWh/tCO2e/Ha figure, or similar) whenever the source text
  contains one for this initiative.

- If the initiative genuinely has no specific number attached to it,
  set "metric" to an empty string "" and still return the initiative
  as normal - a missing metric is NOT a reason to skip or exclude
  an initiative.

- NEVER write the word "None", "N/A", "null", "Not Applicable", or
  any placeholder text as the metric value. Leave it truly empty
  instead.

- Evidence must be copied verbatim from the report.
- Do not paraphrase evidence.
- Do not summarize evidence.
- Maximum evidence length: 300 characters.

- Use only information present in the provided text.
- Do not hallucinate.
- If no initiatives are found, return:
  {{"initiatives": []}}

TEXT:

{text}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
    except Exception:
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        parsed = json.loads(content)

    # The model now returns:
    #
    # {
    #     "initiatives": [...]
    # }
    #
    # Convert it back into the list expected by the rest
    # of the existing pipeline.
    if isinstance(parsed, dict):
        parsed = parsed.get("initiatives", [])

    if not isinstance(parsed, list):
        raise ValueError(
            "LLM returned an invalid JSON structure. "
            "Expected an 'initiatives' array."
        )

    for item in parsed:
        if "metric" in item:
            item["metric"] = _clean_metric(item["metric"])

    return parsed


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)


def build_batches(results, max_tokens_per_batch=4000, max_batches=8):
    batches = []
    current_batch = []
    current_tokens = 0

    for result in results:
        chunk = result["chunk"]

        chunk_text = f"""
SECTION: {chunk.get('section', '')}
PAGES: {chunk['start_page']}-{chunk['end_page']}

TEXT:
{chunk['chunk_text']}
"""

        chunk_tokens = estimate_tokens(chunk_text)

        if (
            current_batch
            and (current_tokens + chunk_tokens) > max_tokens_per_batch
        ):
            batches.append(current_batch)

            current_batch = []
            current_tokens = 0

            if len(batches) >= max_batches:
                break

        current_batch.append(chunk_text)
        current_tokens += chunk_tokens

    if current_batch and len(batches) < max_batches:
        batches.append(current_batch)

    return batches


def extract_initiatives_batched(
    results,
    max_tokens_per_batch=4000,
    max_batches=8,
    delay_seconds=2
):
    batches = build_batches(
        results,
        max_tokens_per_batch,
        max_batches
    )

    print(
        f"Running extraction across {len(batches)} batches..."
    )

    all_initiatives = []
    batch_errors = []

    for i, batch in enumerate(batches):
        context = "\n".join(batch)

        print(
            f"  Batch {i+1}/{len(batches)} - "
            f"{estimate_tokens(context)} est. tokens"
        )

        try:
            initiatives = extract_initiatives(context)

            all_initiatives.extend(initiatives)

        except Exception as e:
            print(
                f"  Batch {i+1} failed: {e}"
            )

            batch_errors.append(
                f"Batch {i+1}: {e}"
            )

            continue

        if i < len(batches) - 1:
            time.sleep(delay_seconds)

    return all_initiatives, batch_errors