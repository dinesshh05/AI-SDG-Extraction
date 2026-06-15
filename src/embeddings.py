from sentence_transformers import SentenceTransformer #type:ignore


model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)


def generate_embedding(text: str):
    """
    Generate embedding for a chunk.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding