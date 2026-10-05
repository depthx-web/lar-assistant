"""Evaluator engine for manuscript scoring and evaluation."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import Evaluation, EvaluationIssue, ManuscriptVersion
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """Engine for evaluating manuscripts against journals."""

    def __init__(self, db: Session, model_name: str = "qwen2.5:3b-instruct"):
        self.db = db
        self.model_name = model_name
        self.llm = LLMService(db, model_name)

    def _get_content(self, manuscript: Manuscript) -> Optional[str]:
        """Get full text content from manuscript's document."""
        if not manuscript.document_id:
            return None
        from app.models.document import Document
        doc = self.db.query(Document).filter(Document.id == manuscript.document_id).first()
        if not doc or not doc.chunks:
            return None
        return " ".join([chunk.content for chunk in doc.chunks])

    def _generate_scores(self, content: str, requirements, compliance_score, title: str) -> Dict[str, Any]:
        """Generate evaluation scores using LLM."""
        prompt = self._build_scoring_prompt(content, requirements, compliance_score, title)
        try:
            response = self.llm.provider.generate(
                prompt=prompt,
                model=self.llm.model_name,
                temperature=0.3,
                max_tokens=1000,
            )
            return self._parse_scores(response)
        except Exception as e:
            logger.warning(f"Score generation failed: {e}")
            return self._fallback_scores(compliance_score)

    def _build_scoring_prompt(self, content, requirements, compliance_score, title):
        reqs_text = "\n".join(f"- {r.key}: {r.description}" for r in requirements[:10])
        return f"""You are a journal editor evaluating a manuscript.

Manuscript Title: {title}
Compliance Score: {compliance_score:.0f}%

Requirements:
{reqs_text}

Manuscript Content (first 3000 chars):
{content[:3000]}

Evaluate and return scores 0-100 for: compliance, scientific, methodology, writing, novelty, readiness.
Also identify up to 5 critical issues.

Respond in JSON: {{
  "compliance": <0-100>, "scientific": <0-100>, "methodology": <0-100>,
  "writing": <0-100>, "novelty": <0-100>, "readiness": <0-100>,
  "issues": [{{"severity": "<critical|major|minor>", "category": "<string>", "message": "<string>"}}]
}}"""

    def _parse_scores(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into scores."""
        import re
        text = response.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    return self._fallback_scores(50)
            else:
                return self._fallback_scores(50)

        return {
            "compliance": data.get("compliance", 50),
            "scientific": data.get("scientific", 50),
            "methodology": data.get("methodology", 50),
            "writing": data.get("writing", 50),
            "novelty": data.get("novelty", 50),
            "readiness": data.get("readiness", 50),
            "issues": data.get("issues", []),
        }

    def _fallback_scores(self, compliance: float) -> Dict[str, Any]:
        """Fallback scores when LLM unavailable."""
        return {
            "compliance": int(compliance),
            "scientific": int(compliance * 0.9),
            "methodology": int(compliance * 0.85),
            "writing": int(compliance * 0.8),
            "novelty": int(compliance * 0.75),
            "readiness": int(compliance * 0.7),
            "issues": [],
        }

    def get_evaluation(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """Get evaluation by ID."""
        eval_record = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval_record:
            return None

        issues = self.db.query(EvaluationIssue).filter(
            EvaluationIssue.evaluation_id == evaluation_id
        ).all()

        return {
            "id": eval_record.id,
            "manuscript_version_id": eval_record.manuscript_version_id,
            "journal_id": eval_record.journal_id,
            "status": eval_record.status,
            "scores": {
                "compliance_score": eval_record.compliance_score,
                "scientific_score": eval_record.scientific_score,
                "methodology_score": eval_record.methodology_score,
                "writing_score": eval_record.writing_score,
                "novelty_score": eval_record.novelty_score,
                "readiness_score": eval_record.readiness_score,
            },
            "final_status": eval_record.final_status,
            "model": eval_record.model,
            "issues": [
                {"id": issue.id, "severity": issue.severity, "category": issue.category,
                 "message": issue.message, "is_blocking": issue.is_blocking}
                for issue in issues
            ],
            "created_at": eval_record.created_at.isoformat(),
        }

    def get_manuscript_evaluations(self, manuscript_version_id: int) -> List[Dict[str, Any]]:
        """Get all evaluations for a manuscript version."""
        evaluations = self.db.query(Evaluation).filter(
            Evaluation.manuscript_version_id == manuscript_version_id
        ).order_by(Evaluation.created_at.desc()).all()

        return [
            {
                "id": e.id, "journal_id": e.journal_id, "status": e.status,
                "scores": {
                    "compliance_score": e.compliance_score, "scientific_score": e.scientific_score,
                    "methodology_score": e.methodology_score, "writing_score": e.writing_score,
                    "novelty_score": e.novelty_score, "readiness_score": e.readiness_score,
                },
                "final_status": e.final_status,
                "created_at": e.created_at.isoformat(),
            }
            for e in evaluations
        ]

        """Create EvaluationIssue records."""
        issues = []
        for issue_data in issues_data[:10]:
            issue = EvaluationIssue(
                evaluation_id=evaluation_id,
                severity=issue_data.get("severity", "minor"),
                category=issue_data.get("category", "other"),
                message=issue_data.get("message", ""),
                is_blocking=issue_data.get("severity") == "critical",
            )
            self.db.add(issue)
            issues.append(issue)
        self.db.commit()
        return issues

        """Evaluate a manuscript version."""
        from app.models.manuscript import Manuscript
        from app.models.journal import Journal, JournalRequirement

        version = self.db.query(ManuscriptVersion).filter(
            ManuscriptVersion.id == manuscript_version_id
        ).first()
        if not version:
            raise ValueError(f"Manuscript version {manuscript_version_id} not found")

        manuscript = self.db.query(Manuscript).filter(
            Manuscript.id == version.manuscript_id
        ).first()
        if not manuscript:
            raise ValueError(f"Manuscript {version.manuscript_id} not found")

        target_journal_id = journal_id or manuscript.journal_id
        if not target_journal_id:
            raise ValueError("No journal_id specified and manuscript has no journal")

        journal = self.db.query(Journal).filter(Journal.id == target_journal_id).first()
        if not journal:
            raise ValueError(f"Journal {target_journal_id} not found")

        content = self._get_content(manuscript)
        if not content:
            return {"status": "incomplete", "scores": {}, "issues": [], "message": "No document content"}

        requirements = self.db.query(JournalRequirement).filter(
            JournalRequirement.journal_id == target_journal_id
        ).all()

        compliance_score = manuscript.overall_compliance_score or 50.0
        scores = self._generate_scores(content, requirements, compliance_score, manuscript.title)

        evaluation = Evaluation(
            manuscript_version_id=manuscript_version_id,
            journal_id=target_journal_id,
            status="COMPLETED",
            compliance_score=int(scores.get("compliance", 0)),
            scientific_score=int(scores.get("scientific", 0)),
            methodology_score=int(scores.get("methodology", 0)),
            writing_score=int(scores.get("writing", 0)),
            novelty_score=int(scores.get("novelty", 0)),
            readiness_score=int(scores.get("readiness", 0)),
            final_status="READY" if scores.get("readiness", 0) >= 70 else "NEEDS_REVISION",
            model=self.model_name,
            prompt_version="phase11",
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        issues = self._create_issues(evaluation.id, scores.get("issues", []))

        return {
            "evaluation_id": evaluation.id,
            "manuscript_id": manuscript.id,
            "journal_id": target_journal_id,
            "status": "completed",
            "scores": scores,
            "issues": [issue.to_dict() for issue in issues],
            "final_status": evaluation.final_status,
        }

