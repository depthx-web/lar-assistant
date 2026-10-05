"""Journal endpoints."""
from __future__ import annotations

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.journal_engine.loader import JournalLoader
from app.journal_engine.update import JournalUpdateEngine
from app.journal_engine.style_analyzer import StyleAnalyzer, StyleProfile
from app.models.journal import Journal, JournalRequirement
from app.schemas.journal import (
    JournalInfo,
    JournalDetail,
    JournalListResponse,
    RequirementInfo,
    JournalLoadResponse,
    JournalUpdateCheckResponse,
    JournalUpdateApplyResponse,
    StyleProfileSchema,
    StyleAnalysisHistoryResponse,
    StyleBatchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/journals", response_model=JournalListResponse, summary="List journals")
def list_journals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Annotated[Session, Depends(get_db)] = None,
) -> JournalListResponse:
    """List all journal profiles."""
    journals = db.query(Journal).offset(skip).limit(limit).all()
    total = db.query(Journal).count()
    
    return JournalListResponse(
        journals=[JournalInfo.model_validate(j) for j in journals],
        total=total,
    )


@router.get("/journals/{slug}", response_model=JournalDetail, summary="Get journal by slug")
def get_journal(
    slug: str,
    db: Annotated[Session, Depends(get_db)] = None,
) -> JournalDetail:
    """Get detailed journal profile."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()
    
    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")
    
    # Load requirements
    requirements = db.query(JournalRequirement).filter(
        JournalRequirement.journal_id == journal.id
    ).all()
    
    # Convert to dict and add requirements
    journal_dict = {
        "id": journal.id,
        "name": journal.name,
        "slug": journal.slug,
        "publisher": journal.publisher,
        "issn": journal.issn,
        "official_url": journal.official_url,
        "author_guidelines_url": journal.author_guidelines_url,
        "scope": journal.scope,
        "reference_style": journal.reference_style,
        "article_types": journal.article_types,
        "word_limits": journal.word_limits,
        "style_guide": journal.style_guide,
        "rejection_patterns": journal.rejection_patterns,
        "created_at": journal.created_at,
        "updated_at": journal.updated_at,
        "requirements": [RequirementInfo.model_validate(r) for r in requirements],
    }
    
    return JournalDetail(**journal_dict)


@router.get("/journals/{slug}/requirements", response_model=list[RequirementInfo], summary="Get journal requirements")
def get_journal_requirements(
    slug: str,
    requirement_type: str = Query(None, description="Filter by type: MANDATORY, RECOMMENDED, PREFERRED"),
    db: Annotated[Session, Depends(get_db)] = None,
) -> list[RequirementInfo]:
    """Get requirements for a specific journal."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()
    
    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")
    
    query = db.query(JournalRequirement).filter(JournalRequirement.journal_id == journal.id)
    
    if requirement_type:
        query = query.filter(JournalRequirement.requirement_type == requirement_type.upper())
    
    requirements = query.all()
    
    return [RequirementInfo.model_validate(r) for r in requirements]


@router.post("/journals/load", response_model=JournalLoadResponse, summary="Load journals from YAML")
def load_journals(
    db: Annotated[Session, Depends(get_db)] = None,
) -> JournalLoadResponse:
    """Load all journal profiles from journals/ directory.
    
    This reads YAML files from the journals/ folder and updates the database.
    """
    logger.info("Loading journal profiles from YAML files")
    
    try:
        loader = JournalLoader(db)
        count = loader.load_all()
        
        return JournalLoadResponse(
            loaded_count=count,
            message=f"Successfully loaded {count} journal profile(s)",
        )
    except Exception as e:
        logger.exception(f"Failed to load journals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load journals: {str(e)}")


@router.post("/journals/{slug}/update/check", response_model=JournalUpdateCheckResponse, summary="Check for journal updates")
def check_journal_update(
    slug: str,
    source_url: str = Query(..., description="URL of the new requirements source to check against"),
    source_title: str | None = Query(None, description="Human-readable title of the source"),
    db: Annotated[Session, Depends(get_db)] = None,
) -> JournalUpdateCheckResponse:
    """Check for changes in journal requirements from an external source."""
    try:
        engine = JournalUpdateEngine(db)
        result = engine.compare_with_source(
            slug=slug,
            source_url=source_url,
            source_title=source_title,
        )
        return JournalUpdateCheckResponse(
            journal_slug=result.journal_slug,
            has_changes=result.has_changes,
            needs_confirmation=result.needs_confirmation,
            added_count=len(result.added),
            removed_count=len(result.removed),
            changed_count=len(result.changed),
            source_url=result.source_url,
            added=[RequirementChangeSchema(**c) for c in result.to_dict()["added"]],
            removed=[RequirementChangeSchema(**c) for c in result.to_dict()["removed"]],
            changed=[RequirementChangeSchema(**c) for c in result.to_dict()["changed"]],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to check update for journal {slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check update: {str(e)}")


@router.post("/journals/{slug}/update/apply", response_model=JournalUpdateApplyResponse, summary="Apply journal update")
def apply_journal_update(
    slug: str,
    source_url: str = Query(..., description="Source URL that was previously checked"),
    source_title: str | None = Query(None),
    db: Annotated[Session, Depends(get_db)] = None,
) -> JournalUpdateApplyResponse:
    """Apply confirmed updates to a journal's requirements."""
    try:
        engine = JournalUpdateEngine(db)
        count = engine.apply_update(
            slug=slug,
            source_url=source_url,
            source_title=source_title,
        )
        from datetime import datetime
        return JournalUpdateApplyResponse(
            journal_slug=slug,
            message=f"Update applied successfully ({count} record(s) updated)",
            source_url=source_url,
            verified_at=datetime.utcnow(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to apply update for journal {slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply update: {str(e)}")


@router.post("/journals/{slug}/style/analyze", response_model=StyleProfileSchema, summary="Analyze journal style")
def analyze_journal_style(
    slug: str,
    db: Annotated[Session, Depends(get_db)] = None,
) -> StyleProfileSchema:
    """Analyze and extract style profile for a journal using LLM."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()
    
    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")
    
    analyzer = StyleAnalyzer(db=db)
    profile = analyzer.analyze_from_papers(journal_slug=slug, paper_texts=[])
    
    return StyleProfileSchema(
        structure=profile.structure,
        section_order=profile.section_order,
        paragraph_length_avg=profile.paragraph_length_avg,
        paragraph_style=profile.paragraph_style,
        sentence_length_avg=profile.sentence_length_avg,
        active_voice_ratio=profile.active_voice_ratio,
        passive_voice_ratio=profile.passive_voice_ratio,
        voice_preference=profile.voice_preference,
        tone=profile.tone,
        terminology_level=profile.terminology_level,
        jargon_density=profile.jargon_density,
        citation_style=profile.citation_style,
        avg_citations_per_section=profile.avg_citations_per_section,
        methods_detail_level=profile.methods_detail_level,
        results_style=profile.results_style,
        discussion_approach=profile.discussion_approach,
    )


@router.get("/journals/{slug}/style/profile", response_model=StyleProfileSchema, summary="Get stored style profile")
def get_journal_style_profile(
    slug: str,
    db: Annotated[Session, Depends(get_db)] = None,
) -> StyleProfileSchema:
    """Get previously analyzed style profile for a journal."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()
    
    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")
    
    analyzer = StyleAnalyzer(db=db)
    profile = analyzer.get_profile(slug)
    
    if not profile:
        raise HTTPException(status_code=404, detail="No style profile found. Run analysis first.")
    
    return StyleProfileSchema(
        structure=profile.structure,
        section_order=profile.section_order,
        paragraph_length_avg=profile.paragraph_length_avg,
        paragraph_style=profile.paragraph_style,
        sentence_length_avg=profile.sentence_length_avg,
        active_voice_ratio=profile.active_voice_ratio,
        passive_voice_ratio=profile.passive_voice_ratio,
        voice_preference=profile.voice_preference,
        tone=profile.tone,
        terminology_level=profile.terminology_level,
        jargon_density=profile.jargon_density,
        citation_style=profile.citation_style,
        avg_citations_per_section=profile.avg_citations_per_section,
        methods_detail_level=profile.methods_detail_level,
        results_style=profile.results_style,
        discussion_approach=profile.discussion_approach,
    )


@router.get("/journals/{slug}/style/analysis-info", summary="Get style analysis metadata")
def get_style_analysis_info(
    slug: str,
    db: Annotated[Session, Depends(get_db)] = None,
) -> dict:
    """Get metadata about the latest style analysis."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()
    
    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")
    
    analyzer = StyleAnalyzer(db=db)
    analysis_info = analyzer.get_latest_analysis(slug)
    
    if not analysis_info:
        raise HTTPException(status_code=404, detail="No style analysis found. Run analysis first.")
    
    return analysis_info


@router.get(
    "/journals/{slug}/style/history",
    summary="Get style analysis history",
)
def get_style_analysis_history(
    slug: str,
    limit: int = Query(10, ge=1, le=50),
    db: Annotated[Session, Depends(get_db)] = None,
) -> dict:
    """Get full analysis history for a journal."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()

    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")

    analyzer = StyleAnalyzer(db=db)
    history = analyzer.get_analysis_history(slug, limit=limit)

    return {
        "journal_slug": slug,
        "total_analyses": len(history),
        "history": history,
    }


@router.post(
    "/journals/batch/style/analyze",
    summary="Batch analyze style for multiple journals",
)
def batch_analyze_styles(
    journal_slugs: List[str] = Query(..., description="List of journal slugs to analyze"),
    max_papers_per_journal: int = Query(10, ge=1, le=50),
    db: Annotated[Session, Depends(get_db)] = None,
) -> dict:
    """Analyze style profiles for multiple journals in a single request."""
    analyzer = StyleAnalyzer(db=db)
    results = []
    analyzed_count = 0
    failed_count = 0

    for slug in journal_slugs:
        paper_texts = analyzer.fetch_papers_for_journal(slug, max_papers=max_papers_per_journal)

        try:
            profile = analyzer.analyze_from_papers(
                journal_slug=slug,
                paper_texts=paper_texts,
            )
            results.append({
                "journal_slug": slug,
                "structure": profile.structure,
                "tone": profile.tone,
                "voice_preference": profile.voice_preference,
                "analyzed": True,
            })
            analyzed_count += 1
        except Exception as e:
            logger.error(f"Batch analysis failed for {slug}: {e}")
            results.append({
                "journal_slug": slug,
                "analyzed": False,
                "error": str(e),
            })
            failed_count += 1

    return {
        "analyzed_count": analyzed_count,
        "failed_count": failed_count,
        "results": results,
    }


@router.get(
    "/journals/{slug}/style/papers",
    summary="Get papers for a journal (for style analysis)",
)
def get_journal_papers(
    slug: str,
    max_papers: int = Query(10, ge=1, le=50),
    db: Annotated[Session, Depends(get_db)] = None,
) -> dict:
    """Retrieve paper texts available in the document store for a journal."""
    journal = db.query(Journal).filter(Journal.slug == slug).first()

    if not journal:
        raise HTTPException(status_code=404, detail=f"Journal {slug} not found")

    analyzer = StyleAnalyzer(db=db)
    paper_texts = analyzer.fetch_papers_for_journal(slug, max_papers=max_papers)

    return {
        "journal_slug": slug,
        "paper_count": len(paper_texts),
        "papers": paper_texts,
    }
