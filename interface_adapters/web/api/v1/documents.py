from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.container import Container
from interface_adapters.controllers.document_controller import DocumentController
from interface_adapters.dto.document_dto import (
    DocumentMetaDTO,
    DocumentListItemDTO,
    DocumentDetailDTO,
)


def get_router(container: Container) -> APIRouter:
    router = APIRouter(tags=["documents"])

    controller = DocumentController(
        ingest_uc=__build_ingest_uc(container),
        list_uc=__build_list_uc(container),
        get_uc=__build_get_uc(container),
    )

    @router.post("/documents", response_model=DocumentDetailDTO, status_code=status.HTTP_201_CREATED)
    async def upload_document(file: UploadFile = File(...)):
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

        # timezone-aware (UTC) para evitar DeprecationWarning
        tmp_name = f"tmp__{datetime.now(timezone.utc).timestamp()}"
        tmp = container.document_repository.paths["RAW_DIR"] / tmp_name
        with tmp.open("wb") as f:
            f.write(await file.read())

        out = controller.ingest(
            tmp_file=tmp,
            original_filename=file.filename,
            content_type=file.content_type or "application/pdf",
        )

        meta = DocumentMetaDTO(
            id=out.document.id,
            filename=out.document.stored_filename,
            original_filename=out.document.original_filename,
            size_bytes=out.document.size_bytes,
            pages=out.document.pages,
            created_at=out.document.created_at,
            content_type=out.document.content_type,
        )
        return DocumentDetailDTO(
            meta=meta,
            text_path=out.text_path,
            chunks_path=out.chunks_path,
            chunk_count=out.chunk_count,
        )

    @router.get("/documents", response_model=List[DocumentListItemDTO])
    def list_documents():
        result = controller.list()
        return [
            DocumentListItemDTO(
                id=d.id,
                filename=d.stored_filename,
                size_bytes=d.size_bytes,
                pages=d.pages,
                created_at=d.created_at,
            )
            for d in result.documents
        ]

    @router.get("/documents/{doc_id}", response_model=DocumentDetailDTO)
    def get_document(doc_id: str):
        result = controller.get(doc_id)
        if not result:
            raise HTTPException(status_code=404, detail="Documento não encontrado.")
        meta = DocumentMetaDTO(
            id=result.document.id,
            filename=result.document.stored_filename,
            original_filename=result.document.original_filename,
            size_bytes=result.document.size_bytes,
            pages=result.document.pages,
            created_at=result.document.created_at,
            content_type=result.document.content_type,
        )
        return DocumentDetailDTO(
            meta=meta,
            text_path=result.text_path,
            chunks_path=result.chunks_path,
            chunk_count=result.chunk_count,
        )

    return router


# wiring dos use cases (mantém a FastAPI “fina”)
def __build_ingest_uc(container: Container):
    from use_cases.ingest_document import IngestDocument
    return IngestDocument(
        repo=container.document_repository,
        extractor=container.text_extractor,
        chunker=container.chunker,
    )


def __build_list_uc(container: Container):
    from use_cases.list_documents import ListDocuments
    return ListDocuments(repo=container.document_repository)


def __build_get_uc(container: Container):
    from use_cases.get_document import GetDocument
    return GetDocument(repo=container.document_repository)
