import os
import json

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
        return json.loads(content)

    except Exception:

        # Remove accidental markdown wrappers if model adds them
        content = content.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        return json.loads(content)