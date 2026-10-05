# Phase 13: Multi-Version Comparison, Export & Submission Workflow

**Status:** ✅ Complete (45 tests passing)

---

## Overview

Phase 13 extends the LAR Assistant with **multi-version comparison**, **collaboration features**, **export functionality**, and a **submission workflow**. These capabilities allow researchers to track changes across manuscript versions, collaborate with co-authors, export to multiple formats, and manage the submission process through a structured workflow.

---

## Features Implemented

### 1. Version Diff Analysis

**File:** `app/manuscript_engine/version_diff.py`

Structural diff between any two manuscript versions using Python's `difflib`:

- Line-by-line comparison producing `DiffHunk` objects (insert/delete/change)
- Summary statistics: additions, deletions, net change, total lines
- Serialized output for API responses

**API:** `GET /api/v1/manuscripts/{id}/diff?from_version=N&to_version=M`

### 2. Version Tagging

**File:** `app/manuscript_engine/tagging_collab.py`

Tag and label manuscript versions for easy tracking:

- Create named tags (`v1-draft`, `v2-final`, `review-complete`)
- Mark baseline versions for comparison
- Delete tags
- Automatic baseline flag management (only one baseline per manuscript)

**API:**
- `GET /api/v1/manuscripts/{id}/tags`
- `POST /api/v1/manuscripts/{id}/tags`
- `DELETE /api/v1/manuscripts/{id}/tags/{tag_id}`

### 3. Collaboration Comments

**File:** `app/manuscript_engine/tagging_collab.py`

Threaded comments on manuscript versions:

- Add comments with author, content, and optional line number
- Filter by version or unresolved status
- Resolve/unresolve comments
- Comment statistics (total, unresolved count)

**API:**
- `GET /api/v1/manuscripts/{id}/comments?version_id=N&unresolved_only=true`
- `POST /api/v1/manuscripts/{id}/comments`
- `POST /api/v1/manuscripts/{id}/comments/{comment_id}/resolve`
- `GET /api/v1/manuscripts/{id}/comments/stats`

### 4. Export Engine

**File:** `app/manuscript_engine/export_engine.py`

Generate manuscript exports in multiple formats:

- **Markdown** — Section headers extracted from content
- **LaTeX** — Full document with `\section{}` commands
- **Plain text** — Raw content extraction

Supports async export jobs with status tracking.

**API:**
- `POST /api/v1/manuscripts/{id}/export` — Create export job
- `POST /api/v1/manuscripts/{id}/export/{job_id}/run` — Execute export
- `GET /api/v1/manuscripts/{id}/exports` — List export history

### 5. Submission Workflow

**File:** `app/manuscript_engine/submission_workflow.py`

End-to-end submission management:

- Check submission status (gate readiness, submission history)
- Submit manuscript via gate (creates final version)
- Optional labeling on submission
- Full integration with Phase 12 pre-submission gate

**API:**
- `GET /api/v1/manuscripts/{id}/submission/status`
- `POST /api/v1/manuscripts/{id}/submission`

---

## Database Models

**File:** `app/models/manuscript.py`

| Model | Table | Purpose |
|-------|-------|---------|
| `VersionTag` | `version_tags` | Named labels for manuscript versions |
| `ManuscriptComment` | `manuscript_comments` | Collaboration comments |
| `ExportJob` | `export_jobs` | Export job tracking |

---

## API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/manuscripts/{id}/tags` | List version tags |
| `POST` | `/manuscripts/{id}/tags` | Create version tag |
| `DELETE` | `/manuscripts/{id}/tags/{tag_id}` | Delete tag |
| `GET` | `/manuscripts/{id}/comments` | List comments |
| `POST` | `/manuscripts/{id}/comments` | Add comment |
| `POST` | `/manuscripts/{id}/comments/{id}/resolve` | Resolve comment |
| `GET` | `/manuscripts/{id}/comments/stats` | Comment statistics |
| `GET` | `/manuscripts/{id}/diff` | Version diff |
| `POST` | `/manuscripts/{id}/export` | Create export job |
| `POST` | `/manuscripts/{id}/export/{job_id}/run` | Run export |
| `GET` | `/manuscripts/{id}/exports` | List exports |
| `GET` | `/manuscripts/{id}/submission/status` | Submission status |
| `POST` | `/manuscripts/{id}/submission` | Submit manuscript |

---

## Tests

**File:** `tests/test_phase13.py` — 45 tests covering:

- **Tags (7):** add, list, delete, baseline management, not-found
- **Comments (7):** add, list, filter, resolve, stats, not-found
- **Diff (5):** empty content, different content, same content, missing, serialization
- **Export (6):** create job, bad format, missing manuscript, run markdown/text/latex, list
- **Submission (5):** status ready/pending/missing, submit ready/blocked
- **API (15):** End-to-end tests for all endpoints

---

## Files Created/Modified

| Action | File |
|--------|------|
| Created | `app/manuscript_engine/version_diff.py` |
| Created | `app/manuscript_engine/tagging_collab.py` |
| Created | `app/manuscript_engine/export_engine.py` |
| Created | `app/manuscript_engine/submission_workflow.py` |
| Created | `app/schemas/phase13.py` |
| Created | `app/api/routes/phase13.py` |
| Created | `tests/test_phase13.py` |
| Modified | `app/models/manuscript.py` (+3 models) |
| Modified | `app/models/__init__.py` |
| Modified | `app/manuscript_engine/__init__.py` |
| Modified | `app/api/routes/__init__.py` |