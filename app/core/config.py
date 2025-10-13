from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "local"
    APP_PORT: int = 8000

    CORS_ORIGINS: List[AnyHttpUrl] = []

    DATA_DIR: Path = Path("./data")
    RAW_DIR: Path = Path("./data/raw")
    PROCESSED_DIR: Path = Path("./data/processed")
    INDEX_DIR: Path = Path("./data/index")
    KEEP_TEST_DATA: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    def ensure_dirs(self) -> None:
        for p in (self.DATA_DIR, self.RAW_DIR, self.PROCESSED_DIR, self.INDEX_DIR):
            os.makedirs(p, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
