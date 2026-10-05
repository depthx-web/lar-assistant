"""Tests for Phase 13: Multi-version comparison, diff, tagging, export, submission."""
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
from app.models.manuscript import (
    Manuscript, ManuscriptVersion, VersionTag,
    ManuscriptComment, ExportJob,
)
from app.manuscript_engine.version_diff import VersionDiffEngine
from app.manuscript_engine.tagging_collab import TaggingAndCollaborationEngine
from app.manuscript_engine.export_engine import ExportEngine
from app.manuscript_engine.submission_workflow import SubmissionWorkflow

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
    j = Journal(slug="p13-j-" + uuid.uuid4().hex[:8], name="P13 Test")
    db.add(j); db.commit(); db.refresh(j)
    r = JournalRequirement(journal_id=j.id, key="structure", description="IMRaD", requirement_type="MANDATORY")
    db.add(r); db.commit()
    return j


def _make_manuscript(db, journal):
    m = Manuscript(title="P13 Manuscript", journal_id=journal.id, analysis_status="COMPLETED",
                   overall_compliance_score=85.0, mandatory_compliance_score=100.0)
    db.add(m); db.commit(); db.refresh(m)
    return m


def _make_versions(db, manuscript):
    v1 = ManuscriptVersion(manuscript_id=manuscript.id, version=1, content_path="v1.txt", content_hash="abc")
    v2 = ManuscriptVersion(manuscript_id=manuscript.id, version=2, content_path="v2.txt", content_hash="def")
    db.add(v1); db.add(v2); db.commit(); db.refresh(v1); db.refresh(v2)
    return v1, v2


# ─── Version Tags ────────────────────────────────────────────────────────────


def test_add_tag(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    tag = engine.add_tag(manuscript_id=m.id, tag_name="v1-final", is_baseline=True)
    assert tag.tag_name == "v1-final"
    assert tag.is_baseline is True


def test_list_tags_empty(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    tags = engine.list_tags(m.id)
    assert tags == []


def test_list_tags_with_data(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    engine.add_tag(manuscript_id=m.id, tag_name="draft", is_baseline=False)
    engine.add_tag(manuscript_id=m.id, tag_name="final", is_baseline=True)
    tags = engine.list_tags(m.id)
    assert len(tags) == 2


def test_delete_tag(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    tag = engine.add_tag(manuscript_id=m.id, tag_name="draft", is_baseline=False)
    ok = engine.delete_tag(tag.id, m.id)
    assert ok is True
    tags = engine.list_tags(m.id)
    assert len(tags) == 0


def test_delete_tag_not_found(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    ok = engine.delete_tag(99999, m.id)
    assert ok is False


def test_baseline_flag_cleared(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    engine.add_tag(manuscript_id=m.id, tag_name="old-baseline", is_baseline=True)
    tag = engine.add_tag(manuscript_id=m.id, tag_name="new-baseline", is_baseline=True)
    assert tag.is_baseline is True
    existing = engine.list_tags(m.id)
    assert sum(1 for t in existing if t.is_baseline) == 1


def test_add_tag_manuscript_not_found(db):
    engine = TaggingAndCollaborationEngine(db)
    with pytest.raises(ValueError, match="not found"):
        engine.add_tag(manuscript_id=99999, tag_name="test")


# ─── Comments ────────────────────────────────────────────────────────────────


def test_add_comment(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1, _ = _make_versions(db, m)
    engine = TaggingAndCollaborationEngine(db)
    comment = engine.add_comment(manuscript_id=m.id, author="alice", content="Fix abstract", version_id=v1.id)
    assert comment.author == "alice"
    assert comment.is_resolved is False


def test_list_comments(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1, _ = _make_versions(db, m)
    engine = TaggingAndCollaborationEngine(db)
    engine.add_comment(manuscript_id=m.id, author="alice", content="Comment 1", version_id=v1.id)
    engine.add_comment(manuscript_id=m.id, author="bob", content="Comment 2", version_id=v1.id)
    comments = engine.list_comments(m.id)
    assert len(comments) == 2


def test_list_comments_unresolved_only(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    c1 = engine.add_comment(manuscript_id=m.id, author="alice", content="A")
    c2 = engine.add_comment(manuscript_id=m.id, author="bob", content="B")
    engine.resolve_comment(c1.id, m.id)
    unresolved = engine.list_comments(m.id, unresolved_only=True)
    assert len(unresolved) == 1
    assert unresolved[0].id == c2.id


def test_resolve_comment(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    c = engine.add_comment(manuscript_id=m.id, author="alice", content="Fix this")
    ok = engine.resolve_comment(c.id, m.id)
    assert ok is True
    assert c.is_resolved is True


def test_resolve_comment_not_found(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    ok = engine.resolve_comment(99999, m.id)
    assert ok is False


def test_comment_stats(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = TaggingAndCollaborationEngine(db)
    c1 = engine.add_comment(manuscript_id=m.id, author="a", content="1")
    c2 = engine.add_comment(manuscript_id=m.id, author="b", content="2")
    stats = engine.get_comment_stats(m.id)
    assert stats["total"] == 2
    assert stats["unresolved"] == 2
    engine.resolve_comment(c1.id, m.id)
    stats = engine.get_comment_stats(m.id)
    assert stats["unresolved"] == 1


def test_list_comments_manuscript_not_found(db):
    engine = TaggingAndCollaborationEngine(db)
    comments = engine.list_comments(manuscript_id=99999)
    assert comments == []


# ─── Diff ────────────────────────────────────────────────────────────────────


def test_diff_versions_empty_content(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="v1.txt", content_hash="abc")
    v2 = ManuscriptVersion(manuscript_id=m.id, version=2, content_path="v2.txt", content_hash="def")
    db.add(v1); db.add(v2); db.commit(); db.refresh(v1); db.refresh(v2)
    engine = VersionDiffEngine(db)
    diff = engine.diff_versions(m.id, 1, 2)
    assert diff.from_version == 1
    assert diff.to_version == 2
    # Both versions have no actual file content, so diffs come from placeholder text
    assert diff.line_count_old >= 0
    assert diff.line_count_new >= 0


def test_diff_versions_different_content(db, tmp_path):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    # Create actual content files
    f1 = tmp_path / "v1.txt"
    f2 = tmp_path / "v2.txt"
    f1.write_text("line one\nline two\nline three\n")
    f2.write_text("line one\nmodified line\nline two\nline three\nline four\n")
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path=str(f1), content_hash="abc")
    v2 = ManuscriptVersion(manuscript_id=m.id, version=2, content_path=str(f2), content_hash="def")
    db.add(v1); db.add(v2); db.commit(); db.refresh(v1); db.refresh(v2)
    engine = VersionDiffEngine(db)
    diff = engine.diff_versions(m.id, 1, 2)
    assert diff.additions > 0 or diff.deletions > 0


def test_diff_versions_same_content(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    content = "same content here\n"
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="s1.txt", content_hash="a")
    v2 = ManuscriptVersion(manuscript_id=m.id, version=2, content_path="s2.txt", content_hash="b")
    db.add(v1); db.add(v2); db.commit(); db.refresh(v1); db.refresh(v2)
    engine = VersionDiffEngine(db)
    # Both have placeholder text so no actual file diff
    diff = engine.diff_versions(m.id, 1, 2)
    assert diff.from_version == 1
    assert diff.to_version == 2


def test_diff_versions_missing(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = VersionDiffEngine(db)
    with pytest.raises(ValueError, match="not found"):
        engine.diff_versions(m.id, 1, 99)


def test_diff_to_dict(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="t1.txt", content_hash="abc")
    v2 = ManuscriptVersion(manuscript_id=m.id, version=2, content_path="t2.txt", content_hash="def")
    db.add(v1); db.add(v2); db.commit()
    engine = VersionDiffEngine(db)
    diff = engine.diff_versions(m.id, 1, 2)
    d = engine.diff_to_dict(diff)
    assert "from_version" in d
    assert "hunks" in d
    assert "summary" in d


# ─── Export ──────────────────────────────────────────────────────────────────


def test_export_create_job(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = ExportEngine(db)
    job = engine.create_export_job(m.id, fmt="markdown")
    assert job.manuscript_id == m.id
    assert job.format == "markdown"
    assert job.status == "PENDING"


def test_export_create_job_bad_format(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = ExportEngine(db)
    with pytest.raises(ValueError, match="Unsupported"):
        engine.create_export_job(m.id, fmt="pdf")


def test_export_create_job_missing_manuscript(db):
    engine = ExportEngine(db)
    with pytest.raises(ValueError, match="not found"):
        engine.create_export_job(99999, fmt="markdown")


def test_export_run_markdown(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="none.txt", content_hash="abc")
    db.add(v1); db.commit(); db.refresh(v1)
    engine = ExportEngine(db)
    job = engine.create_export_job(m.id, fmt="markdown", version_id=v1.id)
    result = engine.run_export(job)
    assert result["status"] == "COMPLETED"
    assert result["output_path"] is not None


def test_export_run_text(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="none.txt", content_hash="abc")
    db.add(v1); db.commit(); db.refresh(v1)
    engine = ExportEngine(db)
    job = engine.create_export_job(m.id, fmt="text", version_id=v1.id)
    result = engine.run_export(job)
    assert result["status"] == "COMPLETED"


def test_export_run_latex(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    v1 = ManuscriptVersion(manuscript_id=m.id, version=1, content_path="none.txt", content_hash="abc")
    db.add(v1); db.commit(); db.refresh(v1)
    engine = ExportEngine(db)
    job = engine.create_export_job(m.id, fmt="latex", version_id=v1.id)
    result = engine.run_export(job)
    assert result["status"] == "COMPLETED"


def test_list_exports(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    engine = ExportEngine(db)
    engine.create_export_job(m.id, fmt="markdown")
    engine.create_export_job(m.id, fmt="text")
    q = db.query(ExportJob).filter(ExportJob.manuscript_id == m.id)
    assert q.count() == 2


# ─── Submission Workflow ─────────────────────────────────────────────────────


def test_submission_status_ready(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    workflow = SubmissionWorkflow(db)
    status = workflow.get_submission_status(m.id)
    assert status["manuscript_id"] == m.id
    assert status["gate_ready"] is True
    assert status["is_submitted"] is False


def test_submission_status_pending(db):
    m = Manuscript(title="Pending", journal_id=None, analysis_status="PENDING",
                   overall_compliance_score=50.0, mandatory_compliance_score=60.0)
    db.add(m); db.commit(); db.refresh(m)
    workflow = SubmissionWorkflow(db)
    status = workflow.get_submission_status(m.id)
    assert status["manuscript_id"] == m.id
    assert status["gate_ready"] is False


def test_submission_status_not_found(db):
    workflow = SubmissionWorkflow(db)
    with pytest.raises(ValueError, match="not found"):
        workflow.get_submission_status(99999)


def test_submit_manuscript_ready(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    workflow = SubmissionWorkflow(db)
    result = workflow.submit_manuscript(manuscript_id=m.id, change_summary="First submit")
    assert result["ready_to_submit"] is True


def test_submit_manuscript_blocked(db):
    m = Manuscript(title="Blocked", journal_id=None, analysis_status="PENDING",
                   overall_compliance_score=30.0, mandatory_compliance_score=50.0)
    db.add(m); db.commit(); db.refresh(m)
    workflow = SubmissionWorkflow(db)
    result = workflow.submit_manuscript(manuscript_id=m.id)
    assert result["ready_to_submit"] is False


# ─── API Tests ───────────────────────────────────────────────────────────────


def test_api_list_tags_200(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/tags")
    assert resp.status_code == 200
    data = resp.json()
    assert "tags" in data
    assert data["total"] == 0


def test_api_list_tags_404():
    resp = client.get("/api/v1/manuscripts/99999/tags")
    assert resp.status_code == 404


def test_api_create_tag(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/tags", json={"tag_name": "v1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tag_name"] == "v1"


def test_api_delete_tag(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    create = client.post(f"/api/v1/manuscripts/{m.id}/tags", json={"tag_name": "v1"})
    tag_id = create.json()["id"]
    resp = client.delete(f"/api/v1/manuscripts/{m.id}/tags/{tag_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


def test_api_create_comment(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "alice", "content": "Fix abstract"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["author"] == "alice"


def test_api_list_comments(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "alice", "content": "Comment 1"})
    client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "bob", "content": "Comment 2"})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/comments")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_api_resolve_comment(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    create = client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "alice", "content": "Fix"})
    comment_id = create.json()["id"]
    resp = client.post(f"/api/v1/manuscripts/{m.id}/comments/{comment_id}/resolve")
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"


def test_api_comment_stats(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "a", "content": "1"})
    client.post(f"/api/v1/manuscripts/{m.id}/comments", json={"author": "b", "content": "2"})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/comments/stats")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2
    assert resp.json()["unresolved"] == 2


def test_api_diff_404():
    resp = client.get("/api/v1/manuscripts/99999/diff?from_version=1&to_version=2")
    assert resp.status_code == 404


def test_api_create_export(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/export", json={"format": "markdown"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["format"] == "markdown"
    assert data["status"] == "PENDING"


def test_api_create_export_bad_format(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/export", json={"format": "pdf"})
    assert resp.status_code == 400


def test_api_list_exports(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    client.post(f"/api/v1/manuscripts/{m.id}/export", json={"format": "markdown"})
    resp = client.get(f"/api/v1/manuscripts/{m.id}/exports")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_api_submission_status(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.get(f"/api/v1/manuscripts/{m.id}/submission/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manuscript_id"] == m.id
    assert data["gate_ready"] is True


def test_api_submit_manuscript(db):
    j = _make_journal(db)
    m = _make_manuscript(db, j)
    resp = client.post(f"/api/v1/manuscripts/{m.id}/submission", json={"change_summary": "First"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["manuscript_id"] == m.id