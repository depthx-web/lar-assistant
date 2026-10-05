"""Manuscripts, versions, evaluations and the review/revision workflow."""
from __future__ import annotations

import enum
import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import iso, utcnow


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RequirementStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Manuscript(Base):
    __tablename__ = "manuscripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    document_id: Mapped[Optional[int]] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    journal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("journals.id", ondelete="SET NULL"), nullable=True)
    analysis_status: Mapped[str] = mapped_column(String(32), nullable=False, default=AnalysisStatus.PENDING.value)
    overall_compliance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mandatory_compliance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    requirement_checks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    style_issues: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    rejection_risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    versions: Mapped[List["ManuscriptVersion"]] = relationship(
        back_populates="manuscript", cascade="all, delete-orphan", order_by="ManuscriptVersion.version"
    )


class ManuscriptVersion(Base):
    __tablename__ = "manuscript_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_path: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provenance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON dict
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    manuscript: Mapped[Manuscript] = relationship(back_populates="versions")
    evaluations: Mapped[List["Evaluation"]] = relationship(
        back_populates="manuscript_version", cascade="all, delete-orphan"
    )


class RequirementCheck(Base):
    __tablename__ = "requirement_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("journal_requirements.id", ondelete="SET NULL"), nullable=True
    )
    key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=RequirementStatus.UNKNOWN.value)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_version_id: Mapped[int] = mapped_column(
        ForeignKey("manuscript_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    journal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("journals.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    compliance_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scientific_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    methodology_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    writing_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    novelty_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    readiness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    final_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON dict
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    manuscript_version: Mapped[ManuscriptVersion] = relationship(back_populates="evaluations")
    issues: Mapped[List["EvaluationIssue"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )


class EvaluationIssue(Base):
    __tablename__ = "evaluation_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluation_id: Mapped[int] = mapped_column(ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="minor")
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_blocking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requirement_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    evaluation: Mapped[Evaluation] = relationship(back_populates="issues")

    def to_dict(self) -> dict:
        return {
            "id": self.id, "evaluation_id": self.evaluation_id, "severity": self.severity,
            "category": self.category, "message": self.message, "evidence": self.evidence,
            "is_blocking": bool(self.is_blocking), "requirement_key": self.requirement_key,
        }


class VersionTag(Base):
    __tablename__ = "version_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("manuscript_versions.id", ondelete="SET NULL"), nullable=True
    )
    tag_name: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_baseline: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class ManuscriptComment(Base):
    __tablename__ = "manuscript_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("manuscript_versions.id", ondelete="SET NULL"), nullable=True
    )
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("manuscript_versions.id", ondelete="SET NULL"), nullable=True
    )
    format: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    output_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ImprovementSuggestion(Base):
    __tablename__ = "improvement_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True)
    source_issue_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("evaluation_issues.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="minor")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    suggested_fix: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_addressed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    addressed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    addressed_version_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "manuscript_id": self.manuscript_id, "evaluation_id": self.evaluation_id,
            "source_issue_id": self.source_issue_id, "category": self.category,
            "severity": self.severity, "title": self.title, "description": self.description,
            "suggested_fix": self.suggested_fix, "evidence": self.evidence,
            "priority": self.priority, "is_addressed": bool(self.is_addressed),
            "addressed_at": self.addressed_at, "addressed_version_id": self.addressed_version_id,
            "created_at": self.created_at,
        }


class ImprovementTrack(Base):
    __tablename__ = "improvement_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suggestion_id: Mapped[int] = mapped_column(
        ForeignKey("improvement_suggestions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    action_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "suggestion_id": self.suggestion_id, "manuscript_id": self.manuscript_id,
            "version_id": self.version_id, "action": self.action, "action_detail": self.action_detail,
            "reviewer": self.reviewer, "created_at": self.created_at,
        }


class PeerReviewResponseLetter(Base):
    __tablename__ = "peer_review_response_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[int] = mapped_column(ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="Response to Reviewers")
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    addressed_issue_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="[]")  # JSON list[int]
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    def to_dict(self) -> dict:
        try:
            addressed = json.loads(self.addressed_issue_ids) if self.addressed_issue_ids else []
        except (TypeError, ValueError):
            addressed = []
        return {
            "id": self.id, "manuscript_id": self.manuscript_id, "evaluation_id": self.evaluation_id,
            "title": self.title, "cover_letter": self.cover_letter, "response_body": self.response_body,
            "generated_at": iso(self.generated_at), "addressed_issue_ids": addressed,
            "created_at": iso(self.created_at), "updated_at": iso(self.updated_at),
        }