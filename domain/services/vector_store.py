from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Chunk:
    """
    Unidade mínima de recuperação no RAG.
    Mantemos no domínio para não depender de entidade de infraestrutura.
    """

    document_id: str
    content: str
    chunk_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(ABC):
    """
    Porta (interface) para um repositório vetorial.
    Implementações residem em infrastructure/vectorstores/*.
    """

    @abstractmethod
    def add(self, chunks: Iterable[Chunk]) -> int:
        """
        Indexa uma coleção de chunks.
        Retorna a quantidade adicionada.
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(self, query: str, top_k: int = 5) -> list[tuple[float, Chunk]]:
        """
        Busca semântica aproximada.
        Retorna lista de (score_normalizado_0_1, chunk), ordenada desc.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_document(self, document_id: str) -> int:
        """
        Remove todos os chunks associados ao document_id.
        Retorna a quantidade removida.
        """
        raise NotImplementedError
