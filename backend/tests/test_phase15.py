"""Tests for Phase 15: Peer review response letter generation."""
from __future__ import annotations

import sys
import uuid
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine as db_engine
from app.models.journal import Journal, JournalRequirement
from app.models.manuscript import Manuscript, ManuscriptVersion, Evaluation, EvaluationIssue, ImprovementSuggestion, PeerReviewResponseLetter
from app.manuscript_engine.response_letter import ResponseLetterEngine

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=db_engine)
    yield


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _make_journal(db):
    j = Journal(slug="p15-j-" + uuid.uuid4().hex[:8], name="P15 Test")
    db.add(j); db.commit(); db.refresh(j)
    r = JournalRequirement(journal_id=j.id, key="structure", description="IMRaD", requirement_type="MANDATORY")
    db.add(r); db.commit()
    return j


def _make_manuscript(db, journal):
    m = Manuscript(title="P15 Manuscript", journal_id=journal.id, analysis_status="COMPLETED",
                   overall_compliance_score=85.0, mandatory_compliance_score=100.0)
    db.add(m); db.commit(); db.refresh(m)
    return m


def _make_version(db, manuscript, version=1):
    v = ManuscriptVersion(manuscript_id=manuscript.id, version=version,
                          content_path=f"v{version}.txt", content_hash=f"hash{version}")
    db.add(v); db.commit(); db.refresh(v)
    return v


def _make_evaluation(db, manuscript_version, journal_id):
    e = Evaluation(manuscript_version_id=manuscript_version.id, journal_id=journal_id,
                   status="COMPLETED", compliance_score=80, scientific_score=75,
                   methodology_score=70, writing_score=85, novelty_score=60,
                   readiness_score=70, final_status="READY", model="test", prompt_version="v1")
    db.add(e); db.commit(); db.refresh(e)
    return e


def _make_issues(db, evaluation_id, count=3):
    for i in range(count):
        issue = EvaluationIssue(evaluation_id=evaluation_id, severity="major",
                                category="methodology", message=f"Test issue {i}", is_blocking=False)
        db.add(issue)
    db.commit()


# Engine Tests
def test_generate_letter_no_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = ResponseLetterEngine(db)
    result = engine.generate_response_letter(m.id)
    assert result["status"] == "no_evaluation"


def test_generate_letter_with_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = ResponseLetterEngine(db)
    result = engine.generate_response_letter(m.id, evaluation_id=e.id)
    assert result["status"] == "generated"
    assert result["letter_id"] is not None


def test_generate_letter_falls_back(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = ResponseLetterEngine(db)
    result = engine.generate_response_letter(m.id, evaluation_id=e.id)
    assert result["status"] == "generated"
    letter = engine.get_letter(result["letter_id"])
    assert letter is not None
    assert letter["cover_letter"] is not None
    assert letter["response_body"] is not None


def test_get_letter_not_found(db):
    engine = ResponseLetterEngine(db)
    result = engine.get_letter(99999)
    assert result is None


def test_list_letters_empty(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = ResponseLetterEngine(db)
    letters = engine.list_letters(m.id)
    assert letters == []


def test_regenerate_letter(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    engine = ResponseLetterEngine(db)
    result = engine.generate_response_letter(m.id, evaluation_id=e.id)
    letter_id = result["letter_id"]
    regen = engine.regenerate_letter(letter_id)
    assert regen["status"] == "generated"


def test_regenerate_nonexistent(db):
    engine = ResponseLetterEngine(db)
    with pytest.raises(ValueError):
        engine.regenerate_letter(99999)


# API Tests
def test_api_generate_letter_no_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={})
    assert resp.status_code == 400


def test_api_generate_letter_success(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={"evaluation_id": e.id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["manuscript_id"] == m.id
    assert data["cover_letter"] is not None


def test_api_generate_letter_404():
    resp = client.post("/api/v1/manuscripts/99999/response-letters/generate", json={})
    assert resp.status_code == 404


def test_api_list_letters_empty(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/response-letters")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


def test_api_list_letters_after_generate(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={"evaluation_id": e.id})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/response-letters")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


def test_api_list_letters_404():
    resp = client.get("/api/v1/manuscripts/99999/response-letters")
    assert resp.status_code == 404


def test_api_get_letter(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    gen = client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={"evaluation_id": e.id})
    letter_id = gen.json()["id"]
    resp = client.get(f"/api/v1/manuscripts/{m.id}/response-letters/{letter_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == letter_id


def test_api_get_letter_404():
    resp = client.get("/api/v1/manuscripts/99999/response-letters/99999")
    assert resp.status_code == 404


def test_api_summary(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/response-letters/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manuscript_id"] == m.id
    assert data["total_letters"] == 0


def test_api_summary_after_generate(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={"evaluation_id": e.id})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/response-letters/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_letters"] >= 1
    assert data["has_cover_letter"] is True
    assert data["has_response_body"] is True


def test_api_regenerate(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    gen = client.post(f"/api/v1/manuscripts/{m.id}/response-letters/generate", json={"evaluation_id": e.id})
    letter_id = gen.json()["id"]
    resp = client.post(f"/api/v1/manuscripts/{m.id}/response-letters/{letter_id}/regenerate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == letter_id

