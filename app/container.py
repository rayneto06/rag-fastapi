from __future__ import annotations
from dataclasses import dataclass

from domain.repositories.document_repository import DocumentRepository
from domain.services.chunker import Chunker
from domain.services.text_extractor import TextExtractor
from domain.services.vector_store import VectorStore

from infrastructure.storage.local_document_repository import LocalDocumentRepository
from infrastructure.pdf.pypdf_text_extractor import PyPDFTextExtractor
from infrastructure.chunking.simple_chunker import SimpleChunker
from infrastructure.vectorstores.in_memory import InMemoryVectorStore


@dataclass
class Container:
    document_repository: DocumentRepository
    text_extractor: TextExtractor
    chunker: Chunker
    vector_store: VectorStore


def build_container() -> Container:
    repo = LocalDocumentRepository()
    extractor = PyPDFTextExtractor()
    chunker = SimpleChunker(max_tokens=800, overlap_tokens=120)
    store = InMemoryVectorStore()  # por enquanto em memória

    return Container(
        document_repository=repo,
        text_extractor=extractor,
        chunker=chunker,
        vector_store=store,
    )
