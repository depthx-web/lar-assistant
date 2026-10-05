import pathlib, textwrap, os, json
BASE = pathlib.Path(r"E:\depthx\lar-assistant")
BACKEND = BASE / "backend"
APP = BACKEND / "app"

def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    print(f"WROTE {path.relative_to(BASE)}")

# ─────────────────────────────────────────────────────────────
# pyproject / requirements
# ─────────────────────────────────────────────────────────────
write(BACKEND / "requirements.txt", """
fastapi>=0.110
uvicorn[standard]>=0.30
pydantic>=2.8
pydantic-settings>=2.4
sqlalchemy>=2.0
alembic>=1.13
python-dotenv>=1.0
python-multipart>=0.0.9
httpx>=0.27
pytest>=8
pytest-asyncio>=0.23
anyio>=4
""")

write(BACKEND / "pyproject.toml", """
[project]
name = "lara-backend"
version = "0.1.0"
description = "Local Academic Research Assistant - Backend"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.8",
  "pydantic-settings>=2.4",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "python-dotenv>=1.0",
  "python-multipart>=0.0.9",
  "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
""")

write(BASE / ".env.example", """
# Copy to .env and fill values - NEVER commit .env
# --- Core ---
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
SECRET_KEY=change-me-in-production

# --- Database ---
DATABASE_URL=sqlite:///./data/lara.db
# For Postgres later: postgresql+psycopg://user:pass@localhost/lara

# --- Storage ---
STORAGE_ROOT=./storage
DOCUMENTS_ROOT=./storage/documents
MAX_UPLOAD_MB=100

# --- AI Providers ---
# Leave empty if not used
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:3b-instruct
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# --- RAG ---
EMBEDDING_MODEL=nomic-embed-text
RETRIEVAL_TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=120

# --- OCR ---
OCR_ENABLED=true
OCR_LANGUAGE=eng+ara

# --- Security ---
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
""")

write(BASE / "ARCHITECTURE.md", """
# ARCHITECTURE - LARA

## Layers
```
UI (React/Vite - frontend/)
  |
API (FastAPI - backend/app/api)
  |
Application Services (app/services)
  |
AI Provider Layer (app/ai)  -> LLMProvider abstraction
Document Processing (app/document_processing) -> PDF pipeline
RAG Layer (app/rag) -> vector store + hybrid search
Journal Engine (app/journal_engine) -> profiles + requirements
Manuscript Engine (app/manuscript) -> evaluation + readiness
  |
Database / Storage (SQLite + file storage)
```

## Principles
- Each layer independent, communicates via interfaces.
- No direct coupling to Qwen/Ollama in business logic.
- Journals are data/configuration (YAML/MD), not code.
- Models are Providers (adapter pattern).
- Evidence-first, not LLM-first.

## AI Provider Abstraction
`app/ai/base.py` defines LLMProvider with generate/stream/embed/health_check/list_models.
Implementations: OllamaProvider, OpenAIProvider, AnthropicProvider, LocalTransformersProvider.
Registry: app/ai/registry.py

## Document Pipeline
PDF -> detect -> extract -> OCR if needed -> layout -> metadata -> section detect -> chunk -> embed -> index
Each stage logged, failures isolated.

## RAG
Hybrid (semantic + keyword), filtering by journal/year/author/document/collection, reranking optional.

## Journal / Manuscript
Journal profiles under journals/<name>/ with profile.yaml, requirements.yaml, style-guide.md.
Manuscript engine uses blocking rules (MANDATORY vs RECOMMENDED/QUALITY/WARNING).
""")

write(BASE / "INSTALL.md", """
# INSTALL - LARA (Windows 10/11)

## Prerequisites
- Python 3.11+ (check: py --version)
- Git, PowerShell 5+
- Ollama (optional for Phase 1, required from Phase 2): https://ollama.com/download
- Node 18+ for frontend (optional Phase 1)

## Setup (PowerShell)
```powershell
cd E:\\depthx\\lar-assistant
powershell -ExecutionPolicy Bypass -File setup.ps1
.\.venv\\Scripts\\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --port 8000
# open http://localhost:8000/health and http://localhost:8000/docs
```

## Manual setup
```powershell
py -V:Astral/CPython3.14.7 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
copy .env.example .env
# edit .env if needed
uvicorn app.main:app --app-dir backend --reload --port 8000
```

## Verify
```powershell
pytest backend/tests -v
curl http://localhost:8000/health
```

## Ollama (Phase 2+)
```powershell
ollama serve
ollama pull qwen2.5:3b-instruct
ollama list
```
""")

write(BASE / "CONFIGURATION.md", """
# CONFIGURATION
All config via .env (pydantic-settings). See .env.example.

## Resource Tuning (12GB RAM / CPU only)
| Key | Default | Notes |
|-----|---------|-------|
| CHUNK_SIZE | 800 | tokens/chars per chunk |
| CHUNK_OVERLAP | 120 | overlap |
| RETRIAL_TOP_K | 5 | retrieved chunks |
| EMBEDDING_MODEL | nomic-embed-text | local lightweight |
| OLLAMA_DEFAULT_MODEL | qwen2.5:3b-instruct | 3B Q4 ~2GB RAM |
| MAX_UPLOAD_MB | 100 | |
| OCR_ENABLED | true | |

Low RAM: reduce CHUNK_SIZE, RETRIEVAL_TOP_K, context_length.
""")

write(BASE / "API.md", """
# API (Phase 1)
Base: http://localhost:8000

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | liveness |
| GET | /api/v1/health | versioned health + DB + storage check |
| GET | /docs | OpenAPI Swagger |
| GET | /openapi.json | OpenAPI JSON |

Future (stubs return 501):
/documents, /collections, /journals, /manuscripts, /models, /search, /chat
""")

print("phase1 docs done")