from pathlib import Path

import pytest

from domain.services.vector_store import Chunk

# Importa condicionalmente para não falhar quando chroma não estiver instalado localmente
try:
    from infrastructure.vectorstores.chroma import ChromaVectorStore
except Exception:
    ChromaVectorStore = None  # type: ignore


pytestmark = pytest.mark.skipif(ChromaVectorStore is None, reason="chromadb não instalado")


def _make_chunks(doc_id: str) -> list[Chunk]:
    return [
        Chunk(
            document_id=doc_id, content="FastAPI e RAG com chunks em disco", chunk_id=f"{doc_id}:0"
        ),
        Chunk(
            document_id=doc_id,
            content="Vector Store persistente usando Chroma local",
            chunk_id=f"{doc_id}:1",
        ),
        Chunk(
            document_id=doc_id,
            content="Testes devem validar persistência e deleção",
            chunk_id=f"{doc_id}:2",
        ),
    ]


def test_chroma_persiste_e_busca_apos_reiniciar(tmp_path: Path) -> None:
    chroma_dir = tmp_path / ".chroma"
    store = ChromaVectorStore(persist_directory=chroma_dir, collection_name="test_chunks")

    added = store.add(_make_chunks("doc-1"))
    assert added == 3

    # Recria a instância para simular reinício do app
    store2 = ChromaVectorStore(persist_directory=chroma_dir, collection_name="test_chunks")
    hits = store2.similarity_search("RAG com Vector Store persistente", top_k=2)
    assert len(hits) == 2
    # Deve trazer o chunk sobre Chroma com score alto
    top_doc_ids = [c.document_id for _, c in hits]
    assert "doc-1" in top_doc_ids


def test_chroma_delete_by_document_remove_todos(tmp_path: Path) -> None:
    chroma_dir = tmp_path / ".chroma"
    store = ChromaVectorStore(persist_directory=chroma_dir, collection_name="test_chunks")

    added1 = store.add(_make_chunks("doc-A"))
    added2 = store.add(_make_chunks("doc-B"))
    assert added1 == 3 and added2 == 3

    removed = store.delete_by_document("doc-A")
    assert removed == 3

    hits = store.similarity_search("Vector Store persistente", top_k=10)
    # Nenhum chunk do doc-A deve permanecer
    assert all(chunk.document_id != "doc-A" for _, chunk in hits)
