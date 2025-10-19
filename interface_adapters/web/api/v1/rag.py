from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.container import Container
from use_cases.query_rag import QueryRAG, QueryRAGInput


class RAGQueryRequest(BaseModel):
    question: str = Field(..., description="Pergunta do usuário.")
    top_k: int = Field(5, ge=1, le=50, description="Quantidade de chunks a retornar (1..50).")


class RAGQueryHit(BaseModel):
    score: float
    document_id: str
    content: str
    chunk_id: str | None = None
    metadata: dict = {}


class RAGQueryResponse(BaseModel):
    hits: list[RAGQueryHit]


def get_router(container: Container) -> APIRouter:
    router = APIRouter(prefix="/rag", tags=["rag"])

    @router.post("/query", response_model=RAGQueryResponse, status_code=status.HTTP_200_OK)
    def rag_query(payload: RAGQueryRequest) -> RAGQueryResponse:
        """
        Consulta RAG (apenas retrieval). Retorna os *chunks* mais similares.
        """
        usecase = QueryRAG(store=container.vector_store)
        result = usecase.execute(QueryRAGInput(question=payload.question, top_k=payload.top_k))
        return RAGQueryResponse(
            hits=[
                RAGQueryHit(
                    score=h.score,
                    document_id=h.document_id,
                    content=h.content,
                    chunk_id=h.chunk_id,
                    metadata=h.metadata,
                )
                for h in result.hits
            ]
        )

    return router
