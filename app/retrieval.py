from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.db import fetch_all, vector_literal
from app.embeddings import EmbeddingService


@dataclass(frozen=True)
class RetrievedChunk:
    id: int
    text: str
    similarity: float
    source_name: str
    citation: str
    candidate_id: str | None
    candidate_name: str | None
    document_type: str
    section_title: str | None


class CandidateRetriever:
    def __init__(self, embedder: EmbeddingService | None = None) -> None:
        self.embedder = embedder or EmbeddingService()

    def retrieve(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        query_vector = vector_literal(self.embedder.embed_query(query))
        rows = fetch_all(
            """
            SELECT id, chunk_text, source_name, citation_label, candidate_id,
                   candidate_name, document_type, section_title,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_vector, query_vector, top_k),
        )
        return [
            RetrievedChunk(
                id=int(row["id"]),
                text=row["chunk_text"],
                similarity=float(row["similarity"]),
                source_name=row["source_name"],
                citation=row["citation_label"],
                candidate_id=row["candidate_id"],
                candidate_name=row["candidate_name"],
                document_type=row["document_type"],
                section_title=row["section_title"],
            )
            for row in rows
        ]


def context_for_prompt(chunks: list[RetrievedChunk], token_budget: int = 900) -> str:
    lines: list[str] = []
    used = 0
    for chunk in chunks:
        estimate = max(1, len(chunk.text.split()))
        if used + estimate > token_budget:
            break
        used += estimate
        lines.append(f"[{chunk.citation}] {chunk.text}")
    return "\n\n".join(lines)
