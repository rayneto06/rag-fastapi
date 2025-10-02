from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.v1.health import router as health_router
from app.version import APP_NAME, APP_VERSION


def create_app() -> FastAPI:
    """Fábrica da aplicação FastAPI."""
    configure_logging()
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS] or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rotas v1
    api_v1_prefix = "/v1"
    app.include_router(health_router, prefix=api_v1_prefix)

    @app.get("/", tags=["root"])
    def root():
        """Boas-vindas + versão."""
        return {
            "message": "Bem-vindo à API RAG FastAPI (local). Consulte /docs",
            "version": APP_VERSION,
        }

    return app


app = create_app()
