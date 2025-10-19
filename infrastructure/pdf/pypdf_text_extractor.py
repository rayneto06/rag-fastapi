from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from domain.services.text_extractor import TextExtractor


class PyPDFTextExtractor(TextExtractor):
    def extract(self, pdf_path: Path) -> tuple[str, int]:
        reader = PdfReader(str(pdf_path))
        pages = len(reader.pages)
        parts = []
        for i in range(pages):
            t = reader.pages[i].extract_text() or ""
            if t:
                parts.append(t.strip())
        return ("\n\n".join(parts), pages)
