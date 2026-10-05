from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args: dict = {}
if settings.resolved_database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Make sure the folder for the SQLite file exists (e.g. ./data on a fresh server)
    _db_path = settings.resolved_database_url.replace("sqlite:///", "", 1)
    if _db_path and _db_path != ":memory:":
        Path(_db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.resolved_database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():  # type: ignore
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()