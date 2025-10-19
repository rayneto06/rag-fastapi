import pytest
from httpx import ASGITransport, AsyncClient

from app.container import Container, build_container
from app.main import create_app
from domain.services.vector_store import Chunk
from infrastructure.vectorstores.in_memory import InMemoryVectorStore


@pytest.mark.asyncio
async def test_rag_query_returns_hits_ordered_by_score() -> None:
    # Arrange: cria um container e injeta um VectorStore populado
    base_container: Container = build_container()
    store = InMemoryVectorStore()

    # Adiciona dois documentos/chunks simples
    store.add(
        [
            Chunk(
                document_id="doc-1",
                content="FastAPI RAG com arquitetura limpa e testes de integração.",
            ),
            Chunk(document_id="doc-1", content="Indexação de chunks e busca de similaridade."),
        ]
    )
    store.add(
        [
            Chunk(document_id="doc-2", content="Odontologia hospitalar e protocolos clínicos."),
            Chunk(document_id="doc-2", content="Scores BOE e avaliação de higiene oral em UTI."),
        ]
    )

    # Substitui apenas o vector_store do container padrão
    base_container.vector_store = store

    app = create_app(container=base_container)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Act: consulta por termo que combina melhor com doc-1
        payload = {"question": "Como fazer busca de similaridade no RAG com FastAPI?", "top_k": 3}
        resp = await client.post("/v1/rag/query", json=payload)

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "hits" in data
    hits = data["hits"]
    assert 1 <= len(hits) <= 3
    # Primeiro resultado deve ser de doc-1 (termos mais correlatos)
    assert hits[0]["document_id"] == "doc-1"
    assert isinstance(hits[0]["score"], float)
    assert "similaridade" in hits[0]["content"] or "arquitetura" in hits[0]["content"]


@pytest.mark.asyncio
async def test_rag_query_empty_question_returns_empty_list() -> None:
    base_container: Container = build_container()
    app = create_app(container=base_container)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/v1/rag/query", json={"question": "   ", "top_k": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["hits"] == []
