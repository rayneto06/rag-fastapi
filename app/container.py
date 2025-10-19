from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from domain.repositories.document_repository import DocumentRepository
from domain.services.chunker import Chunker
from domain.services.text_extractor import TextExtractor
from domain.services.vector_store import VectorStore
from infrastructure.chunking.simple_chunker import SimpleChunker
from infrastructure.pdf.pypdf_text_extractor import PyPDFTextExtractor
from infrastructure.storage.local_document_repository import LocalDocumentRepository
from infrastructure.vectorstores.in_memory import InMemoryVectorStore

try:
    from infrastructure.vectorstores.chroma import ChromaVectorStore
except Exception:
    ChromaVectorStore = None  # type: ignore


@dataclass
class Container:
    document_repository: DocumentRepository
    text_extractor: TextExtractor
    chunker: Chunker
    vector_store: VectorStore


def _build_vector_store() -> VectorStore:
    provider = (settings.VECTOR_STORE_PROVIDER or "inmemory").lower()
    if provider == "chroma":
        if ChromaVectorStore is None:
            # Fallback seguro caso a lib não esteja instalada
            return InMemoryVectorStore()
        return ChromaVectorStore(
            persist_directory=settings.CHROMA_DIR,
            collection_name=settings.CHROMA_COLLECTION,
        )
    # default
    return InMemoryVectorStore()


def build_container() -> Container:
    repo = LocalDocumentRepository()
    extractor = PyPDFTextExtractor()
    chunker = SimpleChunker(max_tokens=800, overlap_tokens=120)
    store = _build_vector_store()

    return Container(
        document_repository=repo,
        text_extractor=extractor,
        chunker=chunker,
        vector_store=store,
    )
