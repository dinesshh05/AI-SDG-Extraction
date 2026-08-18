"""
Tracks extraction status per document: "processing" | "ready" | "failed",
plus granular phase info (mirroring the old Streamlit progress bar's
6 steps) and a warnings count (validation errors that were excluded
from the report — surfaced in the UI instead of only printed to
console, same as the original validator.py's intent).
"""

import sqlite3
import os

DB_PATH = os.environ.get("STATUS_DB_PATH", "./cache/status.db")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS document_status (
            document_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            report_path TEXT,
            error TEXT,
            warnings INTEGER,
            phase_label TEXT,
            phase_step INTEGER,
            phase_total INTEGER
        )"""
    )
    return conn


def set_status(document_id: str, status: str, report_path: str | None = None,
               error: str | None = None, warnings: int | None = None) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT INTO document_status (document_id, status, report_path, error, warnings)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(document_id) DO UPDATE SET
                 status=excluded.status, report_path=excluded.report_path,
                 error=excluded.error, warnings=excluded.warnings""",
            (document_id, status, report_path, error, warnings),
        )


def update_phase(document_id: str, step: int, total: int, label: str) -> None:
    """Called by the extractor's progress_callback during processing."""
    with _connect() as conn:
        conn.execute(
            """UPDATE document_status SET phase_label=?, phase_step=?, phase_total=?
               WHERE document_id=?""",
            (label, step, total, document_id),
        )


def get_status(document_id: str) -> str:
    with _connect() as conn:
        row = conn.execute(
            "SELECT status FROM document_status WHERE document_id = ?", (document_id,)
        ).fetchone()
    return row[0] if row else "unknown"


def get_full(document_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """SELECT status, report_path, error, warnings, phase_label, phase_step, phase_total
               FROM document_status WHERE document_id = ?""",
            (document_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "status": row[0],
        "report_path": row[1],
        "error": row[2],
        "warnings": row[3],
        "phase_label": row[4],
        "phase_step": row[5],
        "phase_total": row[6],
    }