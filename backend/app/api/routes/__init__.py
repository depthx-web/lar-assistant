from __future__ import annotations

from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.model_registry import ModelRecord

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.rag import router as rag_router
from app.api.routes.journals import router as journals_router
from app.api.routes.manuscripts import router as manuscripts_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.phase13 import router as phase13_router
from app.api.routes.phase14 import router as phase14_router
from app.api.routes.phase15 import router as phase15_router

system_router = APIRouter()


class SystemComponent(BaseModel):
    name: str
    status: str
    detail: Optional[str] = None


class SystemStatusResponse(BaseModel):
    status: str
    components: Dict[str, SystemComponent]
    uptime_check: bool


class QueueJob(BaseModel):
    model_config = {'from_attributes': True}
    id: int
    job_type: str
    status: str
    progress: int
    created_at: str
    error: Optional[str] = None


class QueueResponse(BaseModel):
    jobs: List[QueueJob]
    total: int
    active: int


class ModelRoleAssignment(BaseModel):
    role: str
    model_name: Optional[str] = None
    provider: Optional[str] = None


class ModelRoleListResponse(BaseModel):
    assignments: List[ModelRoleAssignment]


_ROLE_OPTIONS = [
    'general_chat', 'literature_analysis', 'academic_writing',
    'summarization', 'embeddings', 'classification', 'journal_evaluation',
]


@system_router.get('/system/status', response_model=SystemStatusResponse, tags=['system'])
def get_system_status(db: Annotated[Session, Depends(get_db)]):
    components = {}
    try:
        db.execute(text('SELECT 1'))
        components['database'] = SystemComponent(name='Database', status='ok')
    except Exception as e:
        components['database'] = SystemComponent(name='Database', status='error', detail=str(e))
    try:
        (settings.resolved_documents_root / '.health_probe').write_text('ok', encoding='utf-8')
        components['storage'] = SystemComponent(name='Storage', status='ok')
    except Exception as e:
        components['storage'] = SystemComponent(name='Storage', status='error', detail=str(e))
    try:
        import httpx
        resp = httpx.get(f'{settings.ollama_base_url}/api/tags', timeout=3)
        components['ollama'] = SystemComponent(name='Ollama', status='ok' if resp.status_code == 200 else 'error')
    except Exception:
        components['ollama'] = SystemComponent(name='Ollama', status='unavailable', detail='Cannot reach Ollama service')
    try:
        from app.document_processing.embedder import DocumentEmbedder
        embedder = DocumentEmbedder(db)
        embedder.embed(['test'])
        components['embedding'] = SystemComponent(name='Embedding', status='ok')
    except Exception as e:
        components['embedding'] = SystemComponent(name='Embedding', status='unavailable', detail=str(e)[:100])
    overall = 'ok' if all(c.status == 'ok' for c in components.values()) else 'degraded'
    return SystemStatusResponse(status=overall, components=components, uptime_check=True)


@system_router.get('/system/queue', response_model=QueueResponse, tags=['system'])
def get_processing_queue(db: Annotated[Session, Depends(get_db)]):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return QueueResponse(
        jobs=[QueueJob.model_validate(j) for j in jobs],
        total=len(jobs),
        active=sum(1 for j in jobs if j.status in (JobStatus.RUNNING.value, JobStatus.QUEUED.value)),
    )


@system_router.get('/system/models/roles', response_model=ModelRoleListResponse, tags=['system'])
def list_model_roles(db: Annotated[Session, Depends(get_db)]):
    records = db.query(ModelRecord).all()
    by_role = {}
    for r in records:
        if r.role not in by_role or not by_role[r.role]:
            by_role[r.role] = {'role': r.role, 'model_name': r.name, 'provider': r.provider}
    assignments = [ModelRoleAssignment(**a) for a in by_role.values()]
    return ModelRoleListResponse(assignments=assignments)


@system_router.put('/system/models/roles/{role}', response_model=ModelRoleAssignment, tags=['system'])
def assign_model_role(role: str, db: Annotated[Session, Depends(get_db)]):
    if role not in _ROLE_OPTIONS:
        raise HTTPException(status_code=400, detail='Invalid role. Must be one of: ' + ', '.join(_ROLE_OPTIONS))
    record = db.query(ModelRecord).filter(ModelRecord.role == role).first()
    if record:
        return ModelRoleAssignment(role=record.role, model_name=record.name, provider=record.provider)
    return ModelRoleAssignment(role=role, model_name=None, provider=None)


api_router = APIRouter()
api_router.include_router(health_router, prefix='', tags=['health'])
api_router.include_router(chat_router, prefix='', tags=['chat'])
api_router.include_router(documents_router, prefix='', tags=['documents'])
api_router.include_router(search_router, prefix='', tags=['search'])
api_router.include_router(rag_router, prefix='', tags=['rag'])
api_router.include_router(journals_router, prefix='', tags=['journals'])
api_router.include_router(manuscripts_router, prefix='', tags=['manuscripts'])
api_router.include_router(evaluations_router, prefix='', tags=['evaluations'])
api_router.include_router(phase13_router, prefix='', tags=['phase13'])
api_router.include_router(phase14_router, prefix='', tags=['phase14'])
api_router.include_router(phase15_router, prefix='', tags=['phase15'])
api_router.include_router(system_router, prefix='/system', tags=['system'])

__all__ = ['api_router']