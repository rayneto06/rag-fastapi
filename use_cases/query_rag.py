from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from domain.services.vector_store import Chunk, VectorStore


@dataclass(frozen=True)
class QueryRAGInput:
    """
    Entrada do caso de uso de consulta RAG (apenas recuperação por enquanto).
    """

    question: str
    top_k: int = 5


@dataclass(frozen=True)
class RetrievedChunk:
    """
    Saída normalizada para a aplicação/web sem expor implementações de infraestrutura.
    """

    score: float
    document_id: str
    content: str
    chunk_id: Optional[str]
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class QueryRAGOutput:
    """
    Resultado da consulta: lista de chunks recuperados.
    """

    hits: List[RetrievedChunk]


class QueryRAG:
    """
    Caso de uso: dada uma pergunta (string), realizar busca de similaridade
    no VectorStore e retornar os top_k chunks com score.
    """

    def __init__(self, store: VectorStore) -> None:
        self._store = store

    def execute(self, inp: QueryRAGInput) -> QueryRAGOutput:
        # Validações simples e defensivas (sem "gambiarras")
        q = (inp.question or "").strip()
        if not q:
            return QueryRAGOutput(hits=[])

        top_k = max(1, min(50, int(inp.top_k)))

        results: List[Tuple[float, Chunk]] = self._store.similarity_search(q, top_k=top_k)
        hits: List[RetrievedChunk] = [
            RetrievedChunk(
                score=float(score),
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_id=chunk.chunk_id,
                metadata=chunk.metadata,
            )
            for score, chunk in results
        ]
        return QueryRAGOutput(hits=hits)
