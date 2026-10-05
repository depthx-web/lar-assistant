"""Journal Style Analyzer - Phase 10: LLM-based analysis."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.journal import Journal, JournalRequirement, JournalSource, JournalStyleProfile
from app.models.document import Document, ProcessingStatus
from app.ai.registry import get_provider_class

logger = logging.getLogger(__name__)

# Prompt template for style analysis
STYLE_ANALYSIS_PROMPT = """You are an academic writing style expert analyzing journal publications.

Analyze the following {paper_count} published papers from a scientific journal and extract their writing style profile.

PAPERS:
{papers}

Extract the following style dimensions and return ONLY valid JSON (no markdown, no explanation):
{{
  "structure": "string - paper structure type: IMRaD, Structured, Narrative, etc.",
  "section_order": ["array of section names in order"],
  "paragraph_length_avg": number - average words per paragraph (estimate),
  "paragraph_style": "string: short_concise | medium | long_detailed",
  "sentence_length_avg": number - average words per sentence (estimate),
  "active_voice_ratio": number - 0.0 to 1.0, proportion of active voice,
  "passive_voice_ratio": number - 0.0 to 1.0, proportion of passive voice,
  "voice_preference": "string: active | passive | mixed",
  "tone": "string: formal | informal | neutral | concise",
  "terminology_level": "string: highly_specialized | specialized | intermediate | general",
  "jargon_density": number - 0.0 to 1.0, proportion of specialized terms,
  "citation_style": "string: author_year | numerical | Vancouver, etc.",
  "avg_citations_per_section": number - average citations per section,
  "methods_detail_level": "string: minimal | adequate | detailed | very_detailed",
  "results_style": "string: narrative | table_heavy | mixed | statistics_heavy",
  "discussion_approach": "string: interpretive | conservative | exploratory | balanced"
}}

Return ONLY the JSON object. No markdown formatting."""


@dataclass
class StyleProfile:
    """Structured style profile for a journal."""

    # Structure
    structure: str = ""
    section_order: List[str] = field(default_factory=list)

    # Paragraph organization
    paragraph_length_avg: Optional[float] = None
    paragraph_style: str = ""

    # Sentence analysis
    sentence_length_avg: Optional[float] = None

    # Voice
    active_voice_ratio: Optional[float] = None
    passive_voice_ratio: Optional[float] = None
    voice_preference: str = ""

    # Tone
    tone: str = ""

    # Terminology
    terminology_level: str = ""
    jargon_density: Optional[float] = None

    # Citation behavior
    citation_style: str = ""
    avg_citations_per_section: Optional[float] = None

    # Methodology reporting
    methods_detail_level: str = ""

    # Results reporting
    results_style: str = ""

    # Discussion style
    discussion_approach: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "StyleProfile":
        """Create StyleProfile from dictionary."""
        return cls(
            structure=data.get("structure", ""),
            section_order=data.get("section_order", []),
            paragraph_length_avg=data.get("paragraph_length_avg"),
            paragraph_style=data.get("paragraph_style", ""),
            sentence_length_avg=data.get("sentence_length_avg"),
            active_voice_ratio=data.get("active_voice_ratio"),
            passive_voice_ratio=data.get("passive_voice_ratio"),
            voice_preference=data.get("voice_preference", ""),
            tone=data.get("tone", ""),
            terminology_level=data.get("terminology_level", ""),
            jargon_density=data.get("jargon_density"),
            citation_style=data.get("citation_style", ""),
            avg_citations_per_section=data.get("avg_citations_per_section"),
            methods_detail_level=data.get("methods_detail_level", ""),
            results_style=data.get("results_style", ""),
            discussion_approach=data.get("discussion_approach", ""),
        )


class StyleAnalyzer:
    """Analyze published papers to extract journal style profile using LLM."""

    def __init__(self, db: Optional[Session] = None, model_provider: Optional[str] = None):
        self.db = db
        self.model_provider = model_provider or "ollama"
        self.profiles: dict[str, StyleProfile] = {}

    def analyze_from_papers(
        self,
        journal_slug: str,
        paper_texts: List[str],
        model_provider: Optional[str] = None,
    ) -> StyleProfile:
        """Extract style profile from paper texts using LLM."""
        provider_name = model_provider or self.model_provider

        try:
            provider_cls = get_provider_class(provider_name)
            provider = provider_cls()

            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_text = loop.run_until_complete(
                    provider.generate(
                        prompt=self._build_analysis_prompt(len(paper_texts), paper_texts),
                        temperature=0.3,
                        max_tokens=1000,
                    )
                )
            finally:
                loop.close()

            profile = self._parse_llm_response(response_text, journal_slug, len(paper_texts), provider_name)

            if self.db:
                self._persist_profile(journal_slug, profile, len(paper_texts), provider_name)

            logger.info(f"Analyzed style profile for journal {journal_slug} using {provider_name}")
            return profile

        except Exception as e:
            logger.warning(f"LLM-based analysis failed for {journal_slug}: {e}. Using fallback.")
            return self._get_fallback_profile(journal_slug)

    def _build_analysis_prompt(self, paper_count: int, paper_texts: List[str]) -> str:
        """Build the analysis prompt with paper texts."""
        truncated_papers = []
        for i, text in enumerate(paper_texts[:10], 1):
            truncated = text[:2000] if len(text) > 2000 else text
            truncated_papers.append(f"PAPER {i}:\n{truncated}\n")

        return STYLE_ANALYSIS_PROMPT.format(
            paper_count=paper_count,
            papers="\n\n".join(truncated_papers),
        )

    def _parse_llm_response(self, response: str, journal_slug: str, paper_count: int, provider: str) -> StyleProfile:
        """Parse LLM response into StyleProfile."""
        try:
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                response = "\n".join(lines)

            data = json.loads(response)
            profile = StyleProfile.from_dict(data)

            if profile.active_voice_ratio is not None and profile.passive_voice_ratio is not None:
                total = profile.active_voice_ratio + profile.passive_voice_ratio
                if total > 0:
                    profile.active_voice_ratio = round(profile.active_voice_ratio / total, 2)
                    profile.passive_voice_ratio = round(profile.passive_voice_ratio / total, 2)

            if profile.active_voice_ratio is not None and profile.passive_voice_ratio is not None:
                if profile.active_voice_ratio > 0.6:
                    profile.voice_preference = "active"
                elif profile.passive_voice_ratio > 0.6:
                    profile.voice_preference = "passive"
                else:
                    profile.voice_preference = "mixed"

            self.profiles[journal_slug] = profile
            return profile

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_fallback_profile(journal_slug)

    def _get_fallback_profile(self, journal_slug: str) -> StyleProfile:
        """Return fallback IMRaD profile when LLM fails."""
        profile = StyleProfile(
            structure="IMRaD",
            section_order=["Introduction", "Methods", "Results", "Discussion"],
            tone="formal",
            citation_style="author_year",
            active_voice_ratio=0.6,
            passive_voice_ratio=0.4,
            voice_preference="active",
            paragraph_style="medium",
            terminology_level="specialized",
            methods_detail_level="detailed",
            results_style="mixed",
            discussion_approach="balanced",
        )
        self.profiles[journal_slug] = profile
        return profile

    def _persist_profile(
        self,
        journal_slug: str,
        profile: StyleProfile,
        paper_count: int,
        provider: str,
    ) -> None:
        """Persist style profile to database (keeps history)."""
        journal = self.db.query(Journal).filter(Journal.slug == journal_slug).first()
        if not journal:
            logger.warning(f"Journal {journal_slug} not found for profile persistence")
            return

        style_profile = JournalStyleProfile(
            journal_id=journal.id,
            profile_json=json.dumps(profile.to_dict(), ensure_ascii=False),
            analyzed_at=datetime.utcnow(),
            analyzed_by=provider,
            paper_count=paper_count,
        )
        self.db.add(style_profile)
        self.db.commit()
        logger.info(f"Persisted style profile for journal {journal_slug}")

    def analyze_batch(
        self,
        journal_slugs: List[str],
        paper_texts_map: Optional[Dict[str, List[str]]] = None,
        model_provider: Optional[str] = None,
    ) -> Dict[str, StyleProfile]:
        """Analyze style profiles for multiple journals at once."""
        results = {}
        for slug in journal_slugs:
            papers = paper_texts_map.get(slug, []) if paper_texts_map else []
            results[slug] = self.analyze_from_papers(
                journal_slug=slug,
                paper_texts=papers,
                model_provider=model_provider,
            )
        return results

    def fetch_papers_for_journal(
        self,
        journal_slug: str,
        max_papers: int = 10,
    ) -> List[str]:
        """Fetch paper texts from the document store for a journal.

        Looks up documents whose journal name matches (case-insensitive)
        the journal's name and returns their content.
        """
        if not self.db:
            return []

        journal = self.db.query(Journal).filter(Journal.slug == journal_slug).first()
        if not journal or not journal.name:
            return []

        # Query documents matching this journal by name
        docs = (
            self.db.query(Document)
            .filter(
                Document.journal.isnot(None),
                Document.journal.ilike(f"%{journal.name}%"),
                Document.processing_status == ProcessingStatus.COMPLETED.value,
            )
            .limit(max_papers)
            .all()
        )

        # Extract text from chunks
        texts: List[str] = []
        for doc in docs:
            if doc.chunks:
                full_text = "\n\n".join(c.content for c in doc.chunks)
                if full_text.strip():
                    texts.append(full_text)
            elif doc.doc_metadata:
                try:
                    meta = json.loads(doc.doc_metadata)
                    if meta.get("abstract"):
                        texts.append(meta["abstract"])
                except (json.JSONDecodeError, KeyError):
                    pass

        return texts

    def get_profile(self, journal_slug: str) -> Optional[StyleProfile]:
        """Get stored style profile from database or cache."""
        if journal_slug in self.profiles:
            return self.profiles[journal_slug]

        if self.db:
            journal = self.db.query(Journal).filter(Journal.slug == journal_slug).first()
            if journal:
                style_profile = (
                    self.db.query(JournalStyleProfile)
                    .filter(JournalStyleProfile.journal_id == journal.id)
                    .order_by(JournalStyleProfile.analyzed_at.desc())
                    .first()
                )
                if style_profile:
                    profile = StyleProfile.from_dict(json.loads(style_profile.profile_json))
                    self.profiles[journal_slug] = profile
                    return profile

        return None

    def get_latest_analysis(self, journal_slug: str) -> Optional[dict]:
        """Get latest analysis metadata."""
        if self.db:
            journal = self.db.query(Journal).filter(Journal.slug == journal_slug).first()
            if journal:
                style_profile = (
                    self.db.query(JournalStyleProfile)
                    .filter(JournalStyleProfile.journal_id == journal.id)
                    .order_by(JournalStyleProfile.analyzed_at.desc())
                    .first()
                )
                if style_profile:
                    return {
                        "analyzed_at": style_profile.analyzed_at.isoformat(),
                        "analyzed_by": style_profile.analyzed_by,
                        "paper_count": style_profile.paper_count,
                    }
        return None

    def get_analysis_history(self, journal_slug: str, limit: int = 10) -> List[dict]:
        """Get analysis history for a journal."""
        if not self.db:
            return []

        journal = self.db.query(Journal).filter(Journal.slug == journal_slug).first()
        if not journal:
            return []

        profiles = (
            self.db.query(JournalStyleProfile)
            .filter(JournalStyleProfile.journal_id == journal.id)
            .order_by(JournalStyleProfile.analyzed_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": p.id,
                "analyzed_at": p.analyzed_at.isoformat(),
                "analyzed_by": p.analyzed_by,
                "paper_count": p.paper_count,
                "profile": StyleProfile.from_dict(json.loads(p.profile_json)).to_dict(),
            }
            for p in profiles
        ]

