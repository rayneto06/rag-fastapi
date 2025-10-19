from __future__ import annotations

from typing import Any, Dict, Iterator, List

from domain.services.chunker import Chunker


class SimpleChunker(Chunker):
    def __init__(self, max_tokens: int = 800, overlap_tokens: int = 120) -> None:
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def _split_paragraphs(self, text: str) -> List[str]:
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        return blocks if blocks else [text]

    def chunk(self, text: str) -> Iterator[Dict[str, Any]]:
        if not text.strip():
            return

        paras = self._split_paragraphs(text)
        words: List[str] = []
        for p in paras:
            words.extend(p.split())
            words.append("\n\n")

        if words and words[-1] == "\n\n":
            words = words[:-1]

        start = 0
        n = len(words)
        while start < n:
            end = min(start + self.max_tokens, n)
            piece = words[start:end]
            content = " ".join(piece).replace(" \n\n ", "\n\n").strip()
            if content:
                yield {"content": content, "offset_start": start, "offset_end": end}
            if end >= n:
                break
            start = max(0, end - self.overlap_tokens)
