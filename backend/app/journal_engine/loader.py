"""Journal profile loader from YAML files."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.journal import Journal, JournalRequirement

logger = logging.getLogger(__name__)


class JournalLoader:
    """Load journal profiles from YAML files."""

    def __init__(self, db: Session):
        """Initialize loader.
        
        Args:
            db: Database session
        """
        self.db = db
        self.journals_dir = Path(settings.project_root) / "journals"

    def load_all(self) -> int:
        """Load all journal profiles from journals/ directory.
        
        Returns:
            Number of journals loaded
        """
        if not self.journals_dir.exists():
            logger.warning(f"Journals directory not found: {self.journals_dir}")
            return 0

        loaded_count = 0
        for journal_dir in self.journals_dir.iterdir():
            if not journal_dir.is_dir():
                continue
            
            profile_file = journal_dir / "profile.yaml"
            if not profile_file.exists():
                logger.debug(f"Skipping {journal_dir.name} - no profile.yaml")
                continue
            
            try:
                self.load_journal(journal_dir)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load journal {journal_dir.name}: {e}")
                continue

        logger.info(f"Loaded {loaded_count} journal profiles")
        return loaded_count

    def load_journal(self, journal_dir: Path) -> Journal:
        """Load a single journal profile.
        
        Args:
            journal_dir: Path to journal directory
        
        Returns:
            Journal object
        """
        profile_file = journal_dir / "profile.yaml"
        requirements_file = journal_dir / "requirements.yaml"
        style_guide_file = journal_dir / "style-guide.md"
        rejection_patterns_file = journal_dir / "rejection-patterns.md"

        # Load profile
        with open(profile_file, encoding="utf-8") as f:
            profile_data = yaml.safe_load(f)

        slug = profile_data.get("slug", journal_dir.name)
        
        # Check if journal already exists
        journal = self.db.query(Journal).filter(Journal.slug == slug).first()
        
        if journal:
            logger.info(f"Updating journal: {slug}")
        else:
            logger.info(f"Creating journal: {slug}")
            journal = Journal(slug=slug)
            self.db.add(journal)

        # Update profile fields
        journal.name = profile_data.get("name", "Unknown Journal")
        journal.publisher = profile_data.get("publisher")
        journal.issn = profile_data.get("issn")
        journal.official_url = profile_data.get("official_url")
        journal.author_guidelines_url = profile_data.get("author_guidelines_url")
        journal.scope = profile_data.get("scope")
        
        # Store complex fields as JSON strings
        import json
        journal.article_types = json.dumps(profile_data.get("article_types", []))
        journal.word_limits = json.dumps(profile_data.get("word_limits", {}))
        journal.reference_style = profile_data.get("reference_style")
        
        # Load style guide
        if style_guide_file.exists():
            journal.style_guide = style_guide_file.read_text(encoding="utf-8")
        
        # Load rejection patterns
        if rejection_patterns_file.exists():
            journal.rejection_patterns = rejection_patterns_file.read_text(encoding="utf-8")

        self.db.flush()  # Get journal.id

        # Load requirements
        if requirements_file.exists():
            self._load_requirements(journal, requirements_file)

        self.db.commit()
        logger.info(f"Journal {slug} loaded successfully")
        
        return journal

    def _load_requirements(self, journal: Journal, requirements_file: Path):
        """Load requirements for a journal.
        
        Args:
            journal: Journal object
            requirements_file: Path to requirements.yaml
        """
        with open(requirements_file, encoding="utf-8") as f:
            requirements_data = yaml.safe_load(f)

        if not requirements_data:
            return

        # Delete existing requirements for this journal
        self.db.query(JournalRequirement).filter(
            JournalRequirement.journal_id == journal.id
        ).delete()

        # Add new requirements
        for req_data in requirements_data:
            requirement = JournalRequirement(
                journal_id=journal.id,
                key=req_data.get("key", "unknown"),
                description=req_data.get("description", ""),
                requirement_type=req_data.get("requirement_type", "RECOMMENDED"),
                evidence_level=req_data.get("evidence_level", "MODEL_ASSESSMENT"),
                value=req_data.get("value"),
                source_url=req_data.get("source_url"),
                source_title=req_data.get("source_title"),
                confidence=req_data.get("confidence", "medium"),
                retrieved_at=self._parse_datetime(req_data.get("retrieved_at")),
            )
            self.db.add(requirement)

        logger.debug(f"Loaded {len(requirements_data)} requirements for {journal.slug}")

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string.
        
        Args:
            dt_str: ISO datetime string
        
        Returns:
            datetime object or None
        """
        if not dt_str:
            return None
        
        try:
            # Handle ISO format with Z
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1] + "+00:00"
            return datetime.fromisoformat(dt_str)
        except Exception as e:
            logger.warning(f"Failed to parse datetime: {dt_str} - {e}")
            return None

