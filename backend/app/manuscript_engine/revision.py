"""AI-powered revision engine for Phase 14."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import (
    Evaluation,
    EvaluationIssue,
    ImprovementSuggestion,
    ImprovementTrack,
    Manuscript,
    ManuscriptVersion,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class RevisionEngine:
    """Generate AI-powered improvement suggestions and track their resolution."""

    def __init__(self, db: Session, model_name: str = "qwen2.5:3b-instruct"):
        self.db = db
        self.model_name = model_name
        self.llm = LLMService(db, model_name)

    def _get_manuscript_content(self, manuscript: Manuscript) -> Optional[str]:
        if not manuscript.document_id:
            return None
        from app.models.document import Document
        doc = self.db.query(Document).filter(Document.id == manuscript.document_id).first()
        if not doc or not doc.chunks:
            return None
        return " ".join([chunk.content for chunk in doc.chunks])

    def _build_suggestion_prompt(self, manuscript: Manuscript, evaluation: Evaluation,
                                  issues: List[EvaluationIssue], content: str) -> str:
        issues_text = "\n".join(
            f"- [{issue.severity}] {issue.category}: {issue.message}"
            for issue in issues[:10]
        )
        content_preview = content[:3000] if content else "No content available"
        return f"""You are an expert academic journal editor providing constructive feedback.

Manuscript: {manuscript.title}
Journal ID: {evaluation.journal_id}

Evaluation Scores:
- Compliance: {evaluation.compliance_score}%
- Scientific: {evaluation.scientific_score}%
- Methodology: {evaluation.methodology_score}%

Identified Issues ({len(issues)} total):
{issues_text if issues_text else "No specific issues identified"}

Manuscript Content (excerpt):
{content_preview}

Generate actionable improvement suggestions in JSON format:
{{
  "suggestions": [
    {{
      "category": "<string>",
      "severity": "<critical|major|minor>",
      "title": "<short title>",
      "description": "<detailed explanation>",
      "suggested_fix": "<concrete actionable fix>",
      "evidence": "<quote from manuscript if applicable>"
    }}
  ]
}}

Return only valid JSON."""

    def generate_suggestions(self, manuscript_id: int, evaluation_id: Optional[int] = None,
                              force_regenerate: bool = False) -> Dict[str, Any]:
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        if evaluation_id:
            evaluation = self.db.query(Evaluation).filter(
                Evaluation.id == evaluation_id,
                Evaluation.manuscript_version_id.in_(
                    self.db.query(ManuscriptVersion.id).filter(
                        ManuscriptVersion.manuscript_id == manuscript_id
                    )
                )
            ).first()
            if not evaluation:
                raise ValueError(f"Evaluation {evaluation_id} not found")
        else:
            evaluation = self.db.query(Evaluation).join(
                ManuscriptVersion, Evaluation.manuscript_version_id == ManuscriptVersion.id
            ).filter(
                ManuscriptVersion.manuscript_id == manuscript_id
            ).order_by(Evaluation.created_at.desc()).first()

        if not evaluation:
            return {"status": "no_evaluation", "suggestions": []}

        issues = self.db.query(EvaluationIssue).filter(
            EvaluationIssue.evaluation_id == evaluation.id
        ).all()

        existing = self.db.query(ImprovementSuggestion).filter(
            ImprovementSuggestion.manuscript_id == manuscript_id,
            ImprovementSuggestion.evaluation_id == evaluation.id
        ).all()

        if existing and not force_regenerate:
            return {
                "status": "existing",
                "evaluation_id": evaluation.id,
                "suggestions": [s.to_dict() for s in existing],
            }

        content = self._get_manuscript_content(manuscript)
        prompt = self._build_suggestion_prompt(manuscript, evaluation, issues, content or "")

        parsed = []
        if self.llm.provider is not None:
            try:
                response = self.llm.provider.generate(
                    prompt=prompt,
                    model=self.llm.model_name,
                    temperature=0.3,
                    max_tokens=1500,
                )
                parsed = self._parse_suggestions(response)
            except Exception as e:
                logger.warning(f"Suggestion generation failed: {e}")

        if not parsed:
            parsed = self._fallback_suggestions(manuscript, evaluation, issues)

        for suggestion_data in parsed:
            suggestion = ImprovementSuggestion(
                manuscript_id=manuscript_id,
                evaluation_id=evaluation.id,
                category=suggestion_data.get("category", "general"),
                severity=suggestion_data.get("severity", "minor"),
                title=suggestion_data.get("title", "Improve manuscript"),
                description=suggestion_data.get("description", ""),
                suggested_fix=suggestion_data.get("suggested_fix"),
                evidence=suggestion_data.get("evidence"),
                priority=self._compute_priority(suggestion_data.get("severity", "minor")),
            )
            self.db.add(suggestion)
            self.db.flush()
            for issue in issues:
                if issue.category.lower() == suggestion_data.get("category", "").lower():
                    suggestion.source_issue_id = issue.id
                    break

        self.db.commit()

        suggestions = self.db.query(ImprovementSuggestion).filter(
            ImprovementSuggestion.manuscript_id == manuscript_id,
            ImprovementSuggestion.evaluation_id == evaluation.id
        ).order_by(ImprovementSuggestion.priority.desc()).all()

        return {"status": "generated", "evaluation_id": evaluation.id,
                "suggestions": [s.to_dict() for s in suggestions]}

    def _parse_suggestions(self, response: str) -> List[Dict[str, Any]]:
        text = response.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    return []
            else:
                return []
        suggestions = data.get("suggestions", [])
        if isinstance(suggestions, dict):
            suggestions = [suggestions]
        return suggestions if suggestions else []

    def _fallback_suggestions(self, manuscript: Manuscript, evaluation: Evaluation,
                               issues: List[EvaluationIssue]) -> List[Dict[str, Any]]:
        return [{"category": issue.category, "severity": issue.severity,
                 "title": f"Address {issue.category}", "description": issue.message,
                 "suggested_fix": f"Review and revise {issue.category.lower()}",
                 "evidence": issue.evidence} for issue in issues[:5]]

    def _compute_priority(self, severity: str) -> int:
        return {"critical": 3, "major": 2, "minor": 1}.get(severity, 0)

    def list_suggestions(self, manuscript_id: int, status: Optional[str] = None) -> List[ImprovementSuggestion]:
        query = self.db.query(ImprovementSuggestion).filter(
            ImprovementSuggestion.manuscript_id == manuscript_id)
        if status == "unaddressed":
            query = query.filter(ImprovementSuggestion.is_addressed == False)
        elif status == "addressed":
            query = query.filter(ImprovementSuggestion.is_addressed == True)
        return query.order_by(ImprovementSuggestion.priority.desc()).all()

    def address_suggestion(self, suggestion_id: int, manuscript_id: int,
                            version_id: Optional[int] = None, reviewer: Optional[str] = None) -> Dict[str, Any]:
        suggestion = self.db.query(ImprovementSuggestion).filter(
            ImprovementSuggestion.id == suggestion_id,
            ImprovementSuggestion.manuscript_id == manuscript_id).first()
        if not suggestion:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        suggestion.is_addressed = True
        suggestion.addressed_at = datetime.utcnow()
        suggestion.addressed_version_id = version_id
        self.db.commit()
        track = ImprovementTrack(
            suggestion_id=suggestion_id, manuscript_id=manuscript_id,
            version_id=version_id or 0, action="addressed",
            action_detail=f"Marked by {reviewer}" if reviewer else None, reviewer=reviewer)
        self.db.add(track)
        self.db.commit()
        return suggestion.to_dict()

    def get_tracking_history(self, suggestion_id: int) -> List[Dict[str, Any]]:
        tracks = self.db.query(ImprovementTrack).filter(
            ImprovementTrack.suggestion_id == suggestion_id
        ).order_by(ImprovementTrack.created_at.desc()).all()
        return [t.to_dict() for t in tracks]

    def get_improvement_summary(self, manuscript_id: int) -> Dict[str, Any]:
        suggestions = self.list_suggestions(manuscript_id)
        total = len(suggestions)
        addressed = sum(1 for s in suggestions if s.is_addressed)
        by_severity = {"critical": 0, "major": 0, "minor": 0}
        for s in suggestions:
            if s.severity in by_severity:
                by_severity[s.severity] += 1
        by_category: Dict[str, int] = {}
        for s in suggestions:
            by_category[s.category] = by_category.get(s.category, 0) + 1
        return {"manuscript_id": manuscript_id, "total_suggestions": total,
                "addressed": addressed, "unaddressed": total - addressed,
                "addressed_ratio": round(addressed / total, 2) if total > 0 else 0.0,
                "by_severity": by_severity, "by_category": by_category}


def _suggestion_to_dict(self) -> Dict[str, Any]:
    return {"id": self.id, "manuscript_id": self.manuscript_id,
            "evaluation_id": self.evaluation_id, "source_issue_id": self.source_issue_id,
            "category": self.category, "severity": self.severity, "title": self.title,
            "description": self.description, "suggested_fix": self.suggested_fix,
            "evidence": self.evidence, "priority": self.priority,
            "is_addressed": self.is_addressed,
            "addressed_at": self.addressed_at.isoformat() if self.addressed_at else None,
            "addressed_version_id": self.addressed_version_id,
            "created_at": self.created_at.isoformat() if self.created_at else None}


def _track_to_dict(self) -> Dict[str, Any]:
    return {"id": self.id, "suggestion_id": self.suggestion_id,
            "manuscript_id": self.manuscript_id, "version_id": self.version_id,
            "action": self.action, "action_detail": self.action_detail,
            "reviewer": self.reviewer,
            "created_at": self.created_at.isoformat() if self.created_at else None}


ImprovementSuggestion.to_dict = _suggestion_to_dict
ImprovementTrack.to_dict = _track_to_dict
