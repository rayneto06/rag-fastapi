from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Iterable, Optional, Dict, Any, List
from dataclasses import asdict

from app.core.config import settings
from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository


class LocalDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.paths = {
            "RAW_DIR": settings.RAW_DIR,
            "PROCESSED_DIR": settings.PROCESSED_DIR,
        }

    def allocate_paths(self, original_filename: str) -> dict:
        doc_id = str(uuid.uuid4())
        safe = original_filename.replace("/", "_").replace("\\", "_")
        raw_path = settings.RAW_DIR / f"{doc_id}__{safe}"
        text_path = settings.PROCESSED_DIR / f"{doc_id}.txt"
        chunks_path = settings.PROCESSED_DIR / f"{doc_id}.chunks.jsonl"
        meta_path = settings.PROCESSED_DIR / f"{doc_id}.meta.json"
        for p in (raw_path.parent, text_path.parent):
            p.mkdir(parents=True, exist_ok=True)
        return {
            "id": doc_id,
            "raw_path": raw_path,
            "text_path": text_path,
            "chunks_path": chunks_path,
            "meta_path": meta_path,
        }

    def save_raw(self, tmp_file: Path, raw_path: Path) -> None:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_file), str(raw_path))

    def save_text(self, text: str, text_path: Path) -> None:
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(text, encoding="utf-8")

    def save_chunks(self, chunks: Iterable[dict], chunks_path: Path) -> int:
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with chunks_path.open("w", encoding="utf-8") as f:
            for ch in chunks:
                f.write(json.dumps(ch, ensure_ascii=False) + "\n")
                count += 1
        return count

    def save_meta(self, doc: Document, meta_path: Path) -> None:
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta = asdict(doc)
        meta["created_at"] = doc.created_at.isoformat()
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_meta_file(self, meta_path: Path) -> Optional[Document]:
        if not meta_path.exists():
            return None
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        try:
            return Document(
                id=data["id"],
                original_filename=data["original_filename"],
                stored_filename=data["stored_filename"],
                size_bytes=int(data["size_bytes"]),
                pages=int(data["pages"]),
                created_at=self._parse_dt(data["created_at"]),
                content_type=data.get("content_type", "application/pdf"),
            )
        except Exception:
            return None

    def list_documents(self) -> Iterable[Document]:
        for meta_file in settings.PROCESSED_DIR.glob("*.meta.json"):
            doc = self._load_meta_file(meta_file)
            if doc:
                yield doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        meta_path = settings.PROCESSED_DIR / f"{doc_id}.meta.json"
        return self._load_meta_file(meta_path)

    def count_chunks(self, doc_id: str) -> int:
        chunks_path = settings.PROCESSED_DIR / f"{doc_id}.chunks.jsonl"
        if not chunks_path.exists():
            return 0
        c = 0
        with chunks_path.open("r", encoding="utf-8") as f:
            for _ in f:
                c += 1
        return c

    @staticmethod
    def _parse_dt(s: str):
        # datetime.fromisoformat cobre o mais comum
        from datetime import datetime
        return datetime.fromisoformat(s)
