from __future__ import annotations

from fastapi import APIRouter
from app.version import APP_NAME, APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthcheck():
    """Endpoint simples para ver se a API está viva."""
    return {"status": "ok", "name": APP_NAME, "version": APP_VERSION}
