from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.container import Container, build_container
from app.core.config import settings
from app.core.logging import configure_logging
from app.version import APP_NAME, APP_VERSION
from interface_adapters.web.api.v1.documents import get_router as documents_router_factory
from interface_adapters.web.api.v1.health import router as health_router
from interface_adapters.web.api.v1.rag import get_router as rag_router_factory


def create_app(container: Container | None = None) -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if settings.CORS_ENABLED:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # DI: permite injetar container customizado em testes
    container = container or build_container()

    api_v1_prefix = "/v1"
    app.include_router(health_router, prefix=api_v1_prefix)
    app.include_router(documents_router_factory(container), prefix=api_v1_prefix)
    app.include_router(rag_router_factory(container), prefix=api_v1_prefix)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "message": "Bem-vindo à API RAG FastAPI (local). Consulte /docs",
            "version": APP_VERSION,
        }

    return app


app = create_app()
