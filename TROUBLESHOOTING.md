# TROUBLESHOOTING

## Backend won't start
- Ensure .venv active: `.\.venv\Scripts\Activate.ps1`
- `pip install -r backend/requirements.txt` again
- Check port: `netstat -ano | findstr :8000`

## DB errors
- Delete `data/lara.db` and restart (Phase 1 only)
- From Phase 3: use `alembic upgrade head`

## Ollama not reachable
- Phase 1: OK, not required
- Phase 2+: `ollama serve` in separate terminal, then `ollama pull qwen2.5:3b-instruct`

## Logs
- See API stdout + `logs/` (when configured)
- Diagnostics endpoint planned for Phase 2

## Windows path traversal
- Filenames are sanitized via `app.core.security.sanitize_filename`
