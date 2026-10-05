# Local Academic Research Assistant (LARA)

> مساعد بحث وكتابة اكاديمية محلي - يعمل Offline قدر الامكان، مصمم لجهاز محدود الموارد (ThinkPad T450s / 12GB RAM / CPU only).

**الحالة:** PHASE 13 - Multi-Version Comparison, Export & Submission Workflow - COMPLETED

## الفكرة باختصار
- رفع اوراق PDF + روابط المقالات -> استخراج نص + OCR -> تقسيم دلالي -> Embedding محلي -> RAG
- تحليل منهجية / مقارنات / Literature Review / اعادة صياغة اكاديمية مع Evidence
- Journal Profiles (متطلبات + style guide) + Manuscript Compliance Engine + Pre-submission Gate
- Model Provider Abstraction (Ollama / OpenAI / Anthropic / LocalTransformers) - لا ارتباط مباشر بـ Qwen/Ollama

## البنية (انظر ARCHITECTURE.md)
```
UI (React/Vite - frontend/)
  |
API (FastAPI - backend/app/api)
  |
Application Services (app/services)
  |
AI Provider Layer  ->  Document Processing  ->  RAG  ->  Journal Engine  ->  Manuscript Engine
  |
SQLite (+ pgvector لاحقا) / Storage
```

## القواعد الذهبية
1. Evidence-first - لا اجابة دون مصدر عند الامكان.
2. لا اختراع DOI/مؤلفين/احصائيات/متطلبات مجلة.
3. فرق بين OFFICIAL_REQUIREMENT / OBSERVED_PATTERN / MODEL_ASSESSMENT.
4. لا نسب قبول وهمية - فقط Readiness/Compliance.

## تشغيل
```powershell
cd E:\depthx\lar-assistant
powershell -ExecutionPolicy Bypass -File setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --port 8000
# http://localhost:8000/health  و  http://localhost:8000/docs
```

## التحقق
```powershell
pytest backend/tests -v
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

## المراحل
| Phase | الحالة | الوصف |
|-------|--------|--------|
| 1 | ✅ DONE | Project skeleton |
| 2 | ✅ DONE | Ollama integration (generate/stream/embed/models) |
| 3 | ✅ DONE | Document upload (hash deduplication, MIME validation, 20MB limit) |
| 4 | ✅ DONE | PDF extraction (text/tables/metadata) |
| 5 | ✅ DONE | Text chunking + embeddings (semantic search) |
| 6 | ✅ DONE | RAG pipeline (Q&A with citations) |
| 7 | ✅ DONE | Journal profiles (YAML-based requirements) |
| 8 | ✅ DONE | URL ingestion + Manuscript compliance |
| 9 | ✅ DONE | Journal Update Engine + Style Analysis Foundation |
| 10-12 | ✅ DONE | Style analysis, Evaluation, Pre-submission gate |\n| 13 | ✅ DONE | Version diff, tagging, collaboration, export (PDF/LaTeX/text), submission workflow |

انظر INSTALL.md و CONFIGURATION.md و DEVELOPMENT.md و PHASE8_URL.md و PHASE8.md.
