import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation/results/local_retrieval_comparison.json"
LABELS = ROOT / "evaluation/results/local_relevance_labels.json"
OUTPUT = ROOT / "evaluation/results/local_retrieval_metrics.json"
K = 5

data = json.loads(RESULTS.read_text())
saved = json.loads(LABELS.read_text()) if LABELS.exists() else {}
all_queries = data["results"]["100"]["queries"]

def key(item):
    return f'{item["file"]}::{item["chunk_index"]}'

# Label the pooled top-five candidates from BOTH configurations.
for query in all_queries:
    qid = query["query_id"]
    question = query["question"]
    candidates = {}

    for size in ("100", "500"):
        match = next(
            q for q in data["results"][size]["queries"]
            if q["query_id"] == qid
        )
        for item in match["top_chunks"][:K]:
            candidates[key(item)] = item

    saved.setdefault(qid, {})
    pending = [
        (candidate_key, item)
        for candidate_key, item in candidates.items()
        if candidate_key not in saved[qid]
    ]

    print(f"\n{'=' * 70}\n{qid}: {question}")
    print(f"Judge {len(pending)} new passages. Type y = relevant, n = not relevant.")
    print("Relevant means the passage contains information that helps answer the question.")

    for candidate_key, item in pending:
        print(f"\n[{item['file']} | chunk {item['chunk_index']}]")
        print(item["text"])
        while True:
            answer = input("Relevant? [y/n]: ").strip().lower()
            if answer in ("y", "n"):
                break
            print("Please enter y or n.")
        saved[qid][candidate_key] = answer == "y"
        LABELS.write_text(json.dumps(saved, indent=2))

print(f"\nLabels saved: {LABELS}")

def metrics(ranked, labels):
    hits = [bool(labels.get(key(item), False)) for item in ranked[:K]]
    relevant_total = sum(labels.get(k, False) for k in labels)

    precision = sum(hits) / K
    first_rank = next((i for i, hit in enumerate(hits, 1) if hit), None)
    mrr = 1 / first_rank if first_rank else 0.0

    dcg = sum(
        1 / math.log2(rank + 1)
        for rank, hit in enumerate(hits, 1) if hit
    )
    ideal_hits = min(relevant_total, K)
    idcg = sum(1 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    ndcg = dcg / idcg if idcg else 0.0

    recall = (
        sum(hits) / relevant_total
        if relevant_total else None
    )
    return {
        "precision_at_5": round(precision, 4),
        "pooled_recall_at_5": round(recall, 4) if recall is not None else None,
        "mrr": round(mrr, 4),
        "ndcg_at_5": round(ndcg, 4),
        "relevant_in_judged_pool": relevant_total,
    }

report = {
    "note": (
        "Recall is relative to the pooled top-five candidates from both "
        "configurations, not every chunk in the corpus. Metrics depend on "
        "manual binary relevance judgments."
    ),
    "metrics": {},
}

for size in ("100", "500"):
    rows = []
    for query in data["results"][size]["queries"]:
        qid = query["query_id"]
        rows.append({
            "query_id": qid,
            **metrics(query["top_chunks"], saved.get(qid, {})),
        })

    report["metrics"][size] = {
        "chunk_count": data["results"][size]["chunk_count"],
        "per_query": rows,
        "means": {},
    }

    for metric in (
        "precision_at_5", "pooled_recall_at_5", "mrr", "ndcg_at_5"
    ):
        values = [
            row[metric] for row in rows if row[metric] is not None
        ]
        report["metrics"][size]["means"][metric] = (
            round(sum(values) / len(values), 4) if values else None
        )

OUTPUT.write_text(json.dumps(report, indent=2))
print(f"\nMetrics saved: {OUTPUT}")
print("\nPRELIMINARY COMPARISON")
for size in ("100", "500"):
    result = report["metrics"][size]
    print(f"\nChunk size {size} ({result['chunk_count']} chunks)")
    for name, value in result["means"].items():
        print(f"  {name}: {value}")
print("\nRecall is pooled recall, not full-corpus recall.")
