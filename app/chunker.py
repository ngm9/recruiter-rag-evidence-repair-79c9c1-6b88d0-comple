from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    section_title: str | None = None
    token_estimate: int = 0


def split_text(text: str, max_words: int = 90, overlap_words: int = 0) -> list[TextChunk]:
    words = text.split()
    if not words:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    step = max(1, max_words - max(0, overlap_words))

    while start < len(words):
        end = min(start + max_words, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append(
            TextChunk(
                index=index,
                text=chunk_text,
                section_title=_section_hint(chunk_text),
                token_estimate=max(1, int(len(chunk_words) * 1.3)),
            )
        )
        index += 1
        start += step

    return chunks


def _section_hint(text: str) -> str | None:
    for marker in ("Experience", "Skills", "Interview", "Notes"):
        if marker.lower() in text.lower():
            return marker
    return None
