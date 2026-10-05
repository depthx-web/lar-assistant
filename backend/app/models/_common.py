from __future__ import annotations

from datetime import datetime


def utcnow() -> datetime:
    """Naive UTC timestamp (SQLite friendly)."""
    return datetime.utcnow()


def iso(value):
    return value.isoformat() if value is not None else None