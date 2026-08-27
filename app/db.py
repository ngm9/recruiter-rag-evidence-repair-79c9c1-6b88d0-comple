from __future__ import annotations

from collections.abc import Iterable, Mapping
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import get_settings


@contextmanager
def connection():
    settings = get_settings()
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(query: str, params: Iterable[Any] | Mapping[str, Any] | None = None):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()


def fetch_one(query: str, params: Iterable[Any] | Mapping[str, Any] | None = None):
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query: str, params: Iterable[Any] | Mapping[str, Any] | None = None) -> None:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def ensure_database_ready() -> None:
    row = fetch_one("SELECT 1 AS ok FROM pg_extension WHERE extname = 'vector'")
    if not row:
        raise RuntimeError("pgvector extension is not available")
    required = fetch_one(
        """
        SELECT to_regclass('public.source_documents') AS documents,
               to_regclass('public.document_chunks') AS chunks
        """
    )
    if not required or not required["documents"] or not required["chunks"]:
        raise RuntimeError("required RAG tables are missing")
