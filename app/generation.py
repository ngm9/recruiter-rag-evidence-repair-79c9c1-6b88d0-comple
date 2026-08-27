from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.retrieval import CandidateRetriever, RetrievedChunk, context_for_prompt

SYSTEM_PROMPT = """You answer recruiter questions using only the provided candidate evidence.
Cite the evidence labels that support your answer. If the evidence is not enough,
say that there is insufficient evidence rather than guessing.
"""


def mask_sensitive_text(text: str) -> str:
    return text


def build_public_payload(answer: str, chunks: list[RetrievedChunk]) -> dict[str, Any]:
    return {
        "answer": mask_sensitive_text(answer),
        "citations": [chunk.citation for chunk in chunks],
    }


def answer_question(
    question: str,
    filters: dict[str, Any] | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("A provider key is required for end-to-end generation")

    retriever = CandidateRetriever()
    chunks = retriever.retrieve(question, filters=filters, top_k=top_k)
    context = context_for_prompt(chunks)
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Evidence:\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    answer = response.choices[0].message.content or ""
    return build_public_payload(answer, chunks)
