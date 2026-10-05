"""Test setup: isolated temp SQLite DB + storage, tables created up front.

Tests use ``TestClient(app)`` without a ``with`` block, so FastAPI's lifespan
(which normally runs ``create_all``) never fires. Create the schema here.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="lara-tests-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(_TMP / 'test.db').as_posix()}")
os.environ.setdefault("STORAGE_ROOT", str(_TMP / "storage"))
os.environ.setdefault("DOCUMENTS_ROOT", str(_TMP / "storage" / "documents"))

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
import app.models  # noqa: E402,F401

settings.resolved_storage_root.mkdir(parents=True, exist_ok=True)
settings.resolved_documents_root.mkdir(parents=True, exist_ok=True)
(settings.resolved_storage_root / "journals").mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)