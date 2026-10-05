# DEVELOPMENT

## Conventions
- Python 3.11+, type hints required, no `except: pass`.
- Each layer independent (see ARCHITECTURE.md).
- Journals = data/config, Models = providers.
- All secrets via .env, never commit.

## Repo layout
```
lar-assistant/
  backend/app/{core,api,models,ai,document_processing,rag,journal_engine,manuscript,jobs,services}
  backend/tests/
  backend/alembic/
  frontend/src/
  journals/<slug>/
  prompts/
  storage/
  data/
```

## Adding a journal (no code change)
1. Copy `journals/example-journal/` to `journals/<slug>/`
2. Edit `profile.yaml`, `requirements.yaml` (with source_url/evidence)
3. Leave style-guide for Phase 10

## Adding a model provider (no core change)
1. Subclass `LLMProvider` in `backend/app/ai/<name>_provider.py`
2. Implement generate/stream/embed/health_check/list_models
3. Call `register_provider("name", YourProvider)` at import
4. Add record via Model Manager (Phase 14) or DB

## Testing
```
pytest backend/tests -v
```

## Lint (optional)
```
ruff check backend/app
mypy backend/app
```
