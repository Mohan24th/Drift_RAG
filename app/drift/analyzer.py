
from app.drift.report import DriftChange, DriftReport
from app.drift.semantic import SemanticDrift


class DriftAnalyzer:
    """Compare retrieved chunks across two document versions."""

    MATCH_THRESHOLD = 0.72
    CONTENT_CHANGE_THRESHOLD = 0.05

    def __init__(self, semantic_detector: SemanticDrift):
        self.semantic_detector = semantic_detector

    def analyze(self, query, v1_results, v2_results) -> DriftReport:
        v1_chunks = [chunk for chunk, _ in v1_results]
        v2_chunks = [chunk for chunk, _ in v2_results]

        candidates = []

        for i, chunk1 in enumerate(v1_chunks):
            for j, chunk2 in enumerate(v2_chunks):
                distance = float(
                    self.semantic_detector.calculate(
                        chunk1.text, chunk2.text
                    )
                )
                distance = min(1.0, max(0.0, distance))
                similarity = 1.0 - distance

                if similarity >= self.MATCH_THRESHOLD:
                    candidates.append((similarity, i, j, distance))

        # Match each chunk at most once, preferring the closest pair.
        candidates.sort(key=lambda item: item[0], reverse=True)

        matched_v1 = set()
        matched_v2 = set()
        matches = []

        for similarity, i, j, distance in candidates:
            if i in matched_v1 or j in matched_v2:
                continue

            matched_v1.add(i)
            matched_v2.add(j)
            matches.append((i, j, distance))

        max_chunks = max(len(v1_chunks), len(v2_chunks))
        retrieval_overlap = (
            len(matches) / max_chunks if max_chunks else 1.0
        )

        if matches:
            max_rank = max(len(v1_chunks), len(v2_chunks), 1)
            rank_change = sum(
                abs(i - j) / max_rank for i, j, _ in matches
            ) / len(matches)
        else:
            rank_change = 0.0

        changes = []

        # Matched chunks contribute their semantic distance.
        semantic_change_total = sum(
            distance for _, _, distance in matches
        )
        comparison_count = len(matches)

        for i, j, distance in matches:
            chunk1 = v1_chunks[i]
            chunk2 = v2_chunks[j]

            if distance > self.CONTENT_CHANGE_THRESHOLD:
                changes.append(
                    DriftChange(
                        chunk_index=chunk1.chunk_index,
                        v1_text=chunk1.text,
                        v2_text=chunk2.text,
                        change_type="CONTENT",
                    )
                )

        # Unmatched chunks count as content changes as well as
        # retrieval differences.
        for i, chunk in enumerate(v1_chunks):
            if i not in matched_v1:
                changes.append(
                    DriftChange(
                        chunk_index=chunk.chunk_index,
                        v1_text=chunk.text,
                        v2_text="",
                        change_type="REMOVED",
                    )
                )
                semantic_change_total += 1.0
                comparison_count += 1

        for j, chunk in enumerate(v2_chunks):
            if j not in matched_v2:
                changes.append(
                    DriftChange(
                        chunk_index=chunk.chunk_index,
                        v1_text="",
                        v2_text=chunk.text,
                        change_type="ADDED",
                    )
                )
                semantic_change_total += 1.0
                comparison_count += 1

        semantic_change = (
            semantic_change_total / comparison_count
            if comparison_count
            else 0.0
        )

        return DriftReport(
            query=query,
            retrieval_overlap=retrieval_overlap,
            rank_change=rank_change,
            semantic_change=semantic_change,
            changes=changes,
        )
