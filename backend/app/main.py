from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.routes import api_router
from app.core.config import settings
from app.core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine

# Import models so metadata is populated before create_all
import app.models  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    # Startup
    settings.resolved_storage_root.mkdir(parents=True, exist_ok=True)
    settings.resolved_documents_root.mkdir(parents=True, exist_ok=True)
    (settings.resolved_storage_root / "journals").mkdir(parents=True, exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception:
        logger.exception("Failed to create DB tables")
    logger.info("LARA startup complete (env=%s)", settings.app_env)
    yield
    # Shutdown
    logger.info("LARA shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="LARA - Local Academic Research Assistant",
        version=__version__,
        description="Modular local RAG + manuscript compliance system (CPU only, 12GB RAM friendly).",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers - never swallow with bare except:pass
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore

    # Routes
    @app.get("/health", tags=["health"], summary="Liveness probe")
    def liveness():  # type: ignore
        return {"status": "ok", "version": __version__}

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
