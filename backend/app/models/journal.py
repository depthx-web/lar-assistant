"""Journal profiles, their requirements, sources and style profiles."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import iso, utcnow


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    issn: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_guidelines_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_style: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    article_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    word_limits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON dict
    style_guide: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_patterns: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    requirements: Mapped[List["JournalRequirement"]] = relationship(
        back_populates="journal", cascade="all, delete-orphan", order_by="JournalRequirement.id"
    )
    sources: Mapped[List["JournalSource"]] = relationship(
        back_populates="journal", cascade="all, delete-orphan"
    )
    style_profiles: Mapped[List["JournalStyleProfile"]] = relationship(
        back_populates="journal", cascade="all, delete-orphan"
    )


class JournalRequirement(Base):
    __tablename__ = "journal_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    requirement_type: Mapped[str] = mapped_column(String(32), nullable=False, default="mandatory")
    evidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    retrieved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    journal: Mapped[Journal] = relationship(back_populates="requirements")

    def to_dict(self) -> dict:
        return {
            "id": self.id, "journal_id": self.journal_id, "key": self.key,
            "description": self.description, "requirement_type": self.requirement_type,
            "evidence_level": self.evidence_level, "value": self.value,
            "source_url": self.source_url, "source_title": self.source_title,
            "confidence": self.confidence, "retrieved_at": iso(self.retrieved_at),
        }


class JournalSource(Base):
    __tablename__ = "journal_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    journal: Mapped[Journal] = relationship(back_populates="sources")


class JournalStyleProfile(Base):
    __tablename__ = "journal_style_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    paper_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    analyzed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    journal: Mapped[Journal] = relationship(back_populates="style_profiles")