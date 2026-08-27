CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS source_documents (
    id BIGSERIAL PRIMARY KEY,
    source_path TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    candidate_id TEXT,
    candidate_name TEXT,
    source_version TEXT,
    raw_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_sha256 TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    candidate_id TEXT,
    candidate_name TEXT,
    document_type TEXT NOT NULL,
    section_title TEXT,
    citation_label TEXT,
    token_estimate INTEGER NOT NULL DEFAULT 0,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_documents_candidate ON source_documents(candidate_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_candidate ON document_chunks(candidate_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_type ON document_chunks(document_type);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
