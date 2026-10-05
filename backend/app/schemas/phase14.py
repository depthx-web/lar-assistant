"""Phase 14 schemas: AI-powered revision & improvement suggestions."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ImprovementSuggestionCreate(BaseModel):
    """Request for generating suggestions."""
    evaluation_id: Optional[int] = None
    force_regenerate: bool = False


class ImprovementSuggestionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    evaluation_id: Optional[int]
    source_issue_id: Optional[int]
    category: str
    severity: str
    title: str
    description: str
    suggested_fix: Optional[str]
    evidence: Optional[str]
    priority: int
    is_addressed: bool
    addressed_at: Optional[datetime]
    addressed_version_id: Optional[int]
    created_at: datetime


class ImprovementSuggestionListResponse(BaseModel):
    suggestions: List[ImprovementSuggestionInfo]
    total: int


class AddressSuggestionRequest(BaseModel):
    version_id: Optional[int] = None
    reviewer: Optional[str] = None


class ImprovementTrackInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suggestion_id: int
    manuscript_id: int
    version_id: int
    action: str
    action_detail: Optional[str]
    reviewer: Optional[str]
    created_at: datetime


class ImprovementSummary(BaseModel):
    manuscript_id: int
    total_suggestions: int
    addressed: int
    unaddressed: int
    addressed_ratio: float
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
