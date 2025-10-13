from __future__ import annotations
from typing import Protocol, Tuple
from pathlib import Path


class TextExtractor(Protocol):
    def extract(self, pdf_path: Path) -> Tuple[str, int]:
        """Retorna (texto, numero_de_paginas)."""
        ...
