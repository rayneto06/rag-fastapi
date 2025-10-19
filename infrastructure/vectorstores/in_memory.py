from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from domain.services.vector_store import Chunk, VectorStore


class InMemoryVectorStore(VectorStore):
    """
    Implementação simples em memória para testes.
    Métrica de similaridade: Jaccard de tokens casefolded.
    """

    def __init__(self) -> None:
        self._by_doc: dict[str, list[Chunk]] = defaultdict(list)

    def add(self, chunks: Iterable[Chunk]) -> int:
        count = 0
        for ch in chunks:
            self._by_doc[ch.document_id].append(ch)
            count += 1
        return count

    def similarity_search(self, query: str, top_k: int = 5) -> list[tuple[float, Chunk]]:
        q = _tokenize(query)
        scored: list[tuple[float, Chunk]] = []
        for lst in self._by_doc.values():
            for ch in lst:
                c = _tokenize(ch.content)
                score = _jaccard(q, c)
                if score > 0:
                    scored.append((score, ch))
        scored.sort(key=lambda t: t[0], reverse=True)
        return scored[:top_k]

    def delete_by_document(self, document_id: str) -> int:
        removed = len(self._by_doc.get(document_id, []))
        if document_id in self._by_doc:
            del self._by_doc[document_id]
        return removed


def _tokenize(text: str) -> set[str]:
    return set(text.casefold().split())


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union
