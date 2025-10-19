from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DocumentMetaDTO(BaseModel):
    id: str
    filename: str
    original_filename: str
    size_bytes: int
    pages: int
    created_at: datetime
    content_type: str = "application/pdf"


class DocumentListItemDTO(BaseModel):
    id: str
    filename: str
    size_bytes: int
    pages: int
    created_at: datetime


class DocumentDetailDTO(BaseModel):
    meta: DocumentMetaDTO
    text_path: str
    chunks_path: str
    chunk_count: int
