from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Versioned health check")
def health_check(db: Session = Depends(get_db)) -> HealthResponse:  # type: ignore
    # DB check
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:  # noqa: BLE001
        db_status = f"error: {e}"

    # Storage check
    try:
        root = settings.resolved_storage_root
        root.mkdir(parents=True, exist_ok=True)
        docs = settings.resolved_documents_root
        docs.mkdir(parents=True, exist_ok=True)
        # write probe
        probe = docs / ".health_probe"
        probe.write_text(str(time.time()), encoding="utf-8")
        storage_status = "ok"
    except Exception as e:  # noqa: BLE001
        storage_status = f"error: {e}"

    return HealthResponse(status="ok", version=__version__, database=db_status, storage=storage_status)
