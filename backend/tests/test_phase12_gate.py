"""Tests for Phase 12: Final Pre-Submission Gate."""
from __future__ import annotations

import json
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
from app.models.manuscript import Manuscript, ManuscriptVersion, Evaluation
from app.manuscript_engine.gate import PreSubmissionGate, BlockingRule

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
    j = Journal(slug="p12-j-" + uuid.uuid4().hex[:8], name="P12 Test")
    db.add(j)
    db.commit()
    db.refresh(j)
    r = JournalRequirement(journal_id=j.id, key="structure", description="IMRaD", requirement_type="MANDATORY")
    db.add(r)
    db.commit()
    return j


def _make_ready_manuscript(db, journal):
    m = Manuscript(title="Ready Manuscript", journal_id=journal.id, analysis_status="COMPLETED",
                   overall_compliance_score=85.0, mandatory_compliance_score=100.0, rejection_risks="[]")
    db.add(m); db.commit(); db.refresh(m)
    return m


def _make_pending_manuscript(db, journal):
    m = Manuscript(title="Pending Manuscript", journal_id=journal.id, analysis_status="PENDING",
                   overall_compliance_score=50.0, mandatory_compliance_score=60.0,
                   rejection_risks=json.dumps([{"severity": "high", "type": "structure"}]))
    db.add(m); db.commit(); db.refresh(m)
    return m


def test_gate_readiness_completed(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db, readiness_threshold=70.0)
    result = gate.check_readiness(m.id)
    assert result["ready_to_submit"] is True
    assert len(result["blocking_issues"]) == 0
    assert result["readiness_score"] >= 70.0


def test_gate_readiness_pending(db):
    j = _make_journal(db)
    m = _make_pending_manuscript(db, j)
    gate = PreSubmissionGate(db, readiness_threshold=70.0)
    result = gate.check_readiness(m.id)
    assert result["ready_to_submit"] is False
    assert len(result["blocking_issues"]) > 0


def test_gate_readiness_no_journal(db):
    m = Manuscript(title="No Journal", journal_id=None, analysis_status="COMPLETED",
                   overall_compliance_score=90.0, mandatory_compliance_score=100.0)
    db.add(m); db.commit(); db.refresh(m)
    gate = PreSubmissionGate(db)
    result = gate.check_readiness(m.id)
    assert result["ready_to_submit"] is False
    blocking = [i["rule"] for i in result["blocking_issues"]]
    assert "no_journal" in blocking


def test_gate_readiness_nonexistent(db):
    gate = PreSubmissionGate(db)
    with pytest.raises(ValueError, match="not found"):
        gate.check_readiness(99999)


def test_gate_custom_rule(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db)
    gate.add_rule(BlockingRule(rule_id="custom_block", severity="critical", message_template="Custom", check_fn=lambda m, db: True))
    result = gate.check_readiness(m.id)
    assert result["ready_to_submit"] is False
    blocking = [i["rule"] for i in result["blocking_issues"]]
    assert "custom_block" in blocking


def test_gate_components(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db)
    components = gate._compute_readiness_components(m)
    factors = [c["factor"] for c in components]
    assert "overall_compliance" in factors
    assert "mandatory_compliance" in factors
    assert "analysis_complete" in factors
    assert "rejection_risk_adjustment" in factors


def test_gate_weighted_readiness():
    gate = PreSubmissionGate.__new__(PreSubmissionGate)
    gate.readiness_threshold = 70.0
    components = [
        {"factor": "overall_compliance", "score": 80.0},
        {"factor": "mandatory_compliance", "score": 100.0},
        {"factor": "analysis_complete", "score": 100.0},
        {"factor": "rejection_risk_adjustment", "score": 100.0},
    ]
    score = gate._weighted_readiness(components)
    assert 70 <= score <= 100


def test_create_final_version_blocked(db):
    j = _make_journal(db)
    m = _make_pending_manuscript(db, j)
    gate = PreSubmissionGate(db)
    result = gate.create_final_version(m.id)
    assert result["ready_to_submit"] is False
    assert result["version_id"] is None


def test_create_final_version_allowed(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db)
    result = gate.create_final_version(m.id, change_summary="Final")
    assert result["ready_to_submit"] is True
    assert result["version_id"] is not None
    v = db.query(ManuscriptVersion).filter(ManuscriptVersion.id == result["version_id"]).first()
    assert v is not None
    assert v.manuscript_id == m.id


def test_create_final_version_sequential(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db)
    r1 = gate.create_final_version(m.id)
    r2 = gate.create_final_version(m.id)
    assert r1["version_id"] != r2["version_id"]
    v1 = db.query(ManuscriptVersion).filter(ManuscriptVersion.id == r1["version_id"]).first()
    v2 = db.query(ManuscriptVersion).filter(ManuscriptVersion.id == r2["version_id"]).first()
    assert v2.version == v1.version + 1


def test_create_final_version_nonexistent(db):
    gate = PreSubmissionGate(db)
    with pytest.raises(ValueError, match="not found"):
        gate.create_final_version(99999)


def test_evaluation_chain_empty(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    gate = PreSubmissionGate(db)
    chain = gate.get_evaluation_chain(m.id)
    assert chain == []


def test_evaluation_chain_with_data(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    v = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="t.txt", content_hash="abc")
    db.add(v); db.commit(); db.refresh(v)
    e = Evaluation(manuscript_version_id=v.id, journal_id=j.id, status="COMPLETED",
                   compliance_score=85, scientific_score=90, methodology_score=80,
                   writing_score=75, novelty_score=70, readiness_score=82, final_status="READY")
    db.add(e); db.commit()
    gate = PreSubmissionGate(db)
    chain = gate.get_evaluation_chain(m.id)
    assert len(chain) == 1
    assert chain[0]["scores"]["compliance"] == 85


def test_evaluation_chain_nonexistent(db):
    gate = PreSubmissionGate(db)
    assert gate.get_evaluation_chain(99999) == []


def test_api_readiness_200(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/gate/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert "readiness_score" in data
    assert data["ready_to_submit"] is True


def test_api_readiness_404():
    resp = client.get("/api/v1/manuscripts/99999/gate/readiness")
    assert resp.status_code == 404


def test_api_final_version_blocked(db):
    j = _make_journal(db)
    m = _make_pending_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/gate/final-version", json={"change_summary": "x"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready_to_submit"] is False
    assert data["version_id"] is None


def test_api_final_version_success(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/gate/final-version", json={"change_summary": "Final"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready_to_submit"] is True
    assert data["version_id"] is not None


def test_api_evaluation_chain_200(db):
    j = _make_journal(db)
    m = _make_ready_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/gate/evaluation-chain")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_evaluation_chain_404():
    resp = client.get("/api/v1/manuscripts/99999/gate/evaluation-chain")
    assert resp.status_code == 404
