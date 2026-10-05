"""Compliance engine for manuscript analysis."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.journal import Journal, JournalRequirement
from app.models.manuscript import Manuscript, RequirementStatus

logger = logging.getLogger(__name__)


class ComplianceEngine:
    """Analyze manuscript compliance with journal requirements."""

    def __init__(self, db: Session, rag_engine: Optional[object] = None):
        """Initialize compliance engine.
        
        Args:
            db: Database session
            rag_engine: Optional RAG engine for contextual analysis
        """
        self.db = db
        self.rag_engine = rag_engine

    def analyze_manuscript(self, manuscript: Manuscript) -> Dict[str, Any]:
        """Analyze manuscript against journal requirements."""
        logger.info(f"Analyzing manuscript {manuscript.id}")
        
        manuscript.analysis_status = "PROCESSING"
        self.db.flush()
        
        try:
            requirements = self.db.query(JournalRequirement).filter(
                JournalRequirement.journal_id == manuscript.journal_id
            ).all()
            
            if not requirements:
                manuscript.analysis_status = "COMPLETED"
                manuscript.analyzed_at = datetime.utcnow()
                self.db.commit()
                return {"status": "no_requirements", "checks": []}
            
            from app.models.document import Document
            document = self._get_document(manuscript)
            if not document:
                raise ValueError(f"No document found for manuscript {manuscript.id}")
            
            # Get content from document chunks
            content = " ".join([chunk.content for chunk in document.chunks]) if document.chunks else ""
            if not content:
                logger.warning(f"No content found in document {document.id} for manuscript {manuscript.id}")
            
            checks = []
            mandatory_passed = 0
            mandatory_total = 0
            
            for requirement in requirements:
                check_result = self._check_requirement(requirement, content, document)
                checks.append(check_result)
                
                if requirement.requirement_type == "MANDATORY":
                    mandatory_total += 1
                    if check_result["status"] == "PASS":
                        mandatory_passed += 1
            
            total_checks = len(checks)
            passed_checks = sum(1 for c in checks if c["status"] == "PASS")
            
            overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            mandatory_score = (mandatory_passed / mandatory_total * 100) if mandatory_total > 0 else 0
            
            style_issues = self._detect_style_issues(manuscript, content)
            rejection_risks = self._detect_rejection_risks(manuscript, content)
            
            manuscript.requirement_checks = json.dumps(checks)
            manuscript.style_issues = json.dumps(style_issues)
            manuscript.rejection_risks = json.dumps(rejection_risks)
            manuscript.overall_compliance_score = round(overall_score, 1)
            manuscript.mandatory_compliance_score = round(mandatory_score, 1)
            manuscript.analysis_status = "COMPLETED"
            manuscript.analyzed_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "status": "completed",
                "overall_score": overall_score,
                "mandatory_score": mandatory_score,
                "checks": checks,
                "style_issues": style_issues,
                "rejection_risks": rejection_risks,
            }
            
        except Exception as e:
            logger.exception(f"Failed to analyze manuscript {manuscript.id}: {e}")
            manuscript.analysis_status = "FAILED"
            self.db.commit()
            raise

    def _get_document(self, manuscript: Manuscript) -> Optional[object]:
        """Get document for manuscript."""
        if manuscript.document_id:
            from app.models.document import Document
            return self.db.query(Document).filter(Document.id == manuscript.document_id).first()
        return None

    def _check_requirement(self, requirement: JournalRequirement, content: str, document: object) -> Dict[str, Any]:
        """Check a single requirement using LLM."""
        from app.services.llm_service import LLMService
        llm = LLMService(self.db)
        requirements = [self._requirement_to_dict(requirement)]
        results = llm.check_requirements(requirements, content, title="")
        return results[0] if results else {
            "requirement_id": requirement.id,
            "key": requirement.key,
            "status": "UNKNOWN",
            "confidence": 0.0,
            "details": "Check failed",
        }

    def _requirement_to_dict(self, req: JournalRequirement) -> Dict[str, Any]:
        """Convert requirement to dict for LLM."""
        return {
            "id": req.id,
            "key": req.key,
            "description": req.description,
            "requirement_type": req.requirement_type,
            "evidence_level": req.evidence_level,
        }

    def _detect_style_issues(self, manuscript: Manuscript, content: str) -> List[Dict[str, Any]]:
        """Detect style issues using LLM and journal style profile."""
        from app.services.llm_service import LLMService
        llm = LLMService(self.db)

        # Get journal style profile
        from app.models.journal import Journal, JournalStyleProfile
        journal = self.db.query(Journal).filter(Journal.id == manuscript.journal_id).first()
        if not journal:
            return []

        profile = self.db.query(JournalStyleProfile).filter(
            JournalStyleProfile.journal_id == journal.id
        ).order_by(JournalStyleProfile.analyzed_at.desc()).first()

        if not profile:
            return []

        try:
            import json
            style_profile = json.loads(profile.profile_json)
            return llm.detect_style_issues(content, style_profile, title=manuscript.title)
        except Exception as e:
            logger.warning(f"Style issue detection failed: {e}")
            return []

    def _detect_rejection_risks(self, manuscript: Manuscript, content: str) -> List[Dict[str, Any]]:
        """Detect rejection risks using LLM."""
        from app.services.llm_service import LLMService
        llm = LLMService(self.db)

        score = manuscript.overall_compliance_score or 0.0
        # Get style issues first
        style_issues = self._detect_style_issues(manuscript, content)

        return llm.detect_rejection_risks(content, score, style_issues, title=manuscript.title)
