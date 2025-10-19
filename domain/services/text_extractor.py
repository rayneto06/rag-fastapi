from __future__ import annotations

from pathlib import Path
from typing import Protocol, Tuple


class TextExtractor(Protocol):
    def extract(self, pdf_path: Path) -> Tuple[str, int]:
        """Retorna (texto, numero_de_paginas)."""
        ...
