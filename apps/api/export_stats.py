from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path
from threading import Lock

_DB_LOCK = Lock()


def _db_path() -> Path:
    configured = os.getenv("EXPORT_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent / "data" / "export_counts.db"


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS export_counts (
            date TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def increment_export_count() -> None:
    with _DB_LOCK:
        conn = _connect()
        try:
            _ensure_schema(conn)
            today_key = date.today().isoformat()
            conn.execute(
                """
                INSERT INTO export_counts (date, count)
                VALUES (?, 1)
                ON CONFLICT(date) DO UPDATE SET count = count + 1
                """,
                (today_key,),
            )
            conn.commit()
        finally:
            conn.close()


def get_export_stats() -> dict:
    with _DB_LOCK:
        conn = _connect()
        try:
            _ensure_schema(conn)
            today_key = date.today().isoformat()
            cursor = conn.execute(
                "SELECT count FROM export_counts WHERE date = ?", (today_key,)
            )
            row = cursor.fetchone()
            today_count = int(row[0]) if row else 0

            cursor = conn.execute("SELECT COALESCE(SUM(count), 0) FROM export_counts")
            total_count = int(cursor.fetchone()[0] or 0)
        finally:
            conn.close()

    return {"today": today_count, "total": total_count}
