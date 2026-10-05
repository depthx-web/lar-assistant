from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(), "message": "Validation failed"}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):  # type: ignore
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def unhandled_exception_handler(request: Request, exc: Exception):  # type: ignore
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    msg = str(exc) if getattr(request.app, "debug", False) else "An unexpected error occurred"
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "message": msg}
    )