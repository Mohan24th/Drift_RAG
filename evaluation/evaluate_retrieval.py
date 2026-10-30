import json
import statistics
import time
from pathlib import Path

from app.database.connection import SessionLocal
from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.pg_retriever import PgRetriever


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "datasets" / "retrieval_benchmark.json"
OUTPUT = ROOT / "results" / "retrieval_results.json"


def precision_at_k(retrieved, relevant, k):
    if k == 0:
        return 0.0
    return sum(i in relevant for i in retrieved[:k]) / k


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        return None
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def reciprocal_rank(retrieved, relevant):
    for rank, index in enumerate(retrieved, start=1):
        if index in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved, relevant, k):
    dcg = sum(
        1.0 / __import__("math").log2(rank + 1)
        for rank, index in enumerate(retrieved[:k], start=1)
        if index in relevant
    )
    ideal_hits = min(len(relevant), k)
    idcg = sum(
        1.0 / __import__("math").log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )
    return dcg / idcg if idcg else None


def main():
    config = json.loads(DATASET.read_text())
    top_k = int(config.get("top_k", 5))
    model = EmbeddingModel()
    results = []
    latencies = []

    session = SessionLocal()
    try:
        retriever = PgRetriever(session, model)

        for query in config["queries"]:
            for version_number, version_id in config["versions"].items():
                started = time.perf_counter()
                found = retriever.retrieve(
                    query=query["question"],
                    top_k=top_k,
                    version_id=version_id,
                )
                elapsed_ms = (time.perf_counter() - started) * 1000
                latencies.append(elapsed_ms)

                chunks = [
                    {
                        "rank": rank,
                        "chunk_index": chunk.chunk_index,
                        "score": round(score, 6),
                        "text": chunk.text,
                    }
                    for rank, (chunk, version, document, score)
                    in enumerate(found, start=1)
                ]

                raw_labels = query["relevant_chunk_indices"].get(
                    version_number, []
                )
                relevant = {int(i) for i in raw_labels}
                retrieved = [item["chunk_index"] for item in chunks]

                entry = {
                    "query_id": query["id"],
                    "question": query["question"],
                    "version_number": int(version_number),
                    "version_id": version_id,
                    "latency_ms": round(elapsed_ms, 2),
                    "retrieved_chunks": chunks,
                    "labels_complete": bool(relevant),
                }

                if relevant:
                    entry["metrics"] = {
                        f"precision_at_{top_k}": round(
                            precision_at_k(retrieved, relevant, top_k), 4
                        ),
                        f"recall_at_{top_k}": round(
                            recall_at_k(retrieved, relevant, top_k), 4
                        ),
                        "mrr": round(
                            reciprocal_rank(retrieved, relevant), 4
                        ),
                        f"ndcg_at_{top_k}": (
                            round(ndcg_at_k(retrieved, relevant, top_k), 4)
                            if ndcg_at_k(retrieved, relevant, top_k) is not None
                            else None
                        ),
                    }

                results.append(entry)
                print(
                    f"{query['id']} | V{version_number} | "
                    f"{elapsed_ms:.1f} ms | "
                    f"top chunks: {retrieved}"
                )

    finally:
        session.close()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2))

    print(f"\nSaved detailed results to: {OUTPUT}")
    print(f"Retrieval calls: {len(results)}")
    if latencies:
        print(f"Mean latency: {statistics.mean(latencies):.2f} ms")
        print(f"Median latency: {statistics.median(latencies):.2f} ms")

    labeled = [r for r in results if "metrics" in r]
    print(f"Queries with relevance labels: {len(labeled)}/{len(results)}")
    if not labeled:
        print(
            "Metrics not calculated yet. Inspect retrieved chunks, "
            "then fill relevant_chunk_indices in the benchmark JSON."
        )
    else:
        metric_names = list(labeled[0]["metrics"])
        for name in metric_names:
            values = [
                r["metrics"][name]
                for r in labeled
                if r["metrics"].get(name) is not None
            ]
            if values:
                print(f"Mean {name}: {statistics.mean(values):.4f}")


if __name__ == "__main__":
    main()
