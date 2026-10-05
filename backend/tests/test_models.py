from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
import app.models  # noqa: F401  ensure metadata


def test_create_all_in_memory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    # check expected tables exist
    tables = set(Base.metadata.tables.keys())
    for expected in ["documents", "document_chunks", "collections", "journals", "journal_requirements", "manuscripts", "manuscript_versions", "evaluations", "jobs", "models", "projects"]:
        assert expected in tables
