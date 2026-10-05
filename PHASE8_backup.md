# Phase 8: URL Ingestion & Manuscript Compliance

**Status:** ✅ COMPLETED  
**Date:** 2026-10-03  
**Duration:** ~2 hours

## Overview

Phase 8 implements two key features:
1. **URL Ingestion** - Fetch academic papers from URLs (DOI, arXiv, PubMed)
2. **Manuscript Compliance** - Check manuscripts against journal requirements

## Feature 1: URL Ingestion

### Architecture
```
User provides URL
    ↓
URLFetcher detects source type
    ↓
Fetch from appropriate API:
    - CrossRef API (DOI)
    - arXiv API
    - PubMed E-utilities
    - Generic HTML parsing
    ↓
Extract metadata + check access status
    ↓
Download PDF if openly available
    ↓
Create Document record
    ↓
Ready for processing (Phase 4-6)
```

### Components

**URLFetcher** (`backend/app/document_processing/url_fetcher.py`)
- Automatic source detection (DOI, arXiv, PubMed, generic)
- Public API integration (CrossRef, arXiv, PubMed - all free)
- Paywall detection and respect
- PDF download for open access papers
- Content hash generation for deduplication

**API Endpoint** (`POST /api/v1/documents/from-url`)
```json
{
  "url": "https://doi.org/10.1038/nature12373",
  "auto_download_pdf": true
}
```

### Supported Sources

| Source | Input Format | API Used | PDF Available |
|--------|--------------|----------|---------------|
| DOI | `10.xxxx/xxxxx` or `https://doi.org/...` | CrossRef | If open access |
| arXiv | `https://arxiv.org/abs/XXXX.XXXXX` | arXiv API | Always |
| PubMed | `https://pubmed.ncbi.nlm.nih.gov/XXXXXXXX/` | NCBI E-utilities | No |
| Generic | Any URL | HTML parsing | If direct link |

### Access Status Values
- `open` - Paper is freely available
- `restricted` - Behind subscription/authentication
- `paywall` - Explicit paywall detected
- `unknown` - Cannot determine

### Ethical & Legal Compliance
✅ Respects paywalls - No authentication bypass  
✅ Uses public APIs - CrossRef, arXiv, PubMed (all free)  
✅ Downloads only open access - Checks status first  
✅ Transparent about access - Reports status to user  
✅ User Agent identification - Proper API etiquette

1. ✅ Create manuscript models linking documents to target journals
2. ✅ Implement compliance engine for requirement checking
3. ✅ Build manuscript API endpoints (CRUD + analysis)
4. ✅ Integrate with document processing pipeline
5. ✅ Provide detailed compliance reporting

## Architecture

```
Document (uploaded PDF/DOCX)
    ↓
Manuscript (links document + journal)
    ↓
ComplianceEngine
    ↓
Analysis Results:
    - Overall compliance score
    - Mandatory requirement checks
    - Style issues
    - Rejection risks
```

## Database Schema

### Manuscripts Table
```sql
CREATE TABLE manuscripts (
    id INTEGER PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    journal_id INTEGER REFERENCES journals(id),
    project_id INTEGER REFERENCES projects(id),
    document_id INTEGER REFERENCES documents(id),
    
    -- Analysis fields (Phase 8)
    analysis_status VARCHAR(32) DEFAULT 'PENDING',
    overall_compliance_score FLOAT,
    mandatory_compliance_score FLOAT,
    requirement_checks JSON,
    style_issues JSON,
    rejection_risks JSON,
    analyzed_at DATETIME,
    
    current_version INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Requirement Checks Table
```sql
CREATE TABLE requirement_checks (
    id INTEGER PRIMARY KEY,
    manuscript_id INTEGER REFERENCES manuscripts(id) ON DELETE CASCADE,
    journal_requirement_id INTEGER REFERENCES journal_requirements(id),
    status VARCHAR(32) DEFAULT 'UNKNOWN',
    confidence FLOAT,
    details TEXT,
    evidence TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### List Manuscripts
```http
GET /api/v1/manuscripts
```

**Response:**
```json
{
  "manuscripts": [
    {
      "id": 1,
      "title": "Novel Machine Learning Approach",
      "journal_id": 5,
      "document_id": 23,
      "analysis_status": "COMPLETED",
      "overall_compliance_score": 0.85,
      "created_at": "2026-10-03T22:00:00Z"
    }
  ],
  "total": 1
}
```

### Create Manuscript
```http
POST /api/v1/manuscripts
Content-Type: application/json

{
  "title": "My Research Paper",
  "document_id": 23,
  "journal_id": 5,
  "project_id": 1
}
```

### Analyze Manuscript
```http
POST /api/v1/manuscripts/{id}/analyze
```

**Response:**
```json
{
  "id": 1,
  "analysis_status": "COMPLETED",
  "overall_score": 0.85,
  "mandatory_score": 0.90,
  "requirement_checks": [
    {
      "requirement_id": 1,
      "requirement_key": "word_limit_8000",
      "status": "PASS",
      "confidence": 0.95,

## Compliance Engine

### Requirements Checking

The `ComplianceEngine` (`app/manuscript_engine/compliance.py`) checks manuscripts against journal requirements:

**Supported Requirement Types:**
- `WORD_LIMIT` - Document length validation
- `ABSTRACT_REQUIRED` - Abstract section presence
- `KEYWORDS_REQUIRED` - Keywords presence
- `REFERENCES_MIN` - Minimum reference count
- `SECTIONS_REQUIRED` - Required sections (Introduction, Methods, etc.)
- `FIGURES_MAX` - Maximum figure count
- `FUNDING_STATEMENT` - Funding disclosure presence

**Status Values:**
- `PASS` - Requirement met
- `FAIL` - Requirement not met
- `WARNING` - Borderline or needs attention
- `UNKNOWN` - Could not determine
- `NOT_APPLICABLE` - Not relevant to this manuscript

### Analysis Workflow

```python
from app.manuscript_engine.compliance import ComplianceEngine

# Initialize engine
engine = ComplianceEngine(db_session)

# Analyze manuscript
result = engine.analyze_manuscript(manuscript_id)

# Result contains:
# - overall_compliance_score (0.0 - 1.0)
# - mandatory_compliance_score (0.0 - 1.0)
# - requirement_checks (list of check results)
# - style_issues (list of style problems)
# - rejection_risks (list of potential issues)
```

## Testing

### Run Tests
```bash
cd backend
python tests/test_manuscript_workflow.py
```

### Test Workflow
The test performs a complete end-to-end workflow:
1. Upload document
2. Process document (extract text, create chunks)
3. Load journal profiles
4. Create manuscript
5. Analyze manuscript compliance
6. Verify analysis results

### Expected Output
```
============================================================
PHASE 8: MANUSCRIPT ANALYSIS - COMPREHENSIVE TEST
============================================================

[1/6] Uploading test document...
Document uploaded: ID=23

[2/6] Processing document...
Document processed

[3/6] Loading journal profiles...
Loaded 1 journal(s)

[4/6] Fetching journal list...
Found journal: Example Journal of Applied Research (ID=1)

[5/6] Creating manuscript...
Manuscript created: ID=3

[6/6] Analyzing manuscript compliance...

============================================================
ANALYSIS RESULTS
============================================================
Status: COMPLETED
Overall Compliance: 85.0%
Requirements Checked: 5

============================================================
ALL TESTS PASSED - PHASE 8 COMPLETE
============================================================
```

## Files Added/Modified

### New Files
- `backend/app/api/routes/manuscripts.py` - Manuscript API endpoints
- `backend/app/manuscript_engine/compliance.py` - Compliance checking engine
- `backend/app/schemas/manuscript.py` - Pydantic schemas
- `backend/tests/test_manuscript_workflow.py` - Integration tests
- `backend/init_db.py` - Database initialization script
- `backend/check_db.py` - Database inspection utility

### Modified Files
- `backend/app/models/manuscript.py` - Added analysis fields
- `backend/app/api/routes/__init__.py` - Registered manuscripts router
- `backend/app/schemas/__init__.py` - Exported manuscript schemas

## Known Issues & Limitations

### Current Limitations
1. **Basic Rule Checking**: Current compliance engine uses simple pattern matching and counting
2. **Style Issue Detection**: Limited to basic patterns
3. **Rejection Risk Assessment**: Currently placeholder logic

### Future Enhancements
- RAG-based semantic requirement checking
- AI-powered writing style analysis
- Automated improvement suggestions
- Multi-version comparison and tracking

## Troubleshooting

### Database Issues
If you encounter "table does not exist" errors:
```bash
cd backend
python init_db.py  # Recreate tables
```

### Analysis Returns 0% Score
This is normal if:
1. Journal profile has no requirements defined
2. Document has no content (failed processing)

## Success Criteria

Phase 8 is complete when:
- ✅ Manuscripts can be created and linked to documents/journals
- ✅ Compliance engine analyzes requirements
- ✅ API endpoints return proper compliance data
- ✅ Database tables are properly structured
- ✅ Integration tests pass
- ✅ Documentation is complete

---

**Phase 8 Completed:** 2026-10-03  
**Database:** SQLite with all tables initialized  
**Test Status:** All integration tests passing  
**API Status:** All endpoints functional
      "details": "Document contains 7,234 words"
    }
  ],
  "style_issues": [],
  "rejection_risks": []
}
```
