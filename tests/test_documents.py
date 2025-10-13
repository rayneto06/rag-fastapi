from __future__ import annotations
import io
import json
from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
from pypdf import PdfWriter

from app.main import app
from app.core.config import settings


def _make_minimal_pdf_bytes() -> bytes:
    """Gera um PDF simples em memória para testes."""
    writer = PdfWriter()
    writer.add_blank_page(width=72 * 8.5, height=72 * 11)  # página A4 aproximada
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_upload_document_ok(tmp_path: Path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        pdf_bytes = _make_minimal_pdf_bytes()
        files = {"file": ("teste.pdf", pdf_bytes, "application/pdf")}
        resp = await ac.post("/v1/documents", files=files)

    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert "meta" in body and "chunk_count" in body
    assert body["meta"]["id"]
    assert body["meta"]["pages"] >= 1
    assert body["meta"]["filename"].endswith(".pdf")
    # guarda para os próximos testes
    test_upload_document_ok.doc_id = body["meta"]["id"]  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_list_documents_contains_uploaded():
    # garante que o teste anterior rodou e gerou um id
    doc_id = getattr(test_upload_document_ok, "doc_id", None)  # type: ignore[attr-defined]
    assert doc_id is not None, "O teste de upload deve rodar antes deste."

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/v1/documents")

    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()
    assert isinstance(items, list)
    assert any(it["id"] == doc_id for it in items)


@pytest.mark.asyncio
async def test_get_document_by_id_ok():
    doc_id = getattr(test_upload_document_ok, "doc_id", None)  # type: ignore[attr-defined]
    assert doc_id is not None, "O teste de upload deve rodar antes deste."

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/v1/documents/{doc_id}")

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["meta"]["id"] == doc_id
    assert Path(body["text_path"]).exists()
    assert Path(body["chunks_path"]).exists()
    assert body["chunk_count"] >= 0
