"""Tagging and collaboration engine for Phase 13."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.manuscript import Manuscript, ManuscriptComment, VersionTag

logger = logging.getLogger(__name__)


class TaggingAndCollaborationEngine:
    """Manage version tags and collaboration comments."""

    def __init__(self, db: Session):
        self.db = db

    # ─── Version Tags ───────────────────────────────────────────────────────

    def add_tag(
        self,
        manuscript_id: int,
        tag_name: str,
        version_id: Optional[int] = None,
        label: Optional[str] = None,
        is_baseline: bool = False,
    ) -> VersionTag:
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        if is_baseline:
            self.db.query(VersionTag).filter(
                VersionTag.manuscript_id == manuscript_id,
                VersionTag.is_baseline == True,
            ).update({"is_baseline": False})

        tag = VersionTag(
            manuscript_id=manuscript_id,
            version_id=version_id,
            tag_name=tag_name,
            label=label,
            is_baseline=is_baseline,
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def list_tags(self, manuscript_id: int) -> List[VersionTag]:
        return (
            self.db.query(VersionTag)
            .filter(VersionTag.manuscript_id == manuscript_id)
            .order_by(VersionTag.created_at.asc())
            .all()
        )

    def delete_tag(self, tag_id: int, manuscript_id: int) -> bool:
        tag = (
            self.db.query(VersionTag)
            .filter(VersionTag.id == tag_id, VersionTag.manuscript_id == manuscript_id)
            .first()
        )
        if not tag:
            return False
        self.db.delete(tag)
        self.db.commit()
        return True

    # ─── Comments ───────────────────────────────────────────────────────────

    def add_comment(
        self,
        manuscript_id: int,
        author: str,
        content: str,
        version_id: Optional[int] = None,
        line_number: Optional[int] = None,
    ) -> ManuscriptComment:
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        comment = ManuscriptComment(
            manuscript_id=manuscript_id,
            version_id=version_id,
            author=author,
            content=content,
            line_number=line_number,
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(
        self,
        manuscript_id: int,
        version_id: Optional[int] = None,
        unresolved_only: bool = False,
    ) -> List[ManuscriptComment]:
        q = self.db.query(ManuscriptComment).filter(
            ManuscriptComment.manuscript_id == manuscript_id
        )
        if version_id is not None:
            q = q.filter(ManuscriptComment.version_id == version_id)
        if unresolved_only:
            q = q.filter(ManuscriptComment.is_resolved == False)
        return q.order_by(ManuscriptComment.created_at.asc()).all()

    def resolve_comment(self, comment_id: int, manuscript_id: int) -> bool:
        comment = (
            self.db.query(ManuscriptComment)
            .filter(ManuscriptComment.id == comment_id, ManuscriptComment.manuscript_id == manuscript_id)
            .first()
        )
        if not comment:
            return False
        comment.is_resolved = True
        self.db.commit()
        return True

    def get_comment_stats(self, manuscript_id: int) -> Dict[str, Any]:
        total = self.db.query(ManuscriptComment).filter(
            ManuscriptComment.manuscript_id == manuscript_id
        ).count()
        unresolved = self.db.query(ManuscriptComment).filter(
            ManuscriptComment.manuscript_id == manuscript_id,
            ManuscriptComment.is_resolved == False,
        ).count()
        return {"total": total, "unresolved": unresolved}
