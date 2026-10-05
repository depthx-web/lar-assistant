"""Phase 15 engine: AI-powered peer review response letter generation."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import (
    Evaluation, EvaluationIssue, ImprovementSuggestion,
    Manuscript, ManuscriptVersion, PeerReviewResponseLetter,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ResponseLetterEngine:
    """Generate and manage peer review response letters."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMService(db)

    # ------------------------------------------------------------------ #
    #  Core generation                                                     #
    # ------------------------------------------------------------------ #

    def generate_response_letter(
        self,
        manuscript_id: int,
        evaluation_id: Optional[int] = None,
        *,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """Generate a peer review response letter for a manuscript."""
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        # Resolve evaluation
        eval_id = evaluation_id
        if eval_id is None:
            # Find latest evaluation for this manuscript's versions
            latest_version = (
                self.db.query(ManuscriptVersion)
                .filter(ManuscriptVersion.manuscript_id == manuscript_id)
                .order_by(ManuscriptVersion.version.desc())
                .first()
            )
            if latest_version:
                eval_id = (
                    self.db.query(Evaluation)
                    .filter(Evaluation.manuscript_version_id == latest_version.id)
                    .order_by(Evaluation.created_at.desc())
                    .first()
                )
                if eval_id:
                    eval_id = eval_id.id
        if eval_id is None:
            return {"status": "no_evaluation", "letter_id": None}

        # Check for existing letter
        existing = (
            self.db.query(PeerReviewResponseLetter)
            .filter(
                PeerReviewResponseLetter.manuscript_id == manuscript_id,
                PeerReviewResponseLetter.evaluation_id == eval_id,
            )
            .first()
        )
        if existing and not force_regenerate:
            return {"status": "exists", "letter_id": existing.id}

        issues = (
            self.db.query(EvaluationIssue)
            .filter(EvaluationIssue.evaluation_id == eval_id)
            .order_by(EvaluationIssue.id)
            .all()
        )
        suggestions = (
            self.db.query(ImprovementSuggestion)
            .filter(ImprovementSuggestion.manuscript_id == manuscript_id)
            .order_by(ImprovementSuggestion.priority.desc())
            .all()
        )
        # Build letter via LLM
        letter_text = self._build_letter(manuscript, issues, suggestions)

        # Persist
        now = datetime.utcnow()
        addressed_ids = [iss.id for iss in issues]
        if existing:
            existing.cover_letter = letter_text.get("cover_letter")
            existing.response_body = letter_text.get("response_body")
            existing.addressed_issue_ids = json.dumps(addressed_ids)
            existing.generated_at = now
            existing.updated_at = now
            letter_id = existing.id
        else:
            letter = PeerReviewResponseLetter(
                manuscript_id=manuscript_id,
                evaluation_id=eval_id,
                title=letter_text.get("title", "Response to Reviewers"),
                cover_letter=letter_text.get("cover_letter"),
                response_body=letter_text.get("response_body"),
                generated_at=now,
                addressed_issue_ids=json.dumps(addressed_ids),
            )
            self.db.add(letter)
            self.db.flush()
            self.db.refresh(letter)
            letter_id = letter.id

        self.db.commit()
        return {"status": "generated", "letter_id": letter_id}

    # ------------------------------------------------------------------ #
    #  Retrieval                                                           #
    # ------------------------------------------------------------------ #

    def get_letter(self, letter_id: int) -> Optional[Dict[str, Any]]:
        letter = self.db.query(PeerReviewResponseLetter).filter(PeerReviewResponseLetter.id == letter_id).first()
        if not letter:
            return None
        return self._serialize(letter)

    def list_letters(self, manuscript_id: int) -> List[Dict[str, Any]]:
        letters = (
            self.db.query(PeerReviewResponseLetter)
            .filter(PeerReviewResponseLetter.manuscript_id == manuscript_id)
            .order_by(PeerReviewResponseLetter.created_at.desc())
            .all()
        )
        return [self._serialize(l) for l in letters]

    def get_letter_for_manuscript(self, manuscript_id: int, evaluation_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Return the most relevant letter for a manuscript+evaluation pair."""
        q = self.db.query(PeerReviewResponseLetter).filter(
            PeerReviewResponseLetter.manuscript_id == manuscript_id,
        )
        if evaluation_id is not None:
            q = q.filter(PeerReviewResponseLetter.evaluation_id == evaluation_id)
        letter = q.order_by(PeerReviewResponseLetter.created_at.desc()).first()
        return self._serialize(letter) if letter else None

    # ------------------------------------------------------------------ #
    #  Regeneration                                                        #
    # ------------------------------------------------------------------ #

    def regenerate_letter(self, letter_id: int) -> Dict[str, Any]:
        letter = self.db.query(PeerReviewResponseLetter).filter(PeerReviewResponseLetter.id == letter_id).first()
        if not letter:
            raise ValueError(f"Letter {letter_id} not found")
        result = self.generate_response_letter(
            letter.manuscript_id,
            evaluation_id=letter.evaluation_id,
            force_regenerate=True,
        )
        return result

    # ------------------------------------------------------------------ #
    #  LLM generation                                                      #
    # ------------------------------------------------------------------ #

    def _build_letter(
        self,
        manuscript: Manuscript,
        issues: List[EvaluationIssue],
        suggestions: List[ImprovementSuggestion],
    ) -> Dict[str, str]:
        """Attempt LLM generation; fall back to structured template."""
        prompt = self._build_prompt(manuscript, issues, suggestions)
        try:
            if self.llm.provider is not None:
                response = self.llm.provider.generate(
                    prompt=prompt,
                    model=self.llm.model_name,
                    temperature=0.3,
                    max_tokens=2000,
                )
                parsed = self._parse_llm_response(response)
                if parsed:
                    return parsed
        except Exception as exc:
            logger.warning(f"LLM letter generation failed: {exc}")

        return self._fallback_letter(manuscript, issues, suggestions)

    def _build_prompt(self, manuscript, issues, suggestions) -> str:
        issues_text = "\n".join(
            f"- [{iss.severity}] {iss.category}: {iss.message}"
            for iss in issues
        ) or "  (no issues)"
        suggestions_text = "\n".join(
            f"- {s.title}: {s.description}"
            for s in suggestions
        ) or "  (no suggestions)"
        return f"""\
You are an academic researcher responding to peer review comments for your manuscript.

Manuscript Title: {manuscript.title}

Reviewer / Evaluation Issues:
{issues_text}

Suggested Improvements:
{suggestions_text}

Please generate a professional peer review response letter with:
1. A polite cover letter paragraph
2. A structured point-by-point response addressing each issue
3. Clear indication of how each concern was addressed

Return JSON only, no markdown:
{{"title": "...", "cover_letter": "...", "response_body": "..."}}
"""

    def _parse_llm_response(self, text: str) -> Optional[Dict[str, str]]:
        """Try to extract JSON from LLM output."""
        if not text:
            return None
        # Try direct parse
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "cover_letter" in data and "response_body" in data:
                return data
        except json.JSONDecodeError:
            pass
        # Try to find JSON block
        import re
        match = re.search(r"\{[^{}]*\"cover_letter\"[^{}]*\"response_body\"[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data
            except json.JSONDecodeError:
                pass
        return None

    def _fallback_letter(self, manuscript, issues, suggestions) -> Dict[str, str]:
        """Structured fallback when LLM is unavailable."""
        lines = []
        for iss in issues:
            lines.append(f"**Issue ({iss.severity} — {iss.category}):** {iss.message}")
            lines.append(f"  **Response:** We thank the reviewer for this observation. "
                         f"We have addressed this by {iss.message.lower().rstrip('.')}.\n")
        for s in suggestions:
            lines.append(f"**Suggestion ({s.severity} — {s.category}):** {s.title}")
            lines.append(f"  **Action:** {s.suggested_fix or s.description}\n")

        body = "\n".join(lines) or "  (No issues to address — manuscript appears ready.)"
        return {
            "title": f"Response to Reviewers — {manuscript.title}",
            "cover_letter": (
                f"Dear Editor and Reviewers,\n\n"
                f"Thank you for the valuable feedback on our manuscript entitled "
                f"'{manuscript.title}'. We have carefully considered all comments and "
                f"have revised the manuscript accordingly. Below we provide a point-by-point "
                f"response to each comment.\n"
            ),
            "response_body": body,
        }

    # ------------------------------------------------------------------ #
    #  Serialization                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _serialize(letter: PeerReviewResponseLetter) -> Dict[str, Any]:
        addressed = json.loads(letter.addressed_issue_ids) if letter.addressed_issue_ids else []
        return {
            "id": letter.id,
            "manuscript_id": letter.manuscript_id,
            "evaluation_id": letter.evaluation_id,
            "title": letter.title,
            "cover_letter": letter.cover_letter,
            "response_body": letter.response_body,
            "generated_at": letter.generated_at.isoformat() if letter.generated_at else None,
            "addressed_issue_ids": addressed,
            "created_at": letter.created_at.isoformat() if letter.created_at else None,
            "updated_at": letter.updated_at.isoformat() if letter.updated_at else None,
        }
