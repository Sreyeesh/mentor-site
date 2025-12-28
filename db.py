"""Simple SQLite helpers for tutoring checkout sessions."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Optional


DEFAULT_DB_NAME = 'tutoring.sqlite'


def _database_path(override: Optional[str] = None) -> Path:
    configured = override or os.getenv('DATABASE') or os.getenv('DATABASE_PATH')
    if configured:
        path = Path(configured)
    else:
        instance = Path('instance')
        instance.mkdir(exist_ok=True)
        path = instance / DEFAULT_DB_NAME
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_db(database_path: Optional[str] = None) -> Path:
    """Ensure the checkout_sessions table exists and return the DB path."""

    path = _database_path(database_path)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checkout_sessions (
            session_id TEXT PRIMARY KEY,
            customer_email TEXT,
            payment_status TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
    return path


def upsert_checkout_session(
    session_id: str,
    *,
    customer_email: Optional[str] = None,
    payment_status: Optional[str] = None,
    database_path: Optional[str] = None,
) -> None:
    """Insert or update a checkout session record."""

    path = _database_path(database_path)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        INSERT INTO checkout_sessions (session_id, customer_email, payment_status)
        VALUES (?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            customer_email=excluded.customer_email,
            payment_status=excluded.payment_status,
            updated_at=CURRENT_TIMESTAMP
        """,
        (session_id, customer_email, payment_status),
    )
    conn.commit()
    conn.close()


def get_checkout_session(
    session_id: str,
    *,
    database_path: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Return a stored checkout session if present."""

    path = _database_path(database_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT session_id, customer_email, payment_status, updated_at FROM checkout_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


__all__ = [
    'init_db',
    'upsert_checkout_session',
    'get_checkout_session',
]
