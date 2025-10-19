import json
from pathlib import Path

from infrastructure.chunk_sources.filesystem_jsonl import FilesystemJsonlChunkSource
from infrastructure.vectorstores.in_memory import InMemoryVectorStore
from use_cases.index_document_chunks import IndexDocumentChunks


def _write_jsonl(dirpath: Path, document_id: str, rows: list[dict]) -> Path:
    dirpath.mkdir(parents=True, exist_ok=True)
    fp = dirpath / f"{document_id}.chunks.jsonl"
    with fp.open("w", encoding="utf-8") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return fp


def test_index_document_chunks_happy_path(tmp_path: Path) -> None:
    doc_id = "doc-123"
    processed_dir = tmp_path / "data" / "processed"
    _write_jsonl(
        processed_dir,
        doc_id,
        [
            {"content": "DDD e domínio: entidades, agregados e repositórios."},
            {"content": "Clean Architecture mantém o domínio independente de frameworks."},
        ],
    )

    source = FilesystemJsonlChunkSource(processed_dir=processed_dir)
    store = InMemoryVectorStore()
    usecase = IndexDocumentChunks(source, store)

    result = usecase.execute(document_id=doc_id)
    assert result.document_id == doc_id
    assert result.added == 2

    # Busca simples
    hits = store.similarity_search("domínio entidades", top_k=5)
    assert len(hits) >= 1
    score, chunk = hits[0]
    assert score > 0
    assert "domínio" in chunk.content.lower()

    # Reindex limpa e re-adiciona
    result2 = usecase.execute(document_id=doc_id, reindex=True)
    assert result2.added == 2


def test_index_document_chunks_empty_source(tmp_path: Path) -> None:
    doc_id = "doc-vazio"
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    source = FilesystemJsonlChunkSource(processed_dir=processed_dir)
    store = InMemoryVectorStore()
    usecase = IndexDocumentChunks(source, store)

    result = usecase.execute(document_id=doc_id)
    assert result.added == 0

    hits = store.similarity_search("qualquer coisa", top_k=3)
    assert hits == []
