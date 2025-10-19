from __future__ import annotations

from dataclasses import dataclass

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository


@dataclass(frozen=True)
class ListDocumentsOutput:
    documents: list[Document]


class ListDocuments:
    def __init__(self, repo: DocumentRepository) -> None:
        self.repo = repo

    def execute(self) -> ListDocumentsOutput:
        docs = list(self.repo.list_documents())
        docs.sort(key=lambda d: d.created_at, reverse=True)
        return ListDocumentsOutput(documents=docs)
