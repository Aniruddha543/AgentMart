"""
Append-only audit trail. Every tool call the agent makes gets logged here
BEFORE and AFTER execution, so a failed/declined step is on the record too,
not just the happy path. This is what you screenshot in the pitch.
"""
import json
from backend.db import get_conn


def log_event(session_id: str, step: str, detail: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_log (session_id, step, detail) VALUES (?, ?, ?)",
            (session_id, step, json.dumps(detail, default=str)),
        )


def get_audit_trail(session_id: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT step, detail, ts FROM audit_log WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return [
        {"step": r["step"], "detail": json.loads(r["detail"]), "ts": r["ts"]}
        for r in rows
    ]
