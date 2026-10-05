#Requires -Version 5.1
<#
.SYNOPSIS
  LARA Windows Setup - Phase 1 skeleton
.DESCRIPTION
  - Checks Python 3.11+
  - Creates .venv
  - Installs backend/requirements.txt
  - Creates folders, .env, and DB
  - Checks Ollama (optional)
#>
param(
  [string]$PythonCmd = "py -V:Astral/CPython3.14.7",
  [switch]$SkipOllamaCheck
)

$ErrorActionPreference = "Stop"
$Base = $PSScriptRoot
if (-not $Base) { $Base = "E:\depthx\lar-assistant" }
Set-Location $Base

Write-Host "== LARA Setup (Phase 1) ==" -ForegroundColor Cyan
Write-Host "Base: $Base"

# 1) Python check
Write-Host "`n[1/7] Checking Python..." -ForegroundColor Yellow
try {
  $pyVer = Invoke-Expression "$PythonCmd --version 2>&1"
  Write-Host "  Found: $pyVer ($PythonCmd)" -ForegroundColor Green
} catch {
  Write-Host "  Python not found via '$PythonCmd'. Try: py --version or python --version" -ForegroundColor Red
  Write-Host "  Install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
  exit 1
}

# 2) venv
Write-Host "`n[2/7] Creating virtual environment .venv..." -ForegroundColor Yellow
if (-not (Test-Path "$Base\.venv\Scripts\python.exe")) {
  Invoke-Expression "$PythonCmd -m venv .venv"
  Write-Host "  Created .venv" -ForegroundColor Green
} else {
  Write-Host "  .venv already exists, skipping" -ForegroundColor DarkGray
}

$VenvPython = "$Base\.venv\Scripts\python.exe"
$VenvPip = "$Base\.venv\Scripts\pip.exe"

# 3) pip install
Write-Host "`n[3/7] Installing backend requirements..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip
& $VenvPip install -r "$Base\backend\requirements.txt"
if ($LASTEXITCODE -ne 0) { Write-Host "  pip install failed" -ForegroundColor Red; exit 1 }
Write-Host "  Dependencies installed" -ForegroundColor Green

# 4) folders
Write-Host "`n[4/7] Creating storage/data/logs folders..." -ForegroundColor Yellow
@("data","storage\documents","storage\journals","logs","journals\example-journal\sources","journals\example-journal\example-papers","prompts") | ForEach-Object {
  $p = Join-Path $Base $_
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}
# .gitkeep
@("storage\documents","storage\journals","logs","data") | ForEach-Object {
  $gk = Join-Path $Base "$_/.gitkeep"
  if (-not (Test-Path $gk)) { New-Item -ItemType File -Path $gk | Out-Null }
}
Write-Host "  Folders ready" -ForegroundColor Green

# 5) .env
Write-Host "`n[5/7] Checking .env..." -ForegroundColor Yellow
if (-not (Test-Path "$Base\.env")) {
  Copy-Item "$Base\.env.example" "$Base\.env"
  Write-Host "  Created .env from .env.example - please edit if needed" -ForegroundColor Green
} else {
  Write-Host "  .env exists" -ForegroundColor DarkGray
}

# 6) DB init
Write-Host "`n[6/7] Initializing SQLite DB..." -ForegroundColor Yellow
& $VenvPython -c "from app.db.base import Base; from app.db.session import engine; import app.models; Base.metadata.create_all(bind=engine); print('  DB OK:', engine.url)"
Write-Host "  DB initialized" -ForegroundColor Green

# 7) Ollama check (optional)
Write-Host "`n[7/7] Checking Ollama (optional)..." -ForegroundColor Yellow
if ($SkipOllamaCheck) {
  Write-Host "  Skipped" -ForegroundColor DarkGray
} else {
  try {
    $resp = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  Ollama is running" -ForegroundColor Green
    if ($resp.models) { $resp.models | ForEach-Object { Write-Host "    - $($_.name)" } }
    else { Write-Host "    No models yet. Run: ollama pull qwen2.5:3b-instruct" -ForegroundColor Yellow }
  } catch {
    Write-Host "  Ollama not reachable at http://localhost:11434 (OK for Phase 1)" -ForegroundColor Yellow
    Write-Host "  Install from https://ollama.com/download and run: ollama pull qwen2.5:3b-instruct" -ForegroundColor DarkGray
  }
}

Write-Host "`n== Setup complete ==" -ForegroundColor Cyan
Write-Host "Next:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app.main:app --app-dir backend --reload --port 8000"
Write-Host "  Open http://localhost:8000/docs"
Write-Host "  pytest backend/tests -v"
