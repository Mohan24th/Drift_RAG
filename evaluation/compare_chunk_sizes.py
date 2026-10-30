import json
import statistics
from pathlib import Path

import pymupdf

from app.ingestion.chunker import chunk_text

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "test_documents"
OUTPUT = ROOT / "evaluation" / "results" / "chunking_comparison.json"

CONFIGS = [
    {"chunk_size": 100, "overlap": 20},
    {"chunk_size": 500, "overlap": 100},
]

def extract_pdf(path):
    with pymupdf.open(path) as doc:
        return "\n\n".join(page.get_text() for page in doc).strip()

def main():
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {PDF_DIR}")

    results = {
        "experiment": "Local PDF chunking comparison",
        "note": (
            "Same source PDFs; overlap is 20% of configured chunk size. "
            "This measures chunking characteristics, not retrieval quality."
        ),
        "documents": [],
    }

    for pdf in pdfs:
        text = extract_pdf(pdf)
        if not text:
            print(f"SKIP: no extractable text in {pdf.name}")
            continue

        document_result = {
            "file": pdf.name,
            "extracted_characters": len(text),
            "configs": [],
        }

        print(f"\n{pdf.name} — {len(text):,} extracted characters")

        for config in CONFIGS:
            size = config["chunk_size"]
            overlap = config["overlap"]

            chunks = chunk_text(
                text=text,
                source=pdf.stem,
                version="local-evaluation",
                chunk_size=size,
                overlap=overlap,
            )
            lengths = [len(chunk.text) for chunk in chunks]

            summary = {
                "chunk_size": size,
                "overlap": overlap,
                "chunk_count": len(chunks),
                "average_chunk_characters": (
                    round(statistics.mean(lengths), 2) if lengths else 0
                ),
                "median_chunk_characters": (
                    statistics.median(lengths) if lengths else 0
                ),
                "min_chunk_characters": min(lengths) if lengths else 0,
                "max_chunk_characters": max(lengths) if lengths else 0,
                "total_chunk_characters": sum(lengths),
            }
            document_result["configs"].append(summary)

            print(
                f"  size={size}, overlap={overlap}: "
                f"{len(chunks)} chunks, "
                f"avg={summary['average_chunk_characters']} chars, "
                f"min={summary['min_chunk_characters']}, "
                f"max={summary['max_chunk_characters']}"
            )

        results["documents"].append(document_result)

    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\nSaved comparison to: {OUTPUT}")

if __name__ == "__main__":
    main()
