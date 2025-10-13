from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository


@dataclass(frozen=True)
class GetDocumentOutput:
    document: Document
    text_path: str
    chunks_path: str
    chunk_count: int


class GetDocument:
    def __init__(self, repo: DocumentRepository) -> None:
        self.repo = repo

    def execute(self, doc_id: str) -> Optional[GetDocumentOutput]:
        doc = self.repo.get_document(doc_id)
        if not doc:
            return None

        text_path = self.repo.paths["PROCESSED_DIR"] / f"{doc_id}.txt"
        chunks_path = self.repo.paths["PROCESSED_DIR"] / f"{doc_id}.chunks.jsonl"
        chunk_count = self.repo.count_chunks(doc_id)

        return GetDocumentOutput(
            document=doc,
            text_path=str(text_path),
            chunks_path=str(chunks_path),
            chunk_count=chunk_count,
        )
