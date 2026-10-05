"""Version diff analysis engine for Phase 13."""
from __future__ import annotations

import difflib
import logging
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import ManuscriptVersion

logger = logging.getLogger(__name__)


@dataclass
class DiffHunk:
    """A single diff segment."""
    old_start: int
    new_start: int
    old_lines: List[str] = field(default_factory=list)
    new_lines: List[str] = field(default_factory=list)
    op: str = "equal"  # "equal", "delete", "insert", "change"


@dataclass
class VersionDiff:
    """Result of comparing two manuscript versions."""
    from_version: int
    to_version: int
    from_hash: str
    to_hash: str
    line_count_old: int = 0
    line_count_new: int = 0
    additions: int = 0
    deletions: int = 0
    hunks: List[DiffHunk] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class VersionDiffEngine:
    """Compare two manuscript versions and produce structured diff output."""

    def __init__(self, db: Session):
        self.db = db

    def _load_text(self, version: ManuscriptVersion) -> str:
        """Try to load text content from version or document."""
        if version.content_path:
            path = version.content_path
            if not path.startswith("/"):
                base = __import__("app.main", fromlist=["settings"]).__dict__
                try:
                    from app.core.config import settings
                    import os
                    full = os.path.join(settings.resolved_storage_root, path)
                    if os.path.isfile(full):
                        with open(full, "r", encoding="utf-8") as f:
                            return f.read()
                except Exception:
                    pass
        return f"[version {version.version} content not available]"

    def diff_versions(
        self,
        manuscript_id: int,
        from_version: int,
        to_version: int,
    ) -> VersionDiff:
        """Compare two versions of a manuscript."""
        v_old = (
            self.db.query(ManuscriptVersion)
            .filter(
                ManuscriptVersion.manuscript_id == manuscript_id,
                ManuscriptVersion.version == from_version,
            )
            .first()
        )
        v_new = (
            self.db.query(ManuscriptVersion)
            .filter(
                ManuscriptVersion.manuscript_id == manuscript_id,
                ManuscriptVersion.version == to_version,
            )
            .first()
        )
        if not v_old or not v_new:
            raise ValueError(f"Versions {from_version} and {to_version} not found for manuscript {manuscript_id}")

        text_old = self._load_text(v_old)
        text_new = self._load_text(v_new)

        lines_old = text_old.splitlines()
        lines_new = text_new.splitlines()

        matcher = difflib.SequenceMatcher(None, lines_old, lines_new, autojunk=False)
        opcodes = matcher.get_opcodes()

        hunks: List[DiffHunk] = []
        additions = 0
        deletions = 0

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                continue
            elif tag == "replace":
                hunks.append(DiffHunk(
                    old_start=i1 + 1, new_start=j1 + 1,
                    old_lines=lines_old[i1:i2], new_lines=lines_new[j1:j2],
                    op="change",
                ))
                deletions += i2 - i1
                additions += j2 - j1
            elif tag == "delete":
                hunks.append(DiffHunk(
                    old_start=i1 + 1, new_start=j1 + 1,
                    old_lines=lines_old[i1:i2],
                    op="delete",
                ))
                deletions += i2 - i1
            elif tag == "insert":
                hunks.append(DiffHunk(
                    old_start=i1 + 1, new_start=j1 + 1,
                    new_lines=lines_new[j1:j2],
                    op="insert",
                ))
                additions += j2 - j1

        # Build summary
        summary = {
            "line_changes": {"additions": additions, "deletions": deletions},
            "total_old_lines": len(lines_old),
            "total_new_lines": len(lines_new),
            "net_change": additions - deletions,
            "hunks_count": len(hunks),
        }

        return VersionDiff(
            from_version=from_version,
            to_version=to_version,
            from_hash=v_old.content_hash,
            to_hash=v_new.content_hash,
            line_count_old=len(lines_old),
            line_count_new=len(lines_new),
            additions=additions,
            deletions=deletions,
            hunks=hunks,
            summary=summary,
        )

    def diff_to_dict(self, diff: VersionDiff) -> Dict[str, Any]:
        """Serialize a VersionDiff to a dict for API response."""
        return {
            "from_version": diff.from_version,
            "to_version": diff.to_version,
            "from_hash": diff.from_hash,
            "to_hash": diff.to_hash,
            "line_count_old": diff.line_count_old,
            "line_count_new": diff.line_count_new,
            "additions": diff.additions,
            "deletions": diff.deletions,
            "hunks_count": len(diff.hunks),
            "summary": diff.summary,
            "hunks": [
                {
                    "op": h.op,
                    "old_start": h.old_start,
                    "new_start": h.new_start,
                    "old_lines": h.old_lines,
                    "new_lines": getattr(h, "new_lines", []),
                }
                for h in diff.hunks
            ],
        }