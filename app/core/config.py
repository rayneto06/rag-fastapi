from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_origins(value: object) -> List[str]:
    """
    Aceita:
    - JSON string: '["http://a","http://b"]'
    - CSV: 'http://a, http://b'
    - Lista já tipada
    """
    if isinstance(value, list) and all(isinstance(i, str) for i in value):
        return value
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list) and all(isinstance(i, str) for i in parsed):
                    return parsed
            except Exception:
                pass
        # fallback CSV
        return [o.strip().strip('"').strip("'") for o in s.split(",") if o.strip()]
    # default seguro
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


class Settings(BaseSettings):
    """
    Configurações globais da aplicação RAG-FastAPI.
    """

    # ---- App ----
    APP_ENV: str = "local"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # ---- CORS ----
    CORS_ENABLED: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ---- Dados locais ----
    DATA_DIR: Path = Path("data")
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    INDEX_DIR: Path = DATA_DIR / "index"

    # Manter arquivos de teste após pytest se =1
    KEEP_TEST_DATA: bool = False

    # ---- Vector Store Provider ----
    VECTOR_STORE_PROVIDER: str = "inmemory"  # 'inmemory' | 'chroma'
    CHROMA_DIR: Path = Path(".chroma")  # diretório de persistência do Chroma
    CHROMA_COLLECTION: str = "rag_chunks"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",  # chaves extras no .env não quebram o app
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _val_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        return _parse_origins(v)

    def ensure_dirs(self) -> None:
        """Cria diretórios esperados, se não existirem."""
        for p in (self.DATA_DIR, self.RAW_DIR, self.PROCESSED_DIR, self.INDEX_DIR, self.CHROMA_DIR):
            os.makedirs(p, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
