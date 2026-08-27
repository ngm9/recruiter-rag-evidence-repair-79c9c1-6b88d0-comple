from __future__ import annotations

import re
from types import SimpleNamespace

from app.db import execute, fetch_all
from app.evaluation import grounding_contract
from app.generation import build_public_payload
from app.ingestion import ingest_documents
from app.retrieval import CandidateRetriever

CONTACT_RE = re.compile(
    r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\+?\d[\d\s().-]{7,}\d)",
    re.IGNORECASE,
)


def reset_store() -> None:
    execute("TRUNCATE TABLE document_chunks, source_documents RESTART IDENTITY CASCADE")


def chunk_count() -> int:
    row = fetch_all("SELECT count(*) AS count FROM document_chunks")[0]
    return int(row["count"])


def test_reingesting_sources_keeps_private_chunk_store() -> None:
    reset_store()
    ingest_documents()
    first_count = chunk_count()
    ingest_documents()
    second_count = chunk_count()

    rows = fetch_all("SELECT chunk_text FROM document_chunks")
    combined_text = "\n".join(row["chunk_text"] for row in rows)

    assert first_count > 0
    assert second_count == first_count
    assert CONTACT_RE.search(combined_text) is None


def test_candidate_scope_controls_retrieved_evidence() -> None:
    reset_store()
    ingest_documents()

    retriever = CandidateRetriever()
    results = retriever.retrieve(
        "What backend Python evidence exists for Aisha Khan?",
        filters={"candidate_id": "priya-nair"},
        top_k=3,
    )

    assert results
    assert all(result.candidate_id == "priya-nair" for result in results)
    assert all(result.citation for result in results)


def test_low_evidence_queries_use_refusal_contract() -> None:
    reset_store()
    ingest_documents()

    retriever = CandidateRetriever()
    results = retriever.retrieve(
        "Does Aisha Khan have audited Salesforce compensation-plan ownership?",
        filters={"candidate_id": "aisha-khan"},
        top_k=3,
    )
    payload = grounding_contract(results, min_similarity=0.85)

    assert payload == {"answer": "Insufficient evidence", "citations": []}


def test_public_payload_masks_sensitive_contact_details() -> None:
    chunks = [
        SimpleNamespace(citation="aisha.md#chunk-0"),
        SimpleNamespace(citation="guide.md#chunk-1"),
    ]
    payload = build_public_payload(
        "Aisha can be reached at aisha.khan@example.com or +1 415-555-0188.",
        chunks,
    )

    assert CONTACT_RE.search(payload["answer"]) is None
    assert payload["citations"] == ["aisha.md#chunk-0", "guide.md#chunk-1"]
