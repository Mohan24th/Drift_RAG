# Drift RAG

Retrieval drift detection for continually-updated document corpora.

## Goal

Measure how changes in a document corpus affect RAG retrieval behavior.

## Core Pipeline

Documents V1/V2
→ Chunking
→ Embeddings
→ Vector Search
→ Retrieval Evaluation
→ Drift Detection
→ Drift Report