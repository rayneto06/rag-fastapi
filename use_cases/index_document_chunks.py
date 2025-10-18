from __future__ import annotations
from dataclasses import dataclass

from domain.services.chunk_source import ChunkSource
from domain.services.vector_store import VectorStore


@dataclass(frozen=True)
class IndexResult:
    document_id: str
    added: int


class IndexDocumentChunks:
    """
    Caso de uso: ler os chunks de um documento a partir de um ChunkSource
    e adicioná-los ao VectorStore.
    """

    def __init__(self, source: ChunkSource, store: VectorStore) -> None:
        self._source = source
        self._store = store

    def execute(self, document_id: str, reindex: bool = False) -> IndexResult:
        if reindex:
            self._store.delete_by_document(document_id)
        added = self._store.add(self._source.iter_chunks(document_id))
        return IndexResult(document_id=document_id, added=added)
