def top_k_overlap(
    v1_chunks: list[str],
    v2_chunks: list[str],
) -> float:
    """
    Calculate the proportion of V1 retrieved chunks
    that are also present in V2 retrieval results.
    """

    if not v1_chunks:
        return 0.0

    common_chunks = set(v1_chunks) & set(v2_chunks)

    return len(common_chunks) / len(v1_chunks)

def mean_rank_change(
    v1_chunks: list[str],
    v2_chunks: list[str],
) -> float:
    """
    Calculate the average normalized rank change
    for chunks appearing in both retrieval lists.

    Returns a value between 0 and 1.

    0 = no rank change
    1 = maximum rank change
    """

    if not v1_chunks or not v2_chunks:
        return 1.0

    v1_ranks = {
        chunk_id: rank
        for rank, chunk_id in enumerate(v1_chunks, start=1)
    }

    v2_ranks = {
        chunk_id: rank
        for rank, chunk_id in enumerate(v2_chunks, start=1)
    }

    common_chunks = set(v1_ranks) & set(v2_ranks)

    if not common_chunks:
        return 1.0

    max_rank = max(
        len(v1_chunks),
        len(v2_chunks),
    )

    rank_changes = []

    for chunk_id in common_chunks:
        difference = abs(
            v1_ranks[chunk_id]
            - v2_ranks[chunk_id]
        )

        rank_changes.append(
            difference / max_rank
        )

    return sum(rank_changes) / len(rank_changes)