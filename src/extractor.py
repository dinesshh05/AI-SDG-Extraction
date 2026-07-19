import os
import json
import time

from dotenv import load_dotenv #type:ignore
from openai import OpenAI #type:ignore

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

# Metric values the LLM sometimes writes when no real metric exists,
# despite prompt instructions to leave the field blank instead. Used
# as a defensive backstop so a prompt slip doesn't leak into output.
_BAD_METRIC_VALUES = {"none", "n/a", "na", "null", "not applicable", "-", ""}


def _clean_metric(value):

    if not value:
        return ""

    if str(value).strip().lower() in _BAD_METRIC_VALUES:
        return ""

    return value


def extract_initiatives(text: str):

    prompt = f"""
You are an ESG and Sustainability analyst.

Your task is to extract sustainability initiatives from the provided annual report text.

Return ONLY a valid JSON array.

Do NOT:
- Return markdown
- Return explanations
- Return notes
- Wrap the response in ```json blocks

Schema:

[
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
  matter. A CSR committee being formed is not evidence for "Life
  Below Water" or "Partnerships for the Goals" just because CSR
  activities are discussed nearby in the report.
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
  as normal - a missing metric is NOT a reason to skip or exclude an
  initiative.
- NEVER write the word "None", "N/A", "null", "Not Applicable", or
  any placeholder text as the metric value. Leave it truly empty
  instead.

- Evidence must be copied verbatim from the report.
- Do not paraphrase evidence.
- Do not summarize evidence.
- Maximum evidence length: 300 characters.

- Use only information present in the provided text.
- Do not hallucinate.
- If no initiatives are found, return [].

TEXT:

{text}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)

    except Exception:

        # Remove accidental markdown wrappers if model adds them
        content = content.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        parsed = json.loads(content)

    # Defensive cleanup: strip placeholder "None"/"N/A" style values
    # that occasionally slip through despite prompt instructions, so
    # a missing metric never leaks into downstream output as literal
    # text like "(None)".
    for item in parsed:
        if "metric" in item:
            item["metric"] = _clean_metric(item["metric"])

    return parsed


# ---------------------------------------------------------------------
# Batched extraction
#
# extract_initiatives() above sends one fixed context to the LLM in a
# single call. That's a problem on two fronts when running on a free
# Groq tier against large retrieved-chunk pools:
#
#   1. Context/token limits - stuffing too many chunks into one call
#      risks hitting the model's context limit or the account's TPM cap.
#   2. Recall loss - if retrieval surfaces far more relevant chunks
#      than fit in one call, slicing to a fixed top-N (e.g. top 12)
#      throws away chunks that were correctly retrieved as relevant.
#
# The functions below split the retrieved, score-sorted chunk pool
# into token-budgeted batches, run extract_initiatives() once per
# batch, and merge the results. max_batches caps the total number of
# LLM calls per run so this stays within free-tier rate limits even
# when retrieval returns a large pool.
# ---------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate for budgeting purposes (~1.3 tokens per word
    for English text). Not exact, but good enough to keep batches
    safely under a token ceiling without adding a tokenizer dependency.
    """
    return int(len(text.split()) * 1.3)


def build_batches(results, max_tokens_per_batch=4000, max_batches=8):
    """
    Groups retrieved chunks (already sorted/ordered upstream) into
    token-budgeted batches.

    - Chunks are added to the current batch until adding the next one
      would exceed max_tokens_per_batch, at which point the batch is
      sealed and a new one starts.
    - Stops creating new batches once max_batches is reached. Since
      `results` is already ordered (best/most-representative first),
      anything left over at that point is the lowest-priority content
      in the pool - an acceptable tradeoff to stay within rate limits
      rather than firing an unbounded number of LLM calls.
    """

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

        if current_batch and (current_tokens + chunk_tokens) > max_tokens_per_batch:

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
    """
    Runs extraction across multiple token-budgeted batches instead of
    a single fixed-size call, then merges all results.

    Returns (all_initiatives, batch_errors) instead of just the
    initiatives list. Previously, a failed batch (rate limit, API
    error, malformed JSON) was only printed to console and silently
    skipped - if EVERY batch failed, the pipeline still completed
    "successfully" with a fully empty report and no error surfaced to
    the user. Returning batch_errors lets the caller detect this and
    fail loudly instead.

    - One extract_initiatives() call per batch, sequentially.
    - A short delay between calls to stay under free-tier RPM limits.
    - If a batch's call fails, that batch is skipped (with its error
      recorded) rather than crashing the whole run - one bad batch
      shouldn't lose everything else, but the caller now knows it
      happened.
    - Because chunk overlap and multiple retrieval queries can surface
      the same real-world initiative in more than one batch, the
      combined output can contain duplicates. This is expected -
      dedup is handled downstream, in excel_writer.py, after
      validation.
    """

    batches = build_batches(results, max_tokens_per_batch, max_batches)

    print(f"Running extraction across {len(batches)} batches...")

    all_initiatives = []
    batch_errors = []

    for i, batch in enumerate(batches):

        context = "\n".join(batch)

        print(f"  Batch {i+1}/{len(batches)} - {estimate_tokens(context)} est. tokens")

        try:
            initiatives = extract_initiatives(context)
            all_initiatives.extend(initiatives)

        except Exception as e:
            print(f"  Batch {i+1} failed: {e}")
            batch_errors.append(f"Batch {i+1}: {e}")
            continue

        if i < len(batches) - 1:
            time.sleep(delay_seconds)

    return all_initiatives, batch_errors