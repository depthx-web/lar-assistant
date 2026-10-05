"""Phase 14 routes: AI-powered revision & improvement suggestions."""
from __future__ import annotations

import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.manuscript_engine.revision import RevisionEngine
from app.models.manuscript import Manuscript
from app.schemas.phase14 import (
    AddressSuggestionRequest,
    ImprovementSuggestionCreate,
    ImprovementSuggestionInfo,
    ImprovementSuggestionListResponse,
    ImprovementTrackInfo,
    ImprovementSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/manuscripts/{manuscript_id}/improvements", response_model=ImprovementSuggestionListResponse)
def list_improvements(
    manuscript_id: int,
    status: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = RevisionEngine(db)
    suggestions = engine.list_suggestions(manuscript_id, status=status)
    return ImprovementSuggestionListResponse(
        suggestions=[ImprovementSuggestionInfo.model_validate(s) for s in suggestions],
        total=len(suggestions),
    )


@router.post("/manuscripts/{manuscript_id}/improvements/generate", response_model=ImprovementSuggestionListResponse)
def generate_improvements(
    manuscript_id: int,
    data: ImprovementSuggestionCreate,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = RevisionEngine(db)
    result = engine.generate_suggestions(
        manuscript_id, evaluation_id=data.evaluation_id,
        force_regenerate=data.force_regenerate,
    )
    if result["status"] == "no_evaluation":
        raise HTTPException(status_code=400, detail="No evaluation found for this manuscript")
    return ImprovementSuggestionListResponse(
        suggestions=[ImprovementSuggestionInfo.model_validate(s) for s in result["suggestions"]],
        total=len(result["suggestions"]),
    )


@router.post("/manuscripts/{manuscript_id}/improvements/{suggestion_id}/address", response_model=ImprovementSuggestionInfo)
def address_improvement(
    manuscript_id: int,
    suggestion_id: int,
    data: AddressSuggestionRequest,
    db: Annotated[Session, Depends(get_db)] = None,
):
    engine = RevisionEngine(db)
    try:
        result = engine.address_suggestion(
            suggestion_id, manuscript_id,
            version_id=data.version_id, reviewer=data.reviewer,
        )
        return ImprovementSuggestionInfo.model_validate(result)
    except ValueError:
        raise HTTPException(status_code=404, detail="Suggestion not found")


@router.get("/manuscripts/{manuscript_id}/improvements/{suggestion_id}/tracking", response_model=List[ImprovementTrackInfo])
def get_tracking_history(
    manuscript_id: int,
    suggestion_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    engine = RevisionEngine(db)
    tracks = engine.get_tracking_history(suggestion_id)
    return [ImprovementTrackInfo.model_validate(t) for t in tracks]


@router.get("/manuscripts/{manuscript_id}/improvements/summary", response_model=ImprovementSummary)
def get_improvement_summary(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = RevisionEngine(db)
    summary = engine.get_improvement_summary(manuscript_id)
    return ImprovementSummary(**summary)
