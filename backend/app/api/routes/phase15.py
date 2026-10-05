"""Phase 15 routes: Peer review response letter generation."""
from __future__ import annotations

import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.manuscript_engine.response_letter import ResponseLetterEngine
from app.models.manuscript import Manuscript
from app.schemas.phase15 import (
    GenerateLetterRequest,
    ResponseLetterInfo,
    ResponseLetterListResponse,
    ResponseLetterSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/manuscripts/{manuscript_id}/response-letters/generate", response_model=ResponseLetterInfo)
def generate_response_letter(
    manuscript_id: int,
    data: GenerateLetterRequest,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ResponseLetterEngine(db)
    result = engine.generate_response_letter(
        manuscript_id,
        evaluation_id=data.evaluation_id,
        force_regenerate=data.force_regenerate,
    )
    if result["status"] == "no_evaluation":
        raise HTTPException(status_code=400, detail="No evaluation found for this manuscript")
    letter = engine.get_letter(result["letter_id"])
    if not letter:
        raise HTTPException(status_code=500, detail="Failed to retrieve generated letter")
    return ResponseLetterInfo(**letter)


@router.get("/manuscripts/{manuscript_id}/response-letters", response_model=ResponseLetterListResponse)
def list_response_letters(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ResponseLetterEngine(db)
    letters = engine.list_letters(manuscript_id)
    return ResponseLetterListResponse(letters=letters, total=len(letters))


@router.get("/manuscripts/{manuscript_id}/response-letters/summary", response_model=ResponseLetterSummary)
def get_response_letter_summary(
    manuscript_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ResponseLetterEngine(db)
    letters = engine.list_letters(manuscript_id)
    latest = letters[0] if letters else None
    return ResponseLetterSummary(
        manuscript_id=manuscript_id,
        total_letters=len(letters),
        latest_letter_id=latest["id"] if latest else None,
        has_cover_letter=bool(latest and latest.get("cover_letter")),
        has_response_body=bool(latest and latest.get("response_body")),
    )


@router.get("/manuscripts/{manuscript_id}/response-letters/{letter_id}", response_model=ResponseLetterInfo)
def get_response_letter(
    manuscript_id: int,
    letter_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ResponseLetterEngine(db)
    letter = engine.get_letter(letter_id)
    if not letter:
        raise HTTPException(status_code=404, detail=f"Letter {letter_id} not found")
    if letter["manuscript_id"] != manuscript_id:
        raise HTTPException(status_code=404, detail=f"Letter {letter_id} not found")
    return ResponseLetterInfo(**letter)


@router.post("/manuscripts/{manuscript_id}/response-letters/{letter_id}/regenerate", response_model=ResponseLetterInfo)
def regenerate_response_letter(
    manuscript_id: int,
    letter_id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    if not db.query(Manuscript).filter(Manuscript.id == manuscript_id).first():
        raise HTTPException(status_code=404, detail=f"Manuscript {manuscript_id} not found")
    engine = ResponseLetterEngine(db)
    result = engine.regenerate_letter(letter_id)
    letter = engine.get_letter(result["letter_id"])
    if not letter:
        raise HTTPException(status_code=500, detail="Failed to retrieve regenerated letter")
    return ResponseLetterInfo(**letter)

