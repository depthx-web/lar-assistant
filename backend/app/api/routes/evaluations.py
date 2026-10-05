"""Evaluation routes for Phase 11 & 12."""
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.manuscript_engine.evaluator import EvaluationEngine
from app.manuscript_engine.gate import PreSubmissionGate
from app.models.manuscript import Manuscript, ManuscriptVersion
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationDetail,
    EvaluationInfo,
    EvaluationListResponse,
    FinalVersionCreate,
    FinalVersionResponse,
    ManuscriptImprovementResponse,
    ManuscriptVersionInfo,
    ManuscriptVersionListResponse,
    PreSubmissionCheckResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/manuscripts/{manuscript_id}/versions", response_model=ManuscriptVersionListResponse)
def list_manuscript_versions(
    manuscript_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Annotated[Session, Depends(get_db)] = None,
) -> ManuscriptVersionListResponse:
    """List all versions of a manuscript."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    versions = (
        db.query(ManuscriptVersion)
        .filter(ManuscriptVersion.manuscript_id == manuscript_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(ManuscriptVersion).filter(ManuscriptVersion.manuscript_id == manuscript_id).count()

    return ManuscriptVersionListResponse(
        versions=[ManuscriptVersionInfo.model_validate(v) for v in versions],
        total=total,
    )


@router.post("/manuscripts/{manuscript_id}/evaluate", response_model=EvaluationInfo)
def evaluate_manuscript(
    manuscript_id: int,
    data: EvaluationCreate,
    db: Annotated[Session, Depends(get_db)] = None,
) -> EvaluationInfo:
    """Create an evaluation for a manuscript version."""
    if data.manuscript_version_id:
        version = db.query(ManuscriptVersion).filter(
            ManuscriptVersion.id == data.manuscript_version_id
        ).first()
    else:
        version = db.query(ManuscriptVersion).filter(
            ManuscriptVersion.manuscript_id == manuscript_id
        ).order_by(ManuscriptVersion.version.desc()).first()

    if not version:
        raise HTTPException(status_code=404, detail="No manuscript version found")

    engine = EvaluationEngine(db, model_name=data.model)
    result = engine.evaluate(version.id, journal_id=data.journal_id)

    return EvaluationInfo(
        id=result["evaluation_id"],
        manuscript_version_id=version.id,
        journal_id=result["journal_id"],
        status=result["status"],
        scores=result["scores"],
        final_status=result["final_status"],
        model=data.model,
        prompt_version="phase11",
        created_at=None,
    )


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationDetail)
def get_evaluation(
    evaluation_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
) -> EvaluationDetail:
    """Get evaluation details."""
    engine = EvaluationEngine(db)
    result = engine.get_evaluation(evaluation_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    return EvaluationDetail(**result)


@router.get("/manuscripts/{manuscript_id}/evaluations", response_model=EvaluationListResponse)
def list_manuscript_evaluations(
    manuscript_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Annotated[Session, Depends(get_db)] = None,
) -> EvaluationListResponse:
    """List all evaluations for a manuscript."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    version = db.query(ManuscriptVersion).filter(
        ManuscriptVersion.manuscript_id == manuscript_id
    ).order_by(ManuscriptVersion.version.desc()).first()

    if not version:
        return EvaluationListResponse(evaluations=[], total=0)

    engine = EvaluationEngine(db)
    evaluations = engine.get_manuscript_evaluations(version.id)
    total = len(evaluations)
    paginated = evaluations[skip : skip + limit]

    return EvaluationListResponse(
        evaluations=[EvaluationInfo(**e) for e in paginated],
        total=total,
    )


@router.post("/manuscripts/{manuscript_id}/improve", response_model=ManuscriptImprovementResponse)
def get_improvement_suggestions(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
) -> ManuscriptImprovementResponse:
    """Get improvement suggestions for a manuscript."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    from app.manuscript_engine.compliance import ComplianceEngine
    engine = ComplianceEngine(db)
    result = engine.analyze_manuscript(manuscript)

    from app.services.llm_service import LLMService
    llm = LLMService(db)

    content = ""
    if manuscript.document_id:
        from app.models.document import Document
        doc = db.query(Document).filter(Document.id == manuscript.document_id).first()
        if doc and doc.chunks:
            content = " ".join([chunk.content for chunk in doc.chunks])

    checks = result.get("checks", [])
    style_issues = result.get("style_issues", [])
    improvements = llm.generate_improvements(content, checks, style_issues, title=manuscript.title)

    return ManuscriptImprovementResponse(
        manuscript_id=manuscript.id,
        overall_score=result.get("overall_score", 0),
        improvements=improvements,
    )


# ─── Phase 12: Pre-submission gate ─────────────────────────────────────────


@router.get("/manuscripts/{manuscript_id}/gate/readiness", response_model=PreSubmissionCheckResponse)
def check_pre_submission_readiness(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
) -> PreSubmissionCheckResponse:
    """Run comprehensive pre-submission readiness check."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    gate = PreSubmissionGate(db)
    result = gate.check_readiness(manuscript_id)
    return PreSubmissionCheckResponse(**result)


@router.post("/manuscripts/{manuscript_id}/gate/final-version", response_model=FinalVersionResponse)
def create_final_version(
    manuscript_id: int,
    data: FinalVersionCreate,
    db: Annotated[Session, Depends(get_db)] = None,
) -> FinalVersionResponse:
    """Attempt to create a final submitted version (gated by blocking rules)."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    gate = PreSubmissionGate(db)
    result = gate.create_final_version(manuscript_id, change_summary=data.change_summary)
    return FinalVersionResponse(**result)


@router.get("/manuscripts/{manuscript_id}/gate/evaluation-chain", response_model=list)
def get_evaluation_chain(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Return full evaluation history across all versions in chronological order."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")

    gate = PreSubmissionGate(db)
    chain = gate.get_evaluation_chain(manuscript_id)
    return chain



