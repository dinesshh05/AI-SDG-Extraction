"""
Thin wrapper around the Groq chat completions call for conversational
replies.
"""

import os
import time
from dotenv import load_dotenv
from groq import Groq, APIStatusError

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = os.environ.get("CHAT_LLM_MODEL", "llama-3.3-70b-versatile")
MAX_RETRIES = 2
MAX_HISTORY_TURNS = 6  # keep last 6 user/assistant pairs, cap token growth


def generate_reply(system_context: str, history: list[dict], user_message: str) -> str:
    """
    history is a list of {"role": "user"|"assistant", "content": str},
    oldest first. Trimmed to the last MAX_HISTORY_TURNS turns so the
    prompt doesn't grow unbounded over a long conversation.
    """

    trimmed_history = history[-(MAX_HISTORY_TURNS * 2):]

    messages = (
        [{"role": "system", "content": system_context}]
        + trimmed_history
        + [{"role": "user", "content": user_message}]
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = _client.chat.completions.create(model=MODEL, messages=messages)
            return response.choices[0].message.content

        except APIStatusError as e:
            if e.status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            if e.status_code == 429:
                return "I'm getting a lot of requests right now — please try again in a moment."
            raise