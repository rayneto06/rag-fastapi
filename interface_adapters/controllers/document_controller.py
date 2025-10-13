from __future__ import annotations
from pathlib import Path

from use_cases.ingest_document import IngestDocument, IngestDocumentInput, IngestDocumentOutput
from use_cases.list_documents import ListDocuments, ListDocumentsOutput
from use_cases.get_document import GetDocument, GetDocumentOutput

from domain.entities.document import Document


class DocumentController:
    def __init__(self, ingest_uc: IngestDocument, list_uc: ListDocuments, get_uc: GetDocument) -> None:
        self.ingest_uc = ingest_uc
        self.list_uc = list_uc
        self.get_uc = get_uc

    def ingest(self, tmp_file: Path, original_filename: str, content_type: str) -> IngestDocumentOutput:
        return self.ingest_uc.execute(
            IngestDocumentInput(tmp_file=tmp_file, original_filename=original_filename, content_type=content_type)
        )

    def list(self) -> ListDocumentsOutput:
        return self.list_uc.execute()

    def get(self, doc_id: str) -> GetDocumentOutput | None:
        return self.get_uc.execute(doc_id)
