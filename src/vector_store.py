import os
import sqlite3 
import numpy as np  #type:ignore


os.makedirs(
    "cache",
    exist_ok=True
)

DB_PATH = os.path.join(
    "cache",
    "embeddings.db"
)


def init_db():

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            chunk_id TEXT PRIMARY KEY,
            start_page INTEGER,
            end_page INTEGER,
            chunk_text TEXT,
            embedding BLOB
        )
        """
    )

    conn.commit()
    conn.close()


def store_embedding(
    chunk_id,
    start_page,
    end_page,
    chunk_text,
    embedding
):

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT OR REPLACE INTO embeddings
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            chunk_id,
            start_page,
            end_page,
            chunk_text,
            embedding.astype(
                np.float32
            ).tobytes()
        )
    )

    conn.commit()
    conn.close()


def fetch_all_embeddings():

    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        """
        SELECT *
        FROM embeddings
        """
    ).fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append(
            {
                "chunk_id": row[0],
                "start_page": row[1],
                "end_page": row[2],
                "chunk_text": row[3],
                "embedding": np.frombuffer(
                    row[4],
                    dtype=np.float32
                )
            }
        )

    return result