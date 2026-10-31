-- Index for fast filtering of chunks by version (CRITICAL for retrieval)
CREATE INDEX IF NOT EXISTS idx_chunks_version_id ON chunks (version_id);

-- Composite index for optimized lookup of the latest approved version of a document
-- This supports both specific document lookups and "latest approved" queries
CREATE INDEX IF NOT EXISTS idx_doc_versions_composite 
ON document_versions (document_id, status, version_number DESC);
