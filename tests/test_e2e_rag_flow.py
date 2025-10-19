from __future__ import annotations

from typing import Any, cast

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


def _minimal_text_pdf_bytes(text: str) -> bytes:
    """Gera um PDF 1-página com *texto real* (não só página em branco).
    Construído manualmente com um stream simples que o PyPDF consegue extrair.
    """
    # Escapa parênteses no texto para o literal PDF
    safe = text.replace("(", "\\(").replace(")", "\\)")
    pdf = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Resources << /Font << /F1 4 0 R >> >>
   /Contents 5 0 R
>>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 55 >>
stream
BT
/F1 12 Tf
72 720 Td
({safe}) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000060 00000 n
0000000118 00000 n
0000000274 00000 n
0000000344 00000 n
trailer
<< /Root 1 0 R /Size 6 >>
startxref
444
%%EOF
""".encode()
    return pdf


@pytest.mark.asyncio
async def test_e2e_upload_ingest_index_query_happy_path() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        text = "DDD Clean Architecture separa domínio e infraestrutura."
        pdf_bytes = _minimal_text_pdf_bytes(text)
        files = {"file": ("ddd-clean.pdf", pdf_bytes, "application/pdf")}
        up = await ac.post("/v1/documents", files=files)
        assert up.status_code == status.HTTP_201_CREATED
        body = up.json()
        assert body["chunk_count"] >= 1
        doc_id = body["meta"]["id"]
        cast(Any, test_e2e_upload_ingest_index_query_happy_path).doc_id = doc_id

        # agora consulta RAG e deve retornar hits reais
        q = await ac.post(
            "/v1/rag/query", json={"question": "Como DDD separa domínio?", "top_k": 5}
        )
        assert q.status_code == status.HTTP_200_OK
        data = q.json()
        assert isinstance(data.get("hits"), list)
        assert len(data["hits"]) >= 1
        # Melhor hit deve conter alguma das palavras do texto enviado
        top = data["hits"][0]
        assert isinstance(top["score"], float)
        assert any(
            w in top["content"].lower() for w in ("ddd", "domínio", "arquitetura", "infraestrutura")
        )


@pytest.mark.asyncio
async def test_upload_invalido_nao_pdf_deve_400() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"file": ("nota.txt", b"apenas texto", "text/plain")}
        resp = await ac.post("/v1/documents", files=files)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Apenas arquivos PDF" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_get_document_inexistente_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/v1/documents/nao-existe-123")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
