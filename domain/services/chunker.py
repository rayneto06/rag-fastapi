from __future__ import annotations
from typing import Protocol, Iterable


class Chunker(Protocol):
    def chunk(self, text: str) -> Iterable[dict]:
        """Gera chunks no formato {'content': str, ...}."""
        ...
