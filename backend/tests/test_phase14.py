"""Tests for Phase 14: AI-powered revision & improvement suggestions."""
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
from app.models.manuscript import (
    Manuscript, ManuscriptVersion,
    Evaluation, EvaluationIssue,
    ImprovementSuggestion, ImprovementTrack,
)
from app.manuscript_engine.revision import RevisionEngine

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
    j = Journal(slug="p14-j-" + uuid.uuid4().hex[:8], name="P14 Test")
    db.add(j); db.commit(); db.refresh(j)
    r = JournalRequirement(journal_id=j.id, key="structure", description="IMRaD", requirement_type="MANDATORY")
    db.add(r); db.commit()
    return j


def _make_manuscript(db, journal):
    m = Manuscript(title="P14 Manuscript", journal_id=journal.id, analysis_status="COMPLETED",
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
    issues = []
    for i in range(count):
        issue = EvaluationIssue(evaluation_id=evaluation_id, severity="major",
                                category="methodology", message=f"Test issue {i}",
                                is_blocking=False)
        db.add(issue)
        issues.append(issue)
    db.commit()
    return issues


# Engine Tests
def test_generate_suggestions_no_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id)
    assert result["status"] == "no_evaluation"


def test_generate_suggestions_with_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    assert result["status"] == "generated"
    assert len(result["suggestions"]) > 0


def test_generate_suggestions_fallback_on_llm_error(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    assert result["status"] == "generated"
    assert len(result["suggestions"]) >= 2


def test_list_suggestions_empty(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = RevisionEngine(db)
    suggestions = engine.list_suggestions(m.id)
    assert suggestions == []


def test_list_suggestions_filtered(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    assert len(result["suggestions"]) > 0
    all_suggestions = engine.list_suggestions(m.id)
    assert len(all_suggestions) > 0
    unaddressed = engine.list_suggestions(m.id, status="unaddressed")
    addressed = engine.list_suggestions(m.id, status="addressed")
    assert len(unaddressed) == len(all_suggestions)
    assert len(addressed) == 0


def test_list_suggestions_manuscript_not_found(db):
    engine = RevisionEngine(db)
    suggestions = engine.list_suggestions(99999)
    assert suggestions == []


def test_address_suggestion(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    suggestion_id = result["suggestions"][0]["id"]
    addressed = engine.address_suggestion(suggestion_id, m.id, version_id=v.id, reviewer="alice")
    assert addressed["is_addressed"] is True
    assert addressed["addressed_version_id"] == v.id


def test_address_suggestion_not_found(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = RevisionEngine(db)
    with pytest.raises(ValueError, match="not found"):
        engine.address_suggestion(99999, m.id)


def test_address_suggestion_wrong_manuscript(db):
    j1 = _make_journal(db)
    m1 = _make_manuscript(db, j1)
    j2 = _make_journal(db)
    m2 = _make_manuscript(db, j2)
    v1 = _make_version(db, m1)
    v2 = _make_version(db, m2)
    e1 = _make_evaluation(db, v1, j1.id)
    e2 = _make_evaluation(db, v2, j2.id)
    _make_issues(db, e1.id, 1)
    _make_issues(db, e2.id, 1)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m1.id, evaluation_id=e1.id)
    suggestion_id = result["suggestions"][0]["id"]
    with pytest.raises(ValueError, match="not found"):
        engine.address_suggestion(suggestion_id, m2.id)


def test_get_tracking_history(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    suggestion_id = result["suggestions"][0]["id"]
    engine.address_suggestion(suggestion_id, m.id, version_id=v.id, reviewer="bob")
    history = engine.get_tracking_history(suggestion_id)
    assert len(history) >= 1
    assert history[0]["action"] == "addressed"
    assert history[0]["reviewer"] == "bob"


def test_get_tracking_history_empty(db):
    engine = RevisionEngine(db)
    history = engine.get_tracking_history(99999)
    assert history == []


def test_get_improvement_summary(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    engine = RevisionEngine(db)
    engine.generate_suggestions(m.id, evaluation_id=e.id)
    summary = engine.get_improvement_summary(m.id)
    assert summary["manuscript_id"] == m.id
    assert summary["total_suggestions"] > 0
    assert summary["addressed"] == 0
    assert summary["unaddressed"] == summary["total_suggestions"]


def test_get_improvement_summary_after_addressing(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    suggestion_id = result["suggestions"][0]["id"]
    engine.address_suggestion(suggestion_id, m.id, version_id=v.id)
    summary = engine.get_improvement_summary(m.id)
    assert summary["addressed"] >= 1


def test_suggestion_to_dict(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(m.id, evaluation_id=e.id)
    suggestion_id = result["suggestions"][0]["id"]
    s = db.query(ImprovementSuggestion).filter(ImprovementSuggestion.id == suggestion_id).first()
    d = s.to_dict()
    assert "id" in d
    assert "title" in d
    assert "severity" in d


# API Tests
def test_api_list_suggestions_200(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/improvements")
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert data["total"] == 0


def test_api_list_suggestions_404():
    resp = client.get("/api/v1/manuscripts/99999/improvements")
    assert resp.status_code == 404


def test_api_generate_suggestions_no_evaluation(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/improvements/generate",
                       json={"force_regenerate": True})
    assert resp.status_code == 400


def test_api_generate_suggestions_success(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/improvements/generate",
                       json={"evaluation_id": e.id})
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data


def test_api_generate_suggestions_404():
    resp = client.post("/api/v1/manuscripts/99999/improvements/generate", json={})
    assert resp.status_code == 404


def test_api_address_suggestion(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    gen = client.post(f"/api/v1/manuscripts/{m.id}/improvements/generate",
                      json={"evaluation_id": e.id})
    suggestion_id = gen.json()["suggestions"][0]["id"]
    resp = client.post(
        f"/api/v1/manuscripts/{m.id}/improvements/{suggestion_id}/address",
        json={"version_id": v.id, "reviewer": "alice"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_addressed"] is True


def test_api_address_suggestion_404():
    resp = client.post(
        "/api/v1/manuscripts/99999/improvements/99999/address",
        json={"reviewer": "alice"},
    )
    assert resp.status_code == 404


def test_api_get_tracking_history(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 1)
    gen = client.post(f"/api/v1/manuscripts/{m.id}/improvements/generate",
                      json={"evaluation_id": e.id})
    suggestion_id = gen.json()["suggestions"][0]["id"]
    client.post(
        f"/api/v1/manuscripts/{m.id}/improvements/{suggestion_id}/address",
        json={"reviewer": "bob"},
    )
    resp = client.get(f"/api/v1/manuscripts/{m.id}/improvements/{suggestion_id}/tracking")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_get_improvement_summary(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v = _make_version(db, m)
    e = _make_evaluation(db, v, j.id)
    _make_issues(db, e.id, 2)
    client.post(f"/api/v1/manuscripts/{m.id}/improvements/generate",
                json={"evaluation_id": e.id})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/improvements/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manuscript_id"] == m.id
    assert data["total_suggestions"] >= 0


def test_api_get_improvement_summary_404():
    resp = client.get("/api/v1/manuscripts/99999/improvements/summary")
    assert resp.status_code == 404
