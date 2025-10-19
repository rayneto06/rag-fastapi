from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações globais da aplicação RAG-FastAPI.

    Usa pydantic-settings para permitir carregamento via variáveis de ambiente (.env)
    mantendo tipagem e valores padrão seguros.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "local"
    APP_PORT: int = 8000

    # CORS
    CORS_ENABLED: bool = True
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

    # Diretórios de dados
    DATA_DIR: Path = Path("./data")
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    INDEX_DIR: Path = DATA_DIR / "index"

    # Flag para limpeza pós-testes
    KEEP_TEST_DATA: bool = False

    @field_validator("CORS_ALLOW_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        """Permite definir múltiplas origens via string separada por vírgulas no .env."""
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    def ensure_dirs(self) -> None:
        """Cria diretórios esperados, se não existirem."""
        for p in (self.DATA_DIR, self.RAW_DIR, self.PROCESSED_DIR, self.INDEX_DIR):
            os.makedirs(p, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
                