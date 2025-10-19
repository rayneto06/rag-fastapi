from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class Chunker(Protocol):
    def chunk(self, text: str) -> Iterable[dict]:
        """Gera chunks no formato {'content': str, ...}."""
        ...
