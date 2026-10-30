# Drift RAG — Phase 3 Retrieval Baseline

Date: 2026-10-27
Status: Preliminary; relevance labels require validation.

## Metrics

| Metric | Baseline |
|---|---:|
| Precision@5 | 0.7333 |
| Recall@5 | 1.0000 |
| MRR | 0.8750 |
| nDCG@5 | 0.9154 |
| Mean latency (ms) | 378.81 |
| Median latency (ms) | 143.38 |
| Retrieval calls | 12 |
| Queries evaluated | 6 across V1 and V2 |

## Files

- Benchmark: evaluation/datasets/retrieval_benchmark.json
- Detailed results: evaluation/results/retrieval_results.json

## Limitations

Relevance labels are provisional and require manual verification.
The first retrieval call took approximately 2.86 seconds, likely due to
initialization or warm-up. Do not use mean latency as steady-state latency.

## Next experiments

1. Verify relevance labels against full retrieved chunk text.
2. Compare chunk sizes 100 and 500 using the same source documents and queries.
3. Record metrics, latency, chunk counts, and experiment configuration.
4. Do not change production Supabase documents until evaluation is complete.
