from app.drift.metrics import (
    top_k_overlap,
    mean_rank_change,
)


def main():
    examples = [
        (
            ["A", "B", "C"],
            ["A", "B", "C"],
        ),
        (
            ["A", "B", "C"],
            ["A", "B", "D"],
        ),
        (
            ["A", "B", "C"],
            ["C", "B", "A"],
        ),
    ]

    for v1, v2 in examples:
        print("\nV1:", v1)
        print("V2:", v2)

        overlap = top_k_overlap(v1, v2)
        rank_change = mean_rank_change(v1, v2)

        print(f"Top-K overlap: {overlap:.2f}")
        print(f"Mean rank change: {rank_change:.2f}")


if __name__ == "__main__":
    main()