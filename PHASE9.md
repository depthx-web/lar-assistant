# Phase 9: Journal Profiles (Enhanced)

**Status:** COMPLETED  
**Priority:** HIGH  
**Date:** 2026-03-10

---

## Overview

Phase 9 builds on the Foundation laid in Phase 7 (basic journal profiles) by adding:

1. **Journal Update Engine** - Compare and update requirements from external sources
2. **Style Analysis Foundation** - Extract structured style profiles from published papers
3. **Evidence Tracking** - Track source provenance for all requirements

---

## Features Implemented

### 2. Style Analysis Foundation (`app/journal_engine/style_analyzer.py`)

```python
@dataclass
class StyleProfile:
    structure: str
    section_order: List[str]
    tone: str
    citation_style: str
    # + 15+ more fields...

class StyleAnalyzer:
    def analyze_from_papers(journal_slug, paper_texts, model_provider) -> StyleProfile
```

**Phase 9 Placeholder:**
- Returns default IMRaD profile
- Phase 10 will add LLM-based analysis from published papers

### 3. Evidence Tracking

All requirements now track:
- `source_url` - Where the requirement came from
- `source_title` - Human-readable source title
- `evidence_level` - OFFICIAL_REQUIREMENT | OBSERVED_PATTERN | MODEL_ASSESSMENT
- `confidence` - high/medium/low
- `retrieved_at` - When source was fetched
- `last_verified` - Last time requirement was validated

---

## API Endpoints (New)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/journals/{slug}/update/check` | Check requirements from new source |
| POST | `/api/v1/journals/{slug}/update/apply` | Apply confirmed updates |
---

## Testing

```bash
pytest backend/tests/test_journals.py -v
```

### Test Coverage

- ✅ `test_check_update_no_changes` - Verify empty diff when no changes
- ✅ `test_check_update_nonexistent_journal` - Verify 404 response
- ✅ `test_apply_update` - Verify update application
- ✅ `test_apply_update_nonexistent_journal` - Verify 404 response
- ✅ `test_analyze_style` - Verify style analysis
- ✅ `test_analyze_style_nonexistent_journal` - Verify 404 response
- ✅ `test_requirement_change_added` - Unit test for change detection
- ✅ `test_requirement_change_removed` - Unit test
- ✅ `test_requirement_change_changed` - Unit test
- ✅ `test_requirement_change_unchanged` - Unit test
- ✅ `test_journal_update_result_to_dict` - Serialization test
- ✅ `test_style_profile_defaults` - Default values test
- ✅ `test_style_analyzer_placeholder` - Placeholder analysis test

---

## Files Created/Modified

| File | Action |
|------|--------|
| `backend/app/journal_engine/update.py` | Created |
| `backend/app/journal_engine/style_analyzer.py` | Created |
| `backend/app/schemas/journal.py` | Extended |
| `backend/app/api/routes/journals.py` | Extended |
| `backend/tests/test_journals.py` | Rewritten |
| `PHASE9.md` | Created (this file) |

---

## Known Limitations

1. **DB table auto-creation** - `journal_style_profiles` table is created via `Base.metadata.create_all()` on startup, but requires model to be imported first (now fixed via `app.models` import in `main.py`).
2. **No auto-fetch of papers** - Paper texts must be ingested into the document store first via `/api/v1/documents` or `/api/v1/documents/ingest-url`. The `fetch_papers_for_journal()` method matches by journal name.
3. **No conflict resolution** - If two users modify same requirement, last-write-wins.

---

## Next: Phase 10 - Style Analysis

**COMPLETED:** Phase 10 implemented LLM-based style analysis from published papers.

Phase 10 delivers:
1. ✅ LLM-based style extraction using Ollama/OpenAI/Anthropic providers
2. ✅ Structured JSON prompt for style dimension extraction (17 fields)
3. ✅ Database persistence via `JournalStyleProfile` model
4. ✅ API endpoints for analysis, retrieval, and metadata
5. ✅ Fallback IMRaD profile when LLM unavailable
6. ✅ 25 tests covering all functionality