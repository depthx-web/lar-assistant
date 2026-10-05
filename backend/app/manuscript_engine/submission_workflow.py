"""Submission workflow engine for Phase 13."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import (
    ExportJob,
    Manuscript,
    ManuscriptComment,
    ManuscriptVersion,
    VersionTag,
)
from app.manuscript_engine.gate import PreSubmissionGate
from app.manuscript_engine.version_diff import VersionDiffEngine

logger = logging.getLogger(__name__)


class SubmissionWorkflow:
    """Track submission state and workflow across versions."""

    def __init__(self, db: Session):
        self.db = db

    def get_submission_status(self, manuscript_id: int) -> Dict[str, Any]:
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        gate = PreSubmissionGate(self.db)
        try:
            gate_result = gate.check_readiness(manuscript_id)
            gate_ready = gate_result["ready_to_submit"]
            gate_score = gate_result["readiness_score"]
            blocking_count = len(gate_result["blocking_issues"])
        except Exception:
            gate_ready = False
            gate_score = None
            blocking_count = 0

        submitted_version = (
            self.db.query(ManuscriptVersion)
            .filter(
                ManuscriptVersion.manuscript_id == manuscript_id,
                ManuscriptVersion.provenance.isnot(None),
            )
            .order_by(ManuscriptVersion.version.desc())
            .first()
        )

        provenance = None
        submitted_at = None
        if submitted_version and submitted_version.provenance:
            try:
                provenance = json.loads(submitted_version.provenance)
                submitted_at = provenance.get("submitted_at")
            except Exception:
                pass

        return {
            "manuscript_id": manuscript.id,
            "title": manuscript.title,
            "journal_id": manuscript.journal_id,
            "is_submitted": submitted_version is not None,
            "submission_version_id": submitted_version.id if submitted_version else None,
            "submitted_at": submitted_at,
            "gate_ready": gate_ready,
            "gate_score": gate_score,
            "blocking_issues_count": blocking_count,
        }

    def submit_manuscript(
        self,
        manuscript_id: int,
        change_summary: str = "",
        label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a final submitted version via the pre-submission gate."""
        from app.manuscript_engine.gate import PreSubmissionGate
        gate = PreSubmissionGate(self.db)

        result = gate.create_final_version(manuscript_id, change_summary=change_summary)
        if not result["ready_to_submit"]:
            return result

        # Optionally add a label tag
        if label:
            collab = __import__("app.manuscript_engine.tagging_collab", fromlist=["TaggingAndCollaborationEngine"]).TaggingAndCollaborationEngine(self.db)
            try:
                collab.add_tag(
                    manuscript_id=manuscript_id,
                    tag_name=label,
                    is_baseline=False,
                    label=label,
                )
            except Exception as e:
                logger.warning("Failed to add label tag: %s", e)

        return result

    def run_diff(
        self,
        manuscript_id: int,
        from_version: int,
        to_version: int,
    ) -> Dict[str, Any]:
        diff_engine = VersionDiffEngine(self.db)
        diff = diff_engine.diff_versions(manuscript_id, from_version, to_version)
        return diff_engine.diff_to_dict(diff)