from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    id: str
    original_filename: str
    stored_filename: str
    size_bytes: int
    pages: int
    created_at: datetime
    content_type: str = "application/pdf"

    @property
    def is_pdf(self) -> bool:
        return self.content_type == "application/pdf" or self.stored_filename.lower().endswith(
            ".pdf"
        )
