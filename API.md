# API Documentation - LARA

**Version:** 0.1.0 (Phase 3)  
**Base URL:** http://localhost:8000

## Health Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness probe |
| GET | /api/v1/health | Versioned health + DB + storage check |

**Example:**
```bash
curl http://localhost:8000/health
# {"status": "ok", "version": "0.1.0"}

curl http://localhost:8000/api/v1/health
# {"status": "ok", "version": "0.1.0", "database": "ok", "storage": "ok"}
```

## Chat Endpoints (Phase 2)

### POST /api/v1/chat
Generate chat completion (non-streaming).

**Request:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is RAG?"}
  ],
  "model": "qwen2.5:3b-instruct",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "RAG (Retrieval-Augmented Generation) is..."
  },
  "model": "qwen2.5:3b-instruct"
}
```

### POST /api/v1/chat/stream
Stream chat completion (Server-Sent Events).

**Request:** Same as `/chat`

**Response:**
```
data: RAG
data:  (Retrieval
data: -Augmented
data:  Generation
data: )
data: ...
data: [DONE]
```

### GET /api/v1/models
List available models.

**Response:**
```json
[
  {"name": "qwen2.5:3b-instruct", "provider": "ollama", "available": true},
  {"name": "nomic-embed-text", "provider": "ollama", "available": true}
]
```

**Example:**
```bash
curl http://localhost:8000/api/v1/models

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Document Endpoints (Phase 3)

### POST /api/v1/documents
Upload a document (PDF, DOCX, TXT).

**Request:** multipart/form-data
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@paper.pdf"
```

**Response:**
```json
{
  "id": 1,
  "file_hash": "a3f5...",
  "filename": "paper.pdf",
  "size_bytes": 524288,
  "document_type": "pdf",
  "processing_status": "PENDING",
  "is_duplicate": false,
  "created_at": "2026-10-03T18:00:00"
}
```

### GET /api/v1/documents
List uploaded documents (paginated).

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 50, max: 100)

**Response:**
```json
{
  "documents": [{"id": 1, "title": "paper.pdf", ...}],
  "total": 10
}
```

### GET /api/v1/documents/{id}
Get document metadata.

### DELETE /api/v1/documents/{id}
Delete document and its file.

### POST /api/v1/documents/{id}/process
Trigger document processing: extract text, metadata, and tables.

**Response:**
```json
{
  "status": "ok",
  "document_id": 1,
  "processing_status": "COMPLETED"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/1/process
```

**Processing includes:**
- Text extraction (PDF/DOCX/TXT)
- Metadata extraction (title, authors, DOI)
- Table extraction (PDF)
- Status updates (PENDING → PROCESSING → COMPLETED/FAILED)

**Features:**
- SHA-256 hash deduplication
- MIME type validation (PDF, DOCX, TXT)
- 20MB size limit
- Automatic file storage
- Automatic metadata extraction
- Automatic chunking (512 words, 50 overlap)
- Automatic embedding generation

## Search Endpoints (Phase 5)

### POST /api/v1/search
Semantic search across document chunks.

**Request:**
```json
{
  "query": "machine learning methods",
  "document_id": 1,
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "machine learning methods",
  "results": [
    {
      "chunk_id": "a3f5d892...",
      "document_id": 1,
      "content": "Machine learning algorithms...",
      "similarity": 0.87,
      "page": null,
      "section": null,
      "source": "chunk_0"
    }
  ],
  "total": 5
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "deep learning", "top_k": 3}'
```

**Requirements:**
- Ollama must be running
- nomic-embed-text model must be available
- Documents must be processed with embeddings

## RAG Endpoints (Phase 6)

### POST /api/v1/rag/ask
Question answering with RAG (Retrieval-Augmented Generation).

**Request:**
```json
{
  "question": "What are the main findings?",
  "document_id": 1,
  "top_k": 5,
  "temperature": 0.7,
  "model": "qwen2.5:3b-instruct"
}
```

**Response:**
```json
{
  "answer": "Based on the provided context, the main findings are... [Source 1]",
  "sources": [
    {
      "source_id": 1,
      "chunk_id": "a3f5...",
      "document_id": 1,
      "document_title": "Research Paper",
      "similarity": 0.89,
      "content_preview": "The study found that..."
    }
  ],
  "context_used": 5,
  "model": "qwen2.5:3b-instruct",
  "question": "What are the main findings?"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What methodology was used?",
    "top_k": 3,
    "temperature": 0.5
  }'
```

### POST /api/v1/rag/ask/stream
Streaming RAG question answering.

Returns Server-Sent Events with answer chunks.

**Requirements:**
- Ollama running
- qwen2.5:3b-instruct (or specified model)
- nomic-embed-text for embeddings
- Documents processed with chunks and embeddings

**Features:**
- Context retrieval via semantic search
- Source citations in answers
- Configurable context size (top_k)
- Temperature control
- Document filtering

## Journal Endpoints (Phase 7)

### POST /api/v1/journals/load
Load journal profiles from YAML files in `journals/` directory.

**Response:**
```json
{
  "loaded_count": 1,
  "message": "Successfully loaded 1 journal profile(s)"
}
```

### GET /api/v1/journals
List all journal profiles (paginated).

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 50, max: 100)

**Response:**
```json
{
  "journals": [
    {
      "id": 1,
      "name": "Example Journal",
      "slug": "example-journal",
      "publisher": "Academic Press",
      "issn": "1234-5678",
      "official_url": "https://example.com",
      "author_guidelines_url": "https://example.com/guidelines",
      "scope": "Research in AI and machine learning",
      "reference_style": "APA",
      "created_at": "2026-10-03T18:00:00",
      "updated_at": "2026-10-03T18:00:00"
    }
  ],
  "total": 1
}
```

### GET /api/v1/journals/{slug}
Get detailed journal profile with requirements.

**Response:**
```json
{
  "id": 1,
  "name": "Example Journal",
  "slug": "example-journal",
  "publisher": "Academic Press",
  "issn": "1234-5678",
  "official_url": "https://example.com",
  "author_guidelines_url": "https://example.com/guidelines",
  "scope": "Research in AI and machine learning",
  "reference_style": "APA",
  "article_types": "[\"Research Article\", \"Review\"]",
  "word_limits": "{\"abstract\": 250, \"main\": 8000}",
  "style_guide": "# Style Guide\n\n...",
  "rejection_patterns": "# Common Rejection Patterns\n\n...",
  "requirements": [
    {
      "id": 1,
      "key": "abstract_word_limit",
      "description": "Abstract must be under 250 words",
      "requirement_type": "MANDATORY",
      "evidence_level": "OFFICIAL_REQUIREMENT",
      "value": "250",
      "source_url": "https://example.com/guidelines",
      "source_title": "Author Guidelines",
      "confidence": "high",
      "retrieved_at": "2026-10-01T10:00:00"
    }
  ],
  "created_at": "2026-10-03T18:00:00",
  "updated_at": "2026-10-03T18:00:00"
}
```

### GET /api/v1/journals/{slug}/requirements
Get requirements for a specific journal.

**Query Parameters:**
- `requirement_type`: Filter by type (MANDATORY, RECOMMENDED, QUALITY, WARNING)

**Response:**
```json
[
  {
    "id": 1,
    "key": "abstract_word_limit",
    "description": "Abstract must be under 250 words",
    "requirement_type": "MANDATORY",
    "evidence_level": "OFFICIAL_REQUIREMENT",
    "value": "250",
    "source_url": "https://example.com/guidelines",
    "source_title": "Author Guidelines",
    "confidence": "high",
    "retrieved_at": "2026-10-01T10:00:00"
  }
]
```

**Example:**
```bash
# Load journals from YAML
curl -X POST http://localhost:8000/api/v1/journals/load

# List all journals
curl http://localhost:8000/api/v1/journals

# Get journal details
curl http://localhost:8000/api/v1/journals/example-journal

# Get journal requirements
curl http://localhost:8000/api/v1/journals/example-journal/requirements

# Filter requirements by type
curl "http://localhost:8000/api/v1/journals/example-journal/requirements?requirement_type=MANDATORY"
```

**Journal Profile Structure:**
```
journals/
├── example-journal/
│   ├── profile.yaml          # Journal metadata
│   ├── requirements.yaml     # Submission requirements
│   ├── style-guide.md        # Formatting guidelines
│   └── rejection-patterns.md # Common rejection reasons
```

## Future Endpoints (Phase 9+)
- GET /api/v1/collections — List collections
- Enhanced AI-powered analysis features
- Multi-version manuscript tracking
- Collaborative review workflow

## URL Ingestion Endpoints (Phase 8)

### POST /api/v1/documents/from-url
Ingest academic paper from URL (DOI, arXiv, PubMed, or direct link).

**Request:**
```json
{
  "url": "https://doi.org/10.1038/nature12373",
  "auto_download_pdf": true
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Nanometre-scale thermometry in a living cell",
  "authors": "G. Kucsko, P. C. Maurer, et al.",
  "doi": "10.1038/nature12373",
  "journal": "Nature",
  "year": 2013,
  "source_url": "https://doi.org/10.1038/nature12373",
  "access_status": "open",
  "pdf_downloaded": true,
  "processing_status": "PENDING",
  "created_at": "2026-10-03T22:00:00Z"
}
```

**Access Status Values:**
- `open` - Freely available
- `restricted` - Subscription required
- `paywall` - Explicit paywall detected
- `unknown` - Cannot determine

**Supported URL Formats:**
```bash
# DOI
curl -X POST http://localhost:8000/api/v1/documents/from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "10.1038/nature12373", "auto_download_pdf": true}'

# arXiv
curl -X POST http://localhost:8000/api/v1/documents/from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/1706.03762", "auto_download_pdf": true}'

# PubMed
curl -X POST http://localhost:8000/api/v1/documents/from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://pubmed.ncbi.nlm.nih.gov/23223451/", "auto_download_pdf": false}'
```

**Notes:**
- Uses CrossRef API for DOI lookups (public, no auth)
- Respects paywalls - no authentication bypass
- Downloads PDF only if openly available
- Deduplication via content hash

## Manuscript Endpoints (Phase 8)

### GET /api/v1/manuscripts
List all manuscripts.

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

### POST /api/v1/manuscripts
Create a new manuscript.

**Request:**
```json
{
  "title": "My Research Paper",
  "document_id": 23,
  "journal_id": 5,
  "project_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "title": "My Research Paper",
  "document_id": 23,
  "journal_id": 5,
  "analysis_status": "PENDING",
  "created_at": "2026-10-03T22:00:00Z"
}
```

### POST /api/v1/manuscripts/{id}/analyze
Analyze manuscript compliance against journal requirements.

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
      "details": "Document contains 7,234 words (within limit)"
    },
    {
      "requirement_id": 2,
      "requirement_key": "abstract_required",
      "status": "PASS",
      "confidence": 0.90,
      "details": "Abstract section found"
    }
  ],
  "style_issues": [
    {
      "severity": "WARNING",
      "category": "formatting",
      "message": "Inconsistent citation style detected"
    }
  ],
  "rejection_risks": [
    {
      "risk_level": "LOW",
      "category": "methodology",
      "description": "Limited discussion of limitations"
    }
  ],
  "analyzed_at": "2026-10-03T22:05:00Z"
}
```

### DELETE /api/v1/manuscripts/{id}
Delete a manuscript.

**Response:**
```json
{
  "message": "Manuscript deleted successfully"
}
```

**Example:**
```bash
# Create manuscript
curl -X POST http://localhost:8000/api/v1/manuscripts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Paper",
    "document_id": 23,
    "journal_id": 5
  }'

# Analyze manuscript
curl -X POST http://localhost:8000/api/v1/manuscripts/1/analyze

# List manuscripts
curl http://localhost:8000/api/v1/manuscripts

# Delete manuscript
curl -X DELETE http://localhost:8000/api/v1/manuscripts/1
```
