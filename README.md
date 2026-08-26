# Drift RAG

Drift RAG is a version-aware Retrieval-Augmented Generation system for
company knowledge bases.

The system answers questions from company documents while detecting
whether changes between document versions affect retrieval behavior or
the information being retrieved.

## Core Problem

Traditional RAG systems can continue operating after company documents
change without showing whether the knowledge used for answering questions
has changed.

Drift RAG compares document versions and measures:

- Retrieval-set drift
- Retrieval ranking drift
- Semantic/content drift

This allows organizations to identify queries affected by changes in
their knowledge base.

## Current Architecture

```text
Documents
    ↓
Ingestion
    ↓
Chunking
    ↓
Embeddings
    ↓
FAISS Vector Search
    ↓
Retrieval
    ↓
Drift Analysis
    ├── Retrieval overlap
    ├── Rank change
    └── Semantic change