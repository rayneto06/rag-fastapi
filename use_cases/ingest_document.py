from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from domain.services.chunker import Chunker
from domain.services.text_extractor import TextExtractor


@dataclass(frozen=True)
class IngestDocumentInput:
    tmp_file: Path
    original_filename: str
    content_type: str = "application/pdf"


@dataclass(frozen=True)
class IngestDocumentOutput:
    document: Document
    text_path: str
    chunks_path: str
    chunk_count: int


class IngestDocument:
    def __init__(
        self, repo: DocumentRepository, extractor: TextExtractor, chunker: Chunker
    ) -> None:
        self.repo = repo
        self.extractor = extractor
        self.chunker = chunker

    def execute(self, inp: IngestDocumentInput) -> IngestDocumentOutput:
        paths = self.repo.allocate_paths(inp.original_filename)

        # move arquivo bruto
        self.repo.save_raw(inp.tmp_file, paths["raw_path"])

        # extrai texto
        text, pages = self.extractor.extract(paths["raw_path"])
        self.repo.save_text(text, paths["text_path"])

        # chunking
        chunk_iter = self.chunker.chunk(text)
        chunk_count = self.repo.save_chunks(chunk_iter, paths["chunks_path"])

        # cria entidade (timezone-aware, UTC)
        size_bytes = paths["raw_path"].stat().st_size
        doc = Document(
            id=paths["id"],
            original_filename=inp.original_filename,
            stored_filename=paths["raw_path"].name,
            size_bytes=size_bytes,
            pages=pages,
            created_at=datetime.now(timezone.utc),
            content_type=inp.content_type,
        )
        self.repo.save_meta(doc, paths["meta_path"])

        return IngestDocumentOutput(
            document=doc,
            text_path=str(paths["text_path"]),
            chunks_path=str(paths["chunks_path"]),
            chunk_count=chunk_count,
        )
