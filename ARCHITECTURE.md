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
