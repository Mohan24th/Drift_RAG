# Drift RAG — Chunk Size Experiment

Date: 2026-10-27
Status: Exploratory; relevance not fully validated.

## Chunking setup

| Setting | Chunk size | Overlap |
|---|---:|---:|
| A | 100 characters | 20 characters |
| B | 500 characters | 100 characters |

Source: six local PDFs in data/test_documents/.

## Results

- Size 100: 50 chunks.
- Size 500: 11 chunks.
- Reduction in chunk count: 78%.

## Retrieval observations

- Size 100 generated more granular candidates.
- Size 500 generated fewer, longer candidates.
- Similarity scores varied by question; scores alone do not establish answer accuracy.
- The local PDFs do not necessarily contain every benchmark topic.

## Artifacts

- evaluation/results/chunking_comparison.json
- evaluation/results/local_retrieval_comparison.json
- evaluation/results/retrieval_results.json
- evaluation/results/phase3_baseline.md

## Limitations and next steps

1. Inspect complete retrieved passages and manually label relevance.
2. Calculate comparable Precision@5, Recall@5, MRR and nDCG@5 on the same local dataset.
3. Evaluate answer correctness and citation faithfulness.
4. Do not re-ingest production documents based on this exploratory test alone.
