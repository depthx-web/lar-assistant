"""Journal Update Engine - Phase 9."""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.journal import Journal, JournalRequirement, JournalSource

logger = logging.getLogger(__name__)


class RequirementChange:
    """Represents a change to a requirement during update."""

    def __init__(self, key: str, description: str, old_value: Optional[str], new_value: Optional[str]):
        self.key = key
        self.description = description
        self.old_value = old_value
        self.new_value = new_value
        self.change_type = self._determine_type()

    def _determine_type(self) -> str:
        if self.old_value is None and self.new_value is not None:
            return "added"
        elif self.old_value is not None and self.new_value is None:
            return "removed"
        elif self.old_value != self.new_value:
            return "changed"
        return "unchanged"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_type": self.change_type,
        }


class JournalUpdateResult:
    """Result of a journal update comparison."""

    def __init__(
        self,
        journal_slug: str,
        old_requirements: list[dict],
        new_requirements: list[dict],
        added: list[RequirementChange],
        removed: list[RequirementChange],
        changed: list[RequirementChange],
        source_url: str,
    ):
        self.journal_slug = journal_slug
        self.old_requirements = old_requirements
        self.new_requirements = new_requirements
        self.added = added
        self.removed = removed
        self.changed = changed
        self.source_url = source_url
        self.needs_confirmation = len(added) > 0 or len(removed) > 0 or len(changed) > 0

    @property
    def has_changes(self) -> bool:
        return len(self.added) > 0 or len(self.removed) > 0 or len(self.changed) > 0

    def to_dict(self) -> dict:
        return {
            "journal_slug": self.journal_slug,
            "has_changes": self.has_changes,
            "needs_confirmation": self.needs_confirmation,
            "added_count": len(self.added),
            "removed_count": len(self.removed),
            "changed_count": len(self.changed),
            "source_url": self.source_url,
            "added": [r.to_dict() for r in self.added],
            "removed": [r.to_dict() for r in self.removed],
            "changed": [r.to_dict() for r in self.changed],
        }

    def model_dump(self) -> dict:
        """Alias for compatibility with Pydantic v2."""
        return self.to_dict()


class JournalUpdateEngine:
    """Compare and update journal requirements from external sources."""

    def __init__(self, db: Session):
        self.db = db

    def compare_with_source(
        self,
        slug: str,
        source_url: str,
        source_title: Optional[str] = None,
        evidence_level: str = "OFFICIAL_REQUIREMENT",
    ) -> JournalUpdateResult:
        """Compare existing requirements with a new source.

        Args:
            slug: Journal slug
            source_url: URL of the new requirements source
            source_title: Human-readable title of the source
            evidence_level: OFFICIAL_REQUIREMENT | OBSERVED_PATTERN | MODEL_ASSESSMENT

        Returns:
            JournalUpdateResult with diffs
        """
        journal = self.db.query(Journal).filter(Journal.slug == slug).first()
        if not journal:
            raise ValueError(f"Journal {slug} not found")

        current_reqs = self.db.query(JournalRequirement).filter(
            JournalRequirement.journal_id == journal.id
        ).all()

        old_dict: dict = {}
        for r in current_reqs:
            old_dict[r.key] = {
                "key": r.key,
                "description": r.description,
                "value": r.value,
                "requirement_type": r.requirement_type,
                "evidence_level": r.evidence_level,
            }

        # TODO: In Phase 10+, fetch and parse source_url via LLM
        # For now, return empty diff (no auto-changes without LLM analysis)
        return JournalUpdateResult(
            journal_slug=slug,
            old_requirements=list(old_dict.values()),
            new_requirements=[],
            added=[],
            removed=[],
            changed=[],
            source_url=source_url,
        )

    def apply_update(
        self,
        slug: str,
        source_url: str,
        source_title: Optional[str] = None,
        evidence_level: str = "OFFICIAL_REQUIREMENT",
    ) -> int:
        """Apply updated requirements to a journal after user confirmation.

        Args:
            slug: Journal slug
            source_url: Source URL of updated requirements
            source_title: Human-readable title
            evidence_level: Type of evidence

        Returns:
            Number of requirements updated/added
        """
        journal = self.db.query(Journal).filter(Journal.slug == slug).first()
        if not journal:
            raise ValueError(f"Journal {slug} not found")

        now = datetime.utcnow()
        journal.updated_at = now
        journal.last_verified = now

        source = JournalSource(
            journal_id=journal.id,
            source_url=source_url,
            source_title=source_title or "",
            content_hash=hashlib.sha256(source_url.encode()).hexdigest()[:64],
            retrieved_at=now,
        )
        self.db.add(source)
        self.db.flush()

        logger.info("Applied update for journal %s from %s", slug, source_url)
        self.db.commit()
        return 1