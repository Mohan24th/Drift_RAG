import json
import time
from pathlib import Path

import numpy as np
import pymupdf

from app.ingestion.chunker import chunk_text
from app.retrieval.embeddings import EmbeddingModel

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "test_documents"
BENCHMARK = ROOT / "evaluation" / "datasets" / "retrieval_benchmark.json"
OUTPUT = ROOT / "evaluation" / "results" / "local_retrieval_comparison.json"

CONFIGS = [(100, 20), (500, 100)]
TOP_K = 5

def extract_pdf(path):
    with pymupdf.open(path) as doc:
        return "\n\n".join(page.get_text() for page in doc).strip()

def main():
    benchmark = json.loads(BENCHMARK.read_text())
    questions = [q["question"] for q in benchmark["queries"]]

    documents = []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        text = extract_pdf(pdf)
        if text:
            documents.append((pdf.name, text))

    if not documents:
        raise SystemExit(f"No readable PDF text found in {PDF_DIR}")

    print(f"Loading embedding model and embedding {len(questions)} questions...")
    model = EmbeddingModel()
    query_vectors = model.encode(questions)

    output = {
        "note": (
            "Local exploratory retrieval comparison. PDFs are searched together. "
            "These rankings are not directly comparable to Supabase results, "
            "and accuracy metrics require relevance labels for these local chunks."
        ),
        "documents": [name for name, _ in documents],
        "top_k": TOP_K,
        "results": {},
    }

    for size, overlap in CONFIGS:
        chunks = []
        for filename, text in documents:
            pieces = chunk_text(
                text=text,
                source=filename,
                version="local",
                chunk_size=size,
                overlap=overlap,
            )
            for piece in pieces:
                chunks.append({
                    "file": filename,
                    "chunk_index": piece.chunk_index,
                    "text": piece.text,
                })

        if not chunks:
            continue

        print(f"\nChunk size {size}: embedding {len(chunks)} chunks...")
        chunk_vectors = model.encode([c["text"] for c in chunks])

        started = time.perf_counter()
        scores = query_vectors @ chunk_vectors.T
        retrieval_ms = (time.perf_counter() - started) * 1000

        config_results = []
        for i, question in enumerate(questions):
            top_indices = np.argsort(scores[i])[::-1][:TOP_K]
            ranked = []
            for rank, idx in enumerate(top_indices, start=1):
                item = chunks[int(idx)]
                ranked.append({
                    "rank": rank,
                    "file": item["file"],
                    "chunk_index": item["chunk_index"],
                    "score": round(float(scores[i, idx]), 5),
                    "text": item["text"],
                })

            config_results.append({
                "query_id": benchmark["queries"][i]["id"],
                "question": question,
                "top_chunks": ranked,
            })
            print(
                f"Q{i+1}: "
                + ", ".join(
                    f"{r['file']}#{r['chunk_index']} ({r['score']:.3f})"
                    for r in ranked
                )
            )

        output["results"][str(size)] = {
            "overlap": overlap,
            "chunk_count": len(chunks),
            "retrieval_scoring_ms_all_queries": round(retrieval_ms, 2),
            "queries": config_results,
        }

    OUTPUT.write_text(json.dumps(output, indent=2))
    print(f"\nSaved local comparison to: {OUTPUT}")
    print("This is exploratory; manually validate the returned passages before judging accuracy.")

if __name__ == "__main__":
    main()
