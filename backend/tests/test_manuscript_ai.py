"""Tests for Phase 11: AI-Powered Compliance and Evaluation."""
from __future__ import annotations

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.db.session import SessionLocal
from app.models.journal import Journal, JournalRequirement, JournalStyleProfile
from app.models.manuscript import Manuscript, ManuscriptVersion, Evaluation, EvaluationIssue
from app.models.document import Document, DocumentChunk

client = TestClient(app)


# ─── LLM Service Unit Tests ────────────────────────────────────────────────


def test_llm_service_json_extraction():
    """LLMService._extract_json handles various formats."""
    from app.services.llm_service import LLMService
    service = LLMService.__new__(LLMService)
    assert service._extract_json('{"key": "value"}') == {"key": "value"}
    with pytest.raises(ValueError):
        service._extract_json("not json at all")


def test_llm_service_parse_requirement_response():
    """LLMService parses requirement check responses correctly."""
    from app.services.llm_service import LLMService
    service = LLMService.__new__(LLMService)

    requirements = [
        {"id": 1, "key": "structure", "description": "IMRaD format", "requirement_type": "MANDATORY"},
        {"id": 2, "key": "word_count", "description": "Max 3000 words", "requirement_type": "MANDATORY"},
    ]

    response = json.dumps({
        "results": [
            {"requirement_id": 1, "key": "structure", "status": "PASS", "confidence": 0.9, "details": "Clear structure", "evidence": None},
            {"requirement_id": 2, "key": "word_count", "status": "WARNING", "confidence": 0.7, "details": "Near limit", "evidence": None},
        ]
    })

    results = service._parse_requirement_response(response, requirements)
    assert len(results) == 2
    assert results[0]["status"] == "PASS"
    assert results[1]["status"] == "WARNING"
    assert results[1]["confidence"] == 0.7


def test_llm_service_parse_risk_response():
    """LLMService parses rejection risks correctly."""
    from app.services.llm_service import LLMService
    service = LLMService.__new__(LLMService)

    response = json.dumps({
        "risks": [
            {"type": "structural", "severity": "high", "message": "Wrong format", "recommendation": "Follow template"},
        ]
    })

    risks = service._parse_risk_response(response)
    assert len(risks) == 1
    assert risks[0]["type"] == "structural"
    assert risks[0]["severity"] == "high"


def test_llm_service_fallback_on_no_provider():
    """LLMService returns UNKNOWN when no LLM provider available."""
    from app.services.llm_service import LLMService
    service = LLMService.__new__(LLMService)
    service.provider = None

    requirements = [{"id": 1, "key": "test", "description": "Test requirement"}]
    result = service.check_requirements(requirements, "some content")
    assert len(result) == 1
    assert result[0]["status"] == "UNKNOWN"


# ─── API Integration Tests ────────────────────────────────────────────────


def test_list_manuscript_versions_not_found():
    """List versions returns 404 for nonexistent manuscript."""
    response = client.get("/api/v1/manuscripts/99999/versions")
    assert response.status_code == 404


def test_get_evaluation_not_found():
    """Get evaluation returns 404 for nonexistent evaluation."""
    response = client.get("/api/v1/evaluations/99999")
    assert response.status_code == 404


def test_evaluate_manuscript_no_version():
    """Evaluate manuscript returns 404 when no version exists."""
    response = client.post(
        "/api/v1/manuscripts/99999/evaluate",
        json={"manuscript_version_id": 99999},
    )
    assert response.status_code == 404


def test_improve_manuscript_not_found():
    """Get improvements returns 404 for nonexistent manuscript."""
    response = client.post("/api/v1/manuscripts/99999/improve")
    assert response.status_code == 404


# ─── Style Profile + Compliance Integration ──────────────────────────────


def test_style_profile_integration_with_compliance():
    """Compliance engine uses style profiles from Phase 10."""
    from app.db.base import Base
    from app.models.journal import Journal, JournalRequirement, JournalStyleProfile
    import uuid

    # Ensure all tables exist including journal_style_profiles
    from app.db.session import engine as db_engine
    Base.metadata.create_all(bind=db_engine)

    db = SessionLocal()
    try:
        unique_slug = f"integration-test-{uuid.uuid4().hex[:8]}"
        existing_journal = db.query(Journal).filter(Journal.slug == unique_slug).first()
        if existing_journal:
            db.delete(existing_journal)
            db.commit()

        journal = Journal(slug=unique_slug, name="Integration Test Journal")
        db.add(journal)
        db.commit()
        db.refresh(journal)

        req = JournalRequirement(
            journal_id=journal.id,
            key="structure",
            description="IMRaD format required",
            requirement_type="MANDATORY",
        )
        db.add(req)
        db.commit()

        profile = JournalStyleProfile(
            journal_id=journal.id,
            profile_json=json.dumps({"structure": "IMRaD", "tone": "formal"}),
            analyzed_at=datetime.utcnow(),
            analyzed_by="test",
            paper_count=1,
        )
        db.add(profile)
        db.commit()

        stored_profile = db.query(JournalStyleProfile).filter(
            JournalStyleProfile.journal_id == journal.id
        ).first()
        assert stored_profile is not None
        assert stored_profile.paper_count == 1

        stored_req = db.query(JournalRequirement).filter(
            JournalRequirement.key == "structure"
        ).first()
        assert stored_req is not None
        assert stored_req.key == "structure"
    finally:
        # Clean up
        db.query(Journal).filter(Journal.slug.like("integration-test-%")).delete()
        db.commit()
        db.close()


def test_evaluation_engine_parse_scores_valid():
    """EvaluationEngine parses valid score JSON."""
    from app.manuscript_engine.evaluator import EvaluationEngine
    from unittest.mock import MagicMock

    db_mock = MagicMock()
    engine = EvaluationEngine(db_mock)

    response = json.dumps({
        "compliance": 85,
        "scientific": 90,
        "methodology": 80,
        "writing": 75,
        "novelty": 70,
        "readiness": 82,
        "issues": [{"severity": "minor", "category": "writing", "message": "Minor grammar issue"}]
    })

    scores = engine._parse_scores(response)
    assert scores["compliance"] == 85
    assert scores["scientific"] == 90
    assert scores["readiness"] == 82
    assert len(scores["issues"]) == 1
    assert scores["issues"][0]["severity"] == "minor"


def test_evaluation_engine_parse_scores_invalid():
    """EvaluationEngine falls back on invalid JSON."""
    from app.manuscript_engine.evaluator import EvaluationEngine
    from unittest.mock import MagicMock

    db_mock = MagicMock()
    engine = EvaluationEngine(db_mock)

    scores = engine._parse_scores("not valid json at all")
    assert scores["compliance"] == 50
    assert scores["scientific"] == 45  # fallback: 90 * 0.5


def test_evaluation_engine_get_content_no_document():
    """EvaluationEngine returns None when manuscript has no document."""
    from app.manuscript_engine.evaluator import EvaluationEngine
    from unittest.mock import MagicMock

    db_mock = MagicMock()
    engine = EvaluationEngine(db_mock)

    manuscript = MagicMock()
    manuscript.document_id = None

    content = engine._get_content(manuscript)
    assert content is None

