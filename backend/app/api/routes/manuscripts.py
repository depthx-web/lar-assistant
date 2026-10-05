"""Manuscript endpoints."""
from __future__ import annotations

import json
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.manuscript_engine.compliance import ComplianceEngine
from app.models.manuscript import Manuscript
from app.models.document import Document
from app.models.journal import Journal
from app.schemas.manuscript import ManuscriptCreate, ManuscriptInfo, ManuscriptListResponse, ManuscriptAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/manuscripts", response_model=ManuscriptListResponse)
def list_manuscripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    journal_id: Optional[int] = Query(None),
    db: Annotated[Session, Depends(get_db)] = None,
) -> ManuscriptListResponse:
    """List all manuscripts."""
    query = db.query(Manuscript)
    if journal_id:
        query = query.filter(Manuscript.journal_id == journal_id)
    
    manuscripts = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ManuscriptListResponse(
        manuscripts=[ManuscriptInfo.model_validate(m) for m in manuscripts],
        total=total,
    )


@router.post("/manuscripts", response_model=ManuscriptInfo)
def create_manuscript(
    data: ManuscriptCreate,
    db: Annotated[Session, Depends(get_db)] = None,
) -> ManuscriptInfo:
    """Create a new manuscript."""
    manuscript = Manuscript(
        title=data.title,
        document_id=data.document_id,
        journal_id=data.journal_id,
    )
    db.add(manuscript)
    db.commit()
    db.refresh(manuscript)
    return ManuscriptInfo.model_validate(manuscript)


@router.post("/manuscripts/{id}/analyze")
def analyze_manuscript(
    id: int,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Analyze manuscript compliance."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {id} not found")
    if not manuscript.journal_id or not manuscript.document_id:
        raise HTTPException(status_code=400, detail="Journal and document required")
    
    try:
        engine = ComplianceEngine(db)
        result = engine.analyze_manuscript(manuscript)
        db.refresh(manuscript)
        return {
            "manuscript_id": manuscript.id,
            "analysis_status": manuscript.analysis_status,
            "overall_score": manuscript.overall_compliance_score,
            "mandatory_score": manuscript.mandatory_compliance_score,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/manuscripts/{id}")
def delete_manuscript(id: int, db: Annotated[Session, Depends(get_db)] = None):
    """Delete manuscript."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {id} not found")
    db.delete(manuscript)
    db.commit()
    return {"status": "deleted", "id": id}

@router.get("/manuscripts/{id}", response_model=ManuscriptInfo)
def get_manuscript(id: int, db: Annotated[Session, Depends(get_db)] = None):
    manuscript = db.query(Manuscript).filter(Manuscript.id == id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail=f"Manuscript {id} not found")
    return ManuscriptInfo.model_validate(manuscript)
