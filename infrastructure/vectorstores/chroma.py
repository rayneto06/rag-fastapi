from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

from domain.services.vector_store import Chunk, VectorStore


class _HashingEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Embedding determinística, local e rápida para testes offline."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = int(dim)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(x) for x in input]

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.casefold().split():
            h = hash(token) % self.dim
            vec[h] += 1.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]


class ChromaVectorStore(VectorStore):
    """VectorStore persistente usando ChromaDB (local)."""

    def __init__(
        self,
        persist_directory: str | Path = ".chroma",
        collection_name: str = "rag_chunks",
        embedding_dim: int = 256,
    ) -> None:
        self._persist_directory = str(persist_directory)
        self._client = chromadb.PersistentClient(path=self._persist_directory)
        self._collection: Collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=_HashingEmbeddingFunction(dim=embedding_dim),
            metadata={"hnsw:space": "l2"},
        )

    def add(self, chunks: Iterable[Chunk]) -> int:
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for idx, ch in enumerate(chunks):
            cid = ch.chunk_id or f"{ch.document_id}:{idx}"
            ids.append(cid)
            documents.append(ch.content)
            meta: dict[str, Any] = {"document_id": ch.document_id, "chunk_id": cid}
            for k, v in (ch.metadata or {}).items():
                if k not in meta:
                    meta[k] = v
            metadatas.append(meta)

        if not ids:
            return 0

        # Ajuste de tipagem: converte para lista de Mapping[str, Any]
        from collections.abc import Mapping

        metadatas_list: list[Mapping[str, Any]] = [m for m in metadatas]
        self._collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas_list,
        )

        return len(ids)

    def similarity_search(self, query: str, top_k: int = 5) -> list[tuple[float, Chunk]]:
        top_k = max(1, min(50, int(top_k)))
        if not query.strip():
            return []

        # Conversão explícita para tipos aceitos pelo SDK
        include_fields: list[Any] = ["documents", "metadatas", "distances"]
        res = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            include=include_fields,
        )
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]

        results: list[tuple[float, Chunk]] = []
        for doc, meta, dist in zip(docs, metas, dists, strict=False):
            try:
                d = float(dist)
            except Exception:
                d = 0.0
            score = 1.0 / (1.0 + max(0.0, d))
            results.append(
                (
                    score,
                    Chunk(
                        document_id=str(meta.get("document_id", "")),
                        content=str(doc),
                        chunk_id=(
                            str(meta.get("chunk_id")) if meta.get("chunk_id") is not None else None
                        ),
                        metadata={
                            k: v for k, v in meta.items() if k not in ("document_id", "chunk_id")
                        },
                    ),
                )
            )

        results.sort(key=lambda t: t[0], reverse=True)
        return results

    def delete_by_document(self, document_id: str) -> int:
        """Remove todos os chunks de um documento e retorna quantos foram removidos."""
        res = self._collection.get(where={"document_id": document_id}, include=[])
        ids = res.get("ids") or []
        removed = len(ids)
        if removed:
            self._collection.delete(where={"document_id": document_id})
        return removed
