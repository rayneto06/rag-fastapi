from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from domain.services.vector_store import Chunk


class ChunkSource(ABC):
    """
    Porta para leitura de chunks de alguma origem (filesystem, S3, DB, etc.).
    """

    @abstractmethod
    def iter_chunks(self, document_id: str) -> Iterable[Chunk]:
        """
        Itera chunks de um documento específico.
        """
        raise NotImplementedError
