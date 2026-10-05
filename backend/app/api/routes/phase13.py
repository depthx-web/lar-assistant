"""Phase 13 routes: tags, comments, diff, export, submission workflow."""
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.manuscript_engine.export_engine import ExportEngine
from app.manuscript_engine.tagging_collab import TaggingAndCollaborationEngine
from app.manuscript_engine.submission_workflow import SubmissionWorkflow
from app.models.manuscript import Manuscript, ExportJob
from app.schemas.phase13 import (
    CommentStats, DiffSummary, DiffHunkItem, ExportJobCreate,
    ExportJobInfo, ExportJobListResponse, ManuscriptCommentCreate,
    ManuscriptCommentInfo, ManuscriptCommentListResponse,
    SubmissionCreate, SubmissionStatus, VersionDiffResponse,
    VersionTagCreate, VersionTagInfo, VersionTagListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/manuscripts/{manuscript_id}/tags", response_model=VersionTagListResponse)
def list_version_tags(manuscript_id: int, db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = TaggingAndCollaborationEngine(db)
    tags = engine.list_tags(manuscript_id)
    return VersionTagListResponse(tags=[VersionTagInfo.model_validate(t) for t in tags], total=len(tags))


@router.post("/manuscripts/{manuscript_id}/tags", response_model=VersionTagInfo)
def create_version_tag(manuscript_id: int, data: VersionTagCreate, db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = TaggingAndCollaborationEngine(db)
    tag = engine.add_tag(manuscript_id=manuscript_id, tag_name=data.tag_name,
                         version_id=data.version_id, label=data.label, is_baseline=data.is_baseline)
    return VersionTagInfo.model_validate(tag)


@router.delete("/manuscripts/{manuscript_id}/tags/{tag_id}")
def delete_version_tag(manuscript_id: int, tag_id: int, db: Annotated[Session, Depends(get_db)] = None):
    engine = TaggingAndCollaborationEngine(db)
    if not engine.delete_tag(tag_id, manuscript_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"status": "deleted", "tag_id": tag_id}


@router.get("/manuscripts/{manuscript_id}/comments", response_model=ManuscriptCommentListResponse)
def list_comments(manuscript_id: int, version_id: Optional[int] = Query(None),
                  unresolved_only: bool = Query(False), db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = TaggingAndCollaborationEngine(db)
    comments = engine.list_comments(manuscript_id, version_id=version_id, unresolved_only=unresolved_only)
    total = len(comments)
    unresolved = sum(1 for c in comments if not c.is_resolved)
    return ManuscriptCommentListResponse(comments=[ManuscriptCommentInfo.model_validate(c) for c in comments],
                                         total=total, unresolved_count=unresolved)


@router.post("/manuscripts/{manuscript_id}/comments", response_model=ManuscriptCommentInfo)
def create_comment(manuscript_id: int, data: ManuscriptCommentCreate, db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = TaggingAndCollaborationEngine(db)
    comment = engine.add_comment(manuscript_id=manuscript_id, author=data.author, content=data.content,
                                 version_id=data.version_id, line_number=data.line_number)
    return ManuscriptCommentInfo.model_validate(comment)


@router.post("/manuscripts/{manuscript_id}/comments/{comment_id}/resolve")
def resolve_comment(manuscript_id: int, comment_id: int, db: Annotated[Session, Depends(get_db)] = None):
    engine = TaggingAndCollaborationEngine(db)
    if not engine.resolve_comment(comment_id, manuscript_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "resolved", "comment_id": comment_id}


@router.get("/manuscripts/{manuscript_id}/comments/stats", response_model=CommentStats)
def get_comment_stats(manuscript_id: int, db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = TaggingAndCollaborationEngine(db)
    stats = engine.get_comment_stats(manuscript_id)
    return CommentStats(**stats)


@router.get("/manuscripts/{manuscript_id}/diff", response_model=VersionDiffResponse)
def get_version_diff(manuscript_id: int, from_version: int = Query(..., ge=1),
                     to_version: int = Query(..., ge=1), db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    workflow = SubmissionWorkflow(db)
    result = workflow.run_diff(manuscript_id, from_version, to_version)
    return VersionDiffResponse(
        from_version=result["from_version"], to_version=result["to_version"],
        from_hash=result["from_hash"], to_hash=result["to_hash"],
        line_count_old=result["line_count_old"], line_count_new=result["line_count_new"],
        additions=result["additions"], deletions=result["deletions"],
        hunks_count=result["hunks_count"],
        summary=DiffSummary(additions=result["summary"]["line_changes"]["additions"],
                            deletions=result["summary"]["line_changes"]["deletions"],
                            total_old_lines=result["summary"]["total_old_lines"],
                            total_new_lines=result["summary"]["total_new_lines"],
                            net_change=result["summary"]["net_change"],
                            hunks_count=result["summary"]["hunks_count"]),
        hunks=[DiffHunkItem(op=h["op"], old_start=h["old_start"], new_start=h["new_start"],
                            old_lines=h["old_lines"], new_lines=h.get("new_lines", []))
               for h in result["hunks"]],
    )


@router.post("/manuscripts/{manuscript_id}/export", response_model=ExportJobInfo)
def create_export(manuscript_id: int, data: ExportJobCreate, db: Annotated[Session, Depends(get_db)] = None):
    if data.format not in ExportEngine.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400,
                            detail=f"Unsupported format: {data.format}. Supported: {ExportEngine.SUPPORTED_FORMATS}")
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ExportEngine(db)
    job = engine.create_export_job(manuscript_id, fmt=data.format, version_id=data.version_id)
    return ExportJobInfo.model_validate(job)


@router.post("/manuscripts/{manuscript_id}/export/{job_id}/run", response_model=ExportJobInfo)
def run_export(manuscript_id: int, job_id: int, db: Annotated[Session, Depends(get_db)] = None):
    engine = ExportEngine(db)
    job = db.query(ExportJob).filter(ExportJob.id == job_id, ExportJob.manuscript_id == manuscript_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    engine.run_export(job)
    return ExportJobInfo.model_validate(job)


@router.get("/manuscripts/{manuscript_id}/exports", response_model=ExportJobListResponse)
def list_exports(manuscript_id: int, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
                 db: Annotated[Session, Depends(get_db)] = None):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    q = db.query(ExportJob).filter(ExportJob.manuscript_id == manuscript_id)
    total = q.count()
    jobs = q.offset(skip).limit(limit).all()
    return ExportJobListResponse(jobs=[ExportJobInfo.model_validate(j) for j in jobs], total=total)


@router.get("/manuscripts/{manuscript_id}/submission/status", response_model=SubmissionStatus)
def get_submission_status(manuscript_id: int, db: Annotated[Session, Depends(get_db)] = None):
    workflow = SubmissionWorkflow(db)
    return SubmissionStatus(**workflow.get_submission_status(manuscript_id))


@router.post("/manuscripts/{manuscript_id}/submission", response_model=SubmissionStatus)
def submit_manuscript(manuscript_id: int, data: SubmissionCreate, db: Annotated[Session, Depends(get_db)] = None):
    workflow = SubmissionWorkflow(db)
    result = workflow.submit_manuscript(manuscript_id=manuscript_id, change_summary=data.change_summary,
                                        label=data.label)
    if "ready_to_submit" in result:
        return SubmissionStatus(**workflow.get_submission_status(manuscript_id))
    return SubmissionStatus(**result)