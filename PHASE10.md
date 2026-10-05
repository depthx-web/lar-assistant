# Phase 10: LLM-Based Style Analysis

**Status:** COMPLETED ✅
**Priority:** HIGH
**Date:** 2026-03-10
**Previous:** Phase 9 (Journal Profiles)

---

## Overview

Phase 10 replaces the Phase 9 placeholder style analysis with actual LLM-based extraction from published papers. The `StyleAnalyzer` now attempts to use the configured LLM provider (Ollama/OpenAI/Anthropic) to analyze journal publication style and falls back to a sensible IMRaD default when LLM is unavailable.

---

## Features Implemented

### 1. LLM-Based Style Extraction (`app/journal_engine/style_analyzer.py`)

The `StyleAnalyzer` class now:

- Attempts LLM-based analysis using the configured provider
- Sends paper texts (first 2000 chars, up to 10 papers) to the LLM
- Extracts structured style dimensions from JSON response
- Normalizes voice ratios and calculates voice preference
- Falls back to IMRaD default profile on failure
- Persists analysis results to `journal_style_profiles` table

**Prompt Template:** Structured JSON extraction with 17 style dimensions:
- Structure type (IMRaD, Structured, Narrative, etc.)
- Section order
- Paragraph and sentence length statistics
- Voice ratios (active/passive)
- Tone and terminology level
- Citation style
- Methods/results/discussion reporting styles

### 2. Database Model for Style Profiles (`app/models/journal.py`)

New model `JournalStyleProfile`:
- Links to journal via foreign key
- Stores analysis as JSON blob
- Tracks analysis metadata (timestamp, provider, paper count)

```python
class JournalStyleProfile(Base):
    __tablename__ = "journal_style_profiles"
    id: Mapped[int]
    journal_id: Mapped[int]
    profile_json: Mapped[str]  # JSON string
    analyzed_at: Mapped[datetime]
    analyzed_by: Mapped[str]   # model name (e.g., "ollama")
    paper_count: Mapped[int]
```

### 3. API Endpoints (`app/api/routes/journals.py`)

Three new/updated endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/journals/{slug}/style/analyze` | POST | Trigger LLM-based style analysis |
| `/journals/{slug}/style/profile` | GET | Get stored style profile |
| `/journals/{slug}/style/analysis-info` | GET | Get analysis metadata |
| `/journals/{slug}/style/history` | GET | Get full analysis history (all runs) |
| `/journals/batch/style/analyze` | POST | Batch analyze multiple journals |
| `/journals/{slug}/style/papers` | GET | Get available paper texts for a journal |

### 4. Tests (`backend/tests/test_journals.py`)

Comprehensive test coverage:
- API endpoint tests (200/404 status codes)
- Fallback profile tests (no LLM available)
- Profile parsing tests (JSON + markdown handling)
- Voice preference calculation tests
- Prompt building tests

---

## Architecture

```
StyleAnalyzer
├── analyze_from_papers()
│   ├── build_analysis_prompt()     # Format papers into prompt
│   ├── provider.generate()          # Call LLM (async via loop)
│   ├── parse_llm_response()        # Extract JSON, validate
│   └── persist_profile()           # Save to DB
├── get_profile()                   # Load from cache/DB
└── get_latest_analysis()           # Return metadata
```

---

## Behavior

### With LLM Available
1. Fetch paper texts (user provides or from journal's documents)
2. Build prompt with paper excerpts
3. Call LLM provider
4. Parse JSON response
5. Normalize voice ratios
6. Calculate voice preference
7. Persist to database
8. Return profile

### Without LLM (Fallback)
Returns sensible defaults:
- Structure: IMRaD
- Section order: Introduction → Methods → Results → Discussion
- Tone: formal
- Citation style: author_year
- Voice: active (60/40 split)
- All other fields: reasonable defaults

---

## Usage

```python
from app.journal_engine.style_analyzer import StyleAnalyzer

# With database persistence
analyzer = StyleAnalyzer(db=session)
profile = analyzer.analyze_from_papers(
    journal_slug="nature-medicine",
    paper_texts=[...],  # List of paper texts
)

# Get stored profile
profile = analyzer.get_profile("nature-medicine")

# Get analysis metadata
info = analyzer.get_latest_analysis("nature-medicine")
# Returns: {"analyzed_at": "...", "analyzed_by": "ollama", "paper_count": 5}
```

---

## Next Steps

All Phase 10 tasks are now complete:

1. ✅ **Database migration** - `JournalStyleProfile` model registered; `create_all()` in lifespan ensures table creation on startup
2. ✅ **Paper ingestion** - `fetch_papers_for_journal()` retrieves texts from document store by matching journal name
3. ✅ **Batch analysis** - `analyze_batch()` supports multiple journals in one call; `POST /journals/batch/style/analyze` endpoint added
4. ✅ **Analysis history** - `get_analysis_history()` tracks all analyses over time; `GET /journals/{slug}/style/history` endpoint added
5. ✅ **Paper retrieval endpoint** - `GET /journals/{slug}/style/papers` returns available paper texts for a journal

Remaining future enhancements:
- Model selection per-journal
- Incremental analysis (only re-analyze when new papers arrive)
- Style similarity comparison between journals

---

## Testing

Run tests:
```bash
pytest backend/tests/test_journals.py -v
```

Expected: 30 passed, 3 skipped (DB table not yet created in test env)

All tests pass with fallback behavior when LLM unavailable.
