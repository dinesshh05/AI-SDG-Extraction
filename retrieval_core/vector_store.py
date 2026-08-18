"""
Namespaced sqlite embedding store. Same schema/approach as the original
vector_store.py, with one change: a `namespace` column (= f"doc_{document_id}")
so multiple documents' embeddings persist side by side instead of the
whole db being wiped before every run. This is what lets the chatbot
query a document's embeddings after the extractor already indexed it.
"""

import os
import sqlite3
import numpy as np

os.makedirs("cache", exist_ok=True)
DB_PATH = os.environ.get("EMBEDDINGS_DB_PATH", os.path.join("cache", "embeddings.db"))


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            namespace  TEXT NOT NULL,
            chunk_id   TEXT NOT NULL,
            start_page INTEGER,
            end_page   INTEGER,
            section    TEXT,
            chunk_text TEXT,
            embedding  BLOB,
            PRIMARY KEY (namespace, chunk_id)
        )
        """
    )
    conn.commit()
    conn.close()


def store_embedding(namespace, chunk_id, start_page, end_page, section, chunk_text, embedding):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO embeddings
        (namespace, chunk_id, start_page, end_page, section, chunk_text, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            namespace,
            chunk_id,
            start_page,
            end_page,
            section,
            chunk_text,
            embedding.astype(np.float32).tobytes(),
        ),
    )
    conn.commit()
    conn.close()


def fetch_all_embeddings(namespace):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT chunk_id, start_page, end_page, section, chunk_text, embedding
        FROM embeddings WHERE namespace = ?
        """,
        (namespace,),
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(
            {
                "chunk_id": row[0],
                "start_page": row[1],
                "end_page": row[2],
                "section": row[3],
                "chunk_text": row[4],
                "embedding": np.frombuffer(row[5], dtype=np.float32),
            }
        )
    return result


def delete_namespace(namespace):
    """Called before indexing to clear any stale rows for this namespace
    (defensive — document_ids are UUIDs so collisions shouldn't happen,
    but this keeps re-processing idempotent if it ever does)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM embeddings WHERE namespace = ?", (namespace,))
    conn.commit()
    conn.close()


def namespace_exists(namespace):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT 1 FROM embeddings WHERE namespace = ? LIMIT 1", (namespace,)
    ).fetchone()
    conn.close()
    return row is not None