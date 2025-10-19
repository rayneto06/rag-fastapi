from __future__ import annotations

import json
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
from domain.services.vector_store import Chunk as VSChunk


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

        # salva upload temporário (no diretório RAW do repo)
        tmp_name = f"tmp__{datetime.now(timezone.utc).timestamp()}"
        tmp = container.document_repository.paths["RAW_DIR"] / tmp_name
        with tmp.open("wb") as f:
            f.write(await file.read())

        # 1) Ingest (usa o caso de uso existente: salva raw/text/chunks/meta)
        result = controller.ingest(
            tmp_file=tmp,
            original_filename=file.filename,
            content_type=file.content_type or "application/pdf",
        )

        # 2) Indexar no Vector Store a partir do arquivo .chunks.jsonl
        try:
            chunks_path = Path(result.chunks_path)
            vs_chunks: List[VSChunk] = []
            with chunks_path.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    data = json.loads(line)
                    content = (data.get("content") or "").strip()
                    if not content:
                        continue
                    meta = {k: v for k, v in data.items() if k != "content"}
                    vs_chunks.append(
                        VSChunk(
                            document_id=result.document.id,
                            content=content,
                            chunk_id=f"{result.document.id}:{i}",
                            metadata=meta,
                        )
                    )
            if vs_chunks:
                container.vector_store.add(vs_chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha ao indexar chunks: {e}") from e

        # 3) Resposta compatível com os testes e com o contrato atual
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
