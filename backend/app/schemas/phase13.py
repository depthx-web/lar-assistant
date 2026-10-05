"""Version tagging, collaboration, export, and submission workflow schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ─── Version Tagging ──────────────────────────────────────────────────────────

class VersionTagCreate(BaseModel):
    tag_name: str
    label: Optional[str] = None
    version_id: Optional[int] = None
    is_baseline: bool = False


class VersionTagInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    version_id: Optional[int]
    tag_name: str
    label: Optional[str]
    is_baseline: bool
    created_at: datetime


class VersionTagListResponse(BaseModel):
    tags: List[VersionTagInfo]
    total: int


# ─── Collaboration Comments ───────────────────────────────────────────────────

class ManuscriptCommentCreate(BaseModel):
    author: str
    content: str
    version_id: Optional[int] = None
    line_number: Optional[int] = None


class ManuscriptCommentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    version_id: Optional[int]
    author: str
    content: str
    line_number: Optional[int]
    is_resolved: bool
    created_at: datetime


class ManuscriptCommentListResponse(BaseModel):
    comments: List[ManuscriptCommentInfo]
    total: int
    unresolved_count: int


# ─── Diff / Version Comparison ────────────────────────────────────────────────

class DiffHunkItem(BaseModel):
    op: str
    old_start: int
    new_start: int
    old_lines: List[str]
    new_lines: List[str]


class DiffSummary(BaseModel):
    additions: int
    deletions: int
    total_old_lines: int
    total_new_lines: int
    net_change: int
    hunks_count: int


class VersionDiffResponse(BaseModel):
    from_version: int
    to_version: int
    from_hash: str
    to_hash: str
    line_count_old: int
    line_count_new: int
    additions: int
    deletions: int
    hunks_count: int
    summary: DiffSummary
    hunks: List[DiffHunkItem]


# ─── Export ───────────────────────────────────────────────────────────────────

class ExportJobCreate(BaseModel):
    format: str
    version_id: Optional[int] = None


class ExportJobInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manuscript_id: int
    version_id: Optional[int]
    format: str
    status: str
    output_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class ExportJobListResponse(BaseModel):
    jobs: List[ExportJobInfo]
    total: int


# ─── Submission Workflow ─────────────────────────────────────────────────────

class SubmissionStatus(BaseModel):
    manuscript_id: int
    title: str
    journal_id: Optional[int]
    is_submitted: bool
    submission_version_id: Optional[int] = None
    submitted_at: Optional[datetime] = None
    gate_ready: bool
    gate_score: Optional[float] = None
    blocking_issues_count: int


class SubmissionCreate(BaseModel):
    change_summary: str = ""
    label: Optional[str] = None


class CommentStats(BaseModel):
    total: int
    unresolved: int