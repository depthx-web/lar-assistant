"""Journal schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RequirementInfo(BaseModel):
    """Journal requirement information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    key: str
    description: str
    requirement_type: str
    evidence_level: str
    value: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    confidence: Optional[str] = None
    retrieved_at: Optional[datetime] = None


class JournalInfo(BaseModel):
    """Journal profile information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    slug: str
    publisher: Optional[str] = None
    issn: Optional[str] = None
    official_url: Optional[str] = None
    author_guidelines_url: Optional[str] = None
    scope: Optional[str] = None
    reference_style: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JournalDetail(JournalInfo):
    """Detailed journal profile with requirements."""
    article_types: Optional[str] = None
    word_limits: Optional[str] = None
    style_guide: Optional[str] = None
    rejection_patterns: Optional[str] = None
    requirements: List[RequirementInfo] = []


class JournalListResponse(BaseModel):
    """List of journals."""
    journals: List[JournalInfo]
    total: int


class JournalLoadResponse(BaseModel):
    """Journal loader response."""
    loaded_count: int
    message: str


class RequirementChangeSchema(BaseModel):
    """A single requirement change during update."""
    key: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_type: str  # "added", "removed", "changed"


class JournalUpdateCheckResponse(BaseModel):
    """Response from checking for journal updates."""
    journal_slug: str
    has_changes: bool
    needs_confirmation: bool
    added_count: int
    removed_count: int
    changed_count: int
    source_url: str
    added: List[RequirementChangeSchema] = []
    removed: List[RequirementChangeSchema] = []
    changed: List[RequirementChangeSchema] = []


class JournalUpdateApplyResponse(BaseModel):
    """Response from applying journal update."""
    journal_slug: str
    message: str
    source_url: str
    verified_at: datetime


class StyleProfileSchema(BaseModel):
    """Structured style profile for a journal."""
    structure: str = ""
    section_order: List[str] = []
    paragraph_length_avg: Optional[float] = None
    paragraph_style: str = ""
    sentence_length_avg: Optional[float] = None
    active_voice_ratio: Optional[float] = None
    passive_voice_ratio: Optional[float] = None
    voice_preference: str = ""
    tone: str = ""
    terminology_level: str = ""
    jargon_density: Optional[float] = None
    citation_style: str = ""
    avg_citations_per_section: Optional[float] = None
    methods_detail_level: str = ""
    results_style: str = ""
    discussion_approach: str = ""


class StyleAnalysisHistoryItem(BaseModel):
    """Single entry in style analysis history."""
    id: int
    analyzed_at: str
    analyzed_by: Optional[str] = None
    paper_count: int
    profile: dict


class StyleAnalysisHistoryResponse(BaseModel):
    """Response containing analysis history."""
    journal_slug: str
    total_analyses: int
    history: List[StyleAnalysisHistoryItem]


class StyleBatchResult(BaseModel):
    """Result for a single journal in a batch analysis."""
    journal_slug: str
    structure: str = ""
    tone: str = ""
    voice_preference: str = ""
    analyzed: bool = False
    error: Optional[str] = None


class StyleBatchResponse(BaseModel):
    """Response for batch style analysis."""
    analyzed_count: int
    failed_count: int
    results: List[StyleBatchResult]

