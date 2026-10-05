"""Final pre-submission gate engine for Phase 12."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.journal import Journal, JournalRequirement
from app.models.manuscript import (
    AnalysisStatus,
    Evaluation,
    EvaluationIssue,
    Manuscript,
    ManuscriptVersion,
    RequirementStatus,
)

logger = logging.getLogger(__name__)


class BlockingRule:
    """Single blocking or warning rule definition."""

    def __init__(
        self,
        rule_id: str,
        severity: str,
        check_fn,
        message_template: str,
        requirement_key: Optional[str] = None,
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.check_fn = check_fn
        self.message_template = message_template
        self.requirement_key = requirement_key

    def evaluate(self, manuscript: Manuscript, db: Session) -> Optional[Dict[str, Any]]:
        if self.check_fn(manuscript, db):
            message = self.message_template.format(
                title=manuscript.title,
                journal_id=manuscript.journal_id or "?",
                score=manuscript.mandatory_compliance_score or 0.0,
                status=manuscript.analysis_status,
                threshold=self.readiness_threshold if hasattr(self, "readiness_threshold") else 70.0,
            )
            return {
                "rule": self.rule_id,
                "severity": self.severity,
                "message": message,
                "requirement_key": self.requirement_key,
            }
        return None


class PreSubmissionGate:
    """Runs blocking-rule checks and computes a readiness score."""

    def __init__(
        self,
        db: Session,
        readiness_threshold: float = 70.0,
    ):
        self.db = db
        self.readiness_threshold = readiness_threshold
        self._rules: List[BlockingRule] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register the standard blocking and warning rules."""
        self.add_rule(BlockingRule(
            rule_id="no_analysis",
            severity="critical",
            message_template="Manuscript has not been analyzed (status: {status}). Run compliance analysis first.",
            check_fn=lambda m, db: m.analysis_status != AnalysisStatus.COMPLETED,
        ))
        self.add_rule(BlockingRule(
            rule_id="no_journal",
            severity="critical",
            message_template="No journal assigned. A journal is required for submission.",
            check_fn=lambda m, db: m.journal_id is None,
        ))
        self.add_rule(BlockingRule(
            rule_id="no_document",
            severity="warning",
            message_template="No document attached. Upload or link a document before submitting.",
            check_fn=lambda m, db: m.document_id is None,
        ))
        self.add_rule(BlockingRule(
            rule_id="mandatory_fail",
            severity="critical",
            message_template="Mandatory requirements not met. Mandatory compliance score: {score:.0f}%. All mandatory rules must PASS.",
            check_fn=lambda m, db: (m.mandatory_compliance_score or 0.0) < 100.0,
            requirement_key="mandatory_requirements",
        ))
        self.add_rule(BlockingRule(
            rule_id="low_readiness",
            severity="warning",
            message_template="Readiness score {score:.0f}% is below the threshold of {threshold}%. Consider revising before submission.",
            check_fn=lambda m, db: (m.overall_compliance_score or 0.0) < self.readiness_threshold,
        ))
        self.add_rule(BlockingRule(
            rule_id="failed_analysis",
            severity="critical",
            message_template="Analysis failed. Please re-run compliance analysis.",
            check_fn=lambda m, db: m.analysis_status == AnalysisStatus.FAILED,
        ))
        self.add_rule(BlockingRule(
            rule_id="pending_analysis",
            severity="warning",
            message_template="Analysis is still pending. Wait for analysis to complete.",
            check_fn=lambda m, db: m.analysis_status == AnalysisStatus.PENDING,
        ))
        self.add_rule(BlockingRule(
            rule_id="processing_analysis",
            severity="warning",
            message_template="Analysis is currently processing. Please wait.",
            check_fn=lambda m, db: m.analysis_status == AnalysisStatus.PROCESSING,
        ))

    def add_rule(self, rule: BlockingRule) -> None:
        self._rules.append(rule)

    def check_readiness(self, manuscript_id: int) -> Dict[str, Any]:
        """Run all checks and return the pre-submission gate result."""
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        blocking_issues: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        for rule in self._rules:
            hit = rule.evaluate(manuscript, self.db)
            if hit is None:
                continue
            if hit["severity"] == "critical":
                blocking_issues.append(hit)
            else:
                warnings.append(hit)

        components = self._compute_readiness_components(manuscript)
        readiness_score = self._weighted_readiness(components)

        ready_to_submit = len(blocking_issues) == 0 and readiness_score >= self.readiness_threshold

        return {
            "manuscript_id": manuscript.id,
            "title": manuscript.title,
            "journal_id": manuscript.journal_id,
            "readiness_score": round(readiness_score, 1),
            "ready_to_submit": ready_to_submit,
            "blocking_issues": blocking_issues,
            "warnings": warnings,
            "components": components,
        }

    def _compute_readiness_components(self, manuscript: Manuscript) -> List[Dict[str, Any]]:
        overall = manuscript.overall_compliance_score or 0.0
        mandatory = manuscript.mandatory_compliance_score or 0.0
        analysis_ok = manuscript.analysis_status == AnalysisStatus.COMPLETED

        components = [
            {"factor": "overall_compliance", "score": overall},
            {"factor": "mandatory_compliance", "score": mandatory},
            {"factor": "analysis_complete", "score": 100.0 if analysis_ok else 0.0},
        ]

        risks: List[Dict] = []
        if manuscript.rejection_risks:
            try:
                risks = json.loads(manuscript.rejection_risks)
            except json.JSONDecodeError:
                risks = []
        high_risk_count = sum(1 for r in risks if r.get("severity") in ("high", "critical"))
        risk_penalty = min(high_risk_count * 5.0, 20.0)
        components.append({"factor": "rejection_risk_adjustment", "score": max(0.0, 100.0 - risk_penalty)})
        return components

    def _weighted_readiness(self, components: List[Dict[str, Any]]) -> float:
        weights = {
            "overall_compliance": 0.30,
            "mandatory_compliance": 0.35,
            "analysis_complete": 0.15,
            "rejection_risk_adjustment": 0.20,
        }
        total, weight_sum = 0.0, 0.0
        for comp in components:
            w = weights.get(comp["factor"], 0.0)
            total += comp["score"] * w
            weight_sum += w
        return (total / weight_sum) if weight_sum > 0 else 0.0

    def create_final_version(self, manuscript_id: int, change_summary: str = "") -> Dict[str, Any]:
        """Attempt to create a final submitted version. Must pass gate first."""
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        gate_result = self.check_readiness(manuscript_id)
        if not gate_result["ready_to_submit"]:
            return {
                "manuscript_id": manuscript.id,
                "version_id": None,
                "ready_to_submit": False,
                "blocking_issues": gate_result["blocking_issues"],
                "message": "Blocking issues prevent final version creation. Resolve all critical issues before submitting.",
            }

        latest = (
            self.db.query(ManuscriptVersion)
            .filter(ManuscriptVersion.manuscript_id == manuscript_id)
            .order_by(ManuscriptVersion.version.desc())
            .first()
        )
        next_version = (latest.version + 1) if latest else 1
        content_hash = str(abs(hash(f"{manuscript.id}:{manuscript.overall_compliance_score}")) & 0xFFFFFFFF)

        final = ManuscriptVersion(
            manuscript_id=manuscript.id,
            version=next_version,
            content_path=f"final/v{next_version}",
            content_hash=content_hash,
            change_summary=change_summary or f"Final version for submission (v{next_version})",
            provenance=json.dumps({
                "readiness_score": gate_result["readiness_score"],
                "blocking_issues_count": len(gate_result["blocking_issues"]),
                "submitted_at": datetime.utcnow().isoformat(),
            }),
        )
        self.db.add(final)
        self.db.commit()
        self.db.refresh(final)

        return {
            "manuscript_id": manuscript.id,
            "version_id": final.id,
            "ready_to_submit": True,
            "blocking_issues": [],
            "message": f"Final version v{next_version} created successfully.",
        }

    def get_evaluation_chain(self, manuscript_id: int) -> List[Dict[str, Any]]:
        """Return evaluation history for a manuscript in chronological order."""
        from app.models.manuscript import ManuscriptVersion
        versions = (
            self.db.query(ManuscriptVersion)
            .filter(ManuscriptVersion.manuscript_id == manuscript_id)
            .order_by(ManuscriptVersion.created_at.asc())
            .all()
        )
        result = []
        for v in versions:
            evaluations = (
                self.db.query(Evaluation)
                .filter(Evaluation.manuscript_version_id == v.id)
                .order_by(Evaluation.created_at.asc())
                .all()
            )
            for e in evaluations:
                issues = self.db.query(EvaluationIssue).filter(EvaluationIssue.evaluation_id == e.id).all()
                result.append({
                    "version_id": v.id,
                    "version": v.version,
                    "evaluation_id": e.id,
                    "scores": {
                        "compliance": e.compliance_score,
                        "scientific": e.scientific_score,
                        "methodology": e.methodology_score,
                        "writing": e.writing_score,
                        "novelty": e.novelty_score,
                        "readiness": e.readiness_score,
                    },
                    "final_status": e.final_status,
                    "created_at": e.created_at.isoformat(),
                    "blocking_issue_count": sum(1 for i in issues if i.is_blocking),
                })
        return result
