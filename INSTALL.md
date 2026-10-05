# INSTALL - LARA (Windows 10/11)

## Prerequisites
- Python 3.11+ (check: py --version)
- Git, PowerShell 5+
- Ollama (optional for Phase 1, required from Phase 2): https://ollama.com/download
- Node 18+ for frontend (optional Phase 1)

## Setup (PowerShell)
```powershell
cd E:\depthx\lar-assistant
powershell -ExecutionPolicy Bypass -File setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --port 8000
# open http://localhost:8000/health and http://localhost:8000/docs
```

## Manual setup
```powershell
py -V:Astral/CPython3.14.7 -m venv .venv
.\.venv\Scripts\Activate.ps1
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
