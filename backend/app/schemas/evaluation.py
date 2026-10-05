"""Schemas for evaluations and pre-submission gate."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class BlockingIssue(BaseModel):
    """A single blocking or warning issue."""
    rule: str
    severity: str  # "critical" | "warning"
    message: str
    requirement_key: Optional[str] = None


class ReadinessComponent(BaseModel):
    """Score component for readiness calculation."""
    factor: str
    score: float


class PreSubmissionCheckResponse(BaseModel):
    """Response from pre-submission check."""
    manuscript_id: int
    title: str
    journal_id: Optional[int]
    readiness_score: float
    ready_to_submit: bool
    blocking_issues: List[BlockingIssue] = []
    warnings: List[BlockingIssue] = []
    critical_issues: List[BlockingIssue] = []
    components: List[ReadinessComponent] = []


class FinalVersionCreate(BaseModel):
    """Request to create final version."""
    change_summary: str = ""


class FinalVersionResponse(BaseModel):
    """Response after attempting to create final version."""
    manuscript_id: int
    version_id: Optional[int] = None
    ready_to_submit: bool
    blocking_issues: List[BlockingIssue] = []
    message: str = ""


class EvaluationScore(BaseModel):
    """Individual evaluation score."""
    model_config = ConfigDict(from_attributes=True)

    manuscript_version_id: int
    journal_id: Optional[int]
    status: str = "PENDING"
    compliance_score: Optional[int]
    scientific_score: Optional[int]
    methodology_score: Optional[int]
    writing_score: Optional[int]
    novelty_score: Optional[int]
    readiness_score: Optional[int]
    final_status: Optional[str]


class EvaluationIssueItem(BaseModel):
    """Evaluation issue."""
    id: int
    evaluation_id: int
    severity: str
    category: str
    message: str
    evidence: Optional[str]
    is_blocking: bool
    requirement_key: Optional[str]


class ManuscriptVersionInfo(BaseModel):
    """Manuscript version info."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    version: int
    content_path: str
    content_hash: str
    change_summary: Optional[str]
    provenance: Optional[str]
    created_at: datetime


class EvaluationInfo(BaseModel):
    """Evaluation info with scores."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_version_id: int
    journal_id: Optional[int]
    status: str
    scores: Optional[Dict[str, Any]]
    final_status: Optional[str]
    model: Optional[str]
    prompt_version: Optional[str]
    created_at: datetime


class EvaluationCreate(BaseModel):
    """Create evaluation request."""
    manuscript_version_id: int
    journal_id: Optional[int] = None
    model: Optional[str] = None


class ManuscriptVersionListResponse(BaseModel):
    """List of manuscript versions."""
    versions: List[ManuscriptVersionInfo]
    total: int


class EvaluationListResponse(BaseModel):
    """List of evaluations."""
    evaluations: List[EvaluationInfo]
    total: int


class EvaluationDetail(EvaluationInfo):
    """Detailed evaluation with issues."""
    issues: List[EvaluationIssueItem] = []
    report: Optional[Dict[str, Any]] = None


class ManuscriptImprovementResponse(BaseModel):
    """Manuscript improvement suggestions."""
    manuscript_id: int
    overall_score: float
    improvements: List[Dict[str, Any]]
