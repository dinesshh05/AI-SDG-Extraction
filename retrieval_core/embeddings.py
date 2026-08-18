"""
Embedding logic shared by the extractor and the chatbot. Ported from the
original embeddings.py, unchanged model choice.
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_VERSION = "bge-small-en-v1.5"  # bump if MODEL_NAME ever changes

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def generate_embedding(text: str):
    """Embed a single string. Used both for chunks (indexing) and for
    queries (with the BGE query prefix added by the caller in retrieval.py)."""
    model = _get_model()
    return model.encode(text, normalize_embeddings=True)