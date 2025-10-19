from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from domain.services.chunk_source import ChunkSource
from domain.services.vector_store import Chunk


class FilesystemJsonlChunkSource(ChunkSource):
    """
    Lê `data/processed/<document_id>.chunks.jsonl`.
    Cada linha deve ser um JSON com ao menos {"content": "..."}.
    """

    def __init__(self, processed_dir: str | Path = "data/processed") -> None:
        self._processed_dir = Path(processed_dir)

    def iter_chunks(self, document_id: str) -> Iterable[Chunk]:
        path = self._processed_dir / f"{document_id}.chunks.jsonl"
        if not path.exists():
            # Sem exceção aqui: deixar o caso de uso decidir como lidar com 0 itens
            return iter(())
        return _iter_file(path, document_id)


def _iter_file(path: Path, document_id: str) -> Iterator[Chunk]:
    with path.open("r", encoding="utf-8") as f:
        idx = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            data: dict[str, Any] = json.loads(line)
            content = str(data.get("content", "")).strip()
            if not content:
                continue
            # chunk_id determinístico e legível
            chunk_id = f"{document_id}:{idx}"
            metadata = {k: v for k, v in data.items() if k != "content"}
            yield Chunk(
                document_id=document_id,
                content=content,
                chunk_id=chunk_id,
                metadata=metadata,
            )
            idx += 1
