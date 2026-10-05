"""Manuscript schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from app.schemas.journal import RequirementInfo


class ManuscriptBase(BaseModel):
    """Base manuscript schema."""
    title: str
    document_id: Optional[int] = None
    journal_id: Optional[int] = None


class ManuscriptCreate(ManuscriptBase):
    """Manuscript creation schema."""
    pass


class ManuscriptUpdate(BaseModel):
    """Manuscript update schema."""
    title: Optional[str] = None
    journal_id: Optional[int] = None


class RequirementCheckResult(BaseModel):
    """Individual requirement check result."""
    requirement_id: int
    key: str
    status: str
    confidence: float
    details: Optional[str] = None
    evidence: Optional[str] = None


class StyleIssue(BaseModel):
    """Style guide issue."""
    type: str
    severity: str
    message: str
    suggestion: Optional[str] = None


class RejectionRisk(BaseModel):
    """Rejection risk."""
    type: str
    severity: str
    message: str
    recommendation: Optional[str] = None


class ManuscriptInfo(BaseModel):
    """Manuscript information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    document_id: Optional[int] = None
    journal_id: Optional[int] = None
    analysis_status: str = "PENDING"
    overall_compliance_score: Optional[float] = None
    mandatory_compliance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime] = None


class ManuscriptDetail(ManuscriptInfo):
    """Detailed manuscript with analysis."""
    requirement_checks: Optional[List[RequirementCheckResult]] = None
    style_issues: Optional[List[StyleIssue]] = None
    rejection_risks: Optional[List[RejectionRisk]] = None


class ManuscriptListResponse(BaseModel):
    """List of manuscripts."""
    manuscripts: List[ManuscriptInfo]
    total: int


class ManuscriptAnalysisRequest(BaseModel):
    """Request to analyze manuscript."""
    manuscript_id: int


class ManuscriptAnalysisResponse(BaseModel):
    """Manuscript analysis response."""
    manuscript_id: int
    analysis_status: str
    overall_compliance_score: Optional[float] = None
    mandatory_compliance_score: Optional[float] = None
    style_issues: Optional[List[StyleIssue]] = None
    rejection_risks: Optional[List[RejectionRisk]] = None
    message: Optional[str] = None
