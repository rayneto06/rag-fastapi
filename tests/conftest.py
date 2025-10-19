from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.core.config import settings


@pytest.fixture(autouse=True, scope="session")
def clean_data_dirs() -> Iterator[None]:
    """
    Limpa as pastas de dados antes e depois dos testes,
    exceto se KEEP_TEST_DATA=1 no .env.
    """
    if settings.KEEP_TEST_DATA:
        print("⚠️  KEEP_TEST_DATA=1 — arquivos de teste serão mantidos.")
        yield
        return

    _clear_all()
    yield
    _clear_all()


def _clear_all() -> None:
    for folder in (settings.RAW_DIR, settings.PROCESSED_DIR, settings.INDEX_DIR):
        _clear_dir(folder)


def _clear_dir(folder: Path) -> None:
    if not folder.exists():
        return
    for item in folder.iterdir():
        if item.is_file():
            item.unlink(missing_ok=True)
        elif item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
