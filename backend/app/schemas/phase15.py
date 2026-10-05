"""Phase 15 schemas: Peer review response letters."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class GenerateLetterRequest(BaseModel):
    evaluation_id: Optional[int] = None
    force_regenerate: bool = False


class ResponseLetterInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    evaluation_id: Optional[int]
    title: str
    cover_letter: Optional[str]
    response_body: Optional[str]
    generated_at: Optional[datetime]
    addressed_issue_ids: List[int]
    created_at: datetime
    updated_at: datetime


class ResponseLetterListResponse(BaseModel):
    letters: List[ResponseLetterInfo]
    total: int


class ResponseLetterSummary(BaseModel):
    manuscript_id: int
    total_letters: int
    latest_letter_id: Optional[int]
    has_cover_letter: bool
    has_response_body: bool
