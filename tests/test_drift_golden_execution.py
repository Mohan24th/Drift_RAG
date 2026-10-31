from unittest.mock import MagicMock

from app.drift.analyzer import DriftAnalyzer
from app.drift.semantic import SemanticDrift


class MockChunk:
    def __init__(self, text, index):
        self.text = text
        self.chunk_index = index
        self.id = f"chunk-{index}"


def make_analyzer(similarity=0.0):
    detector = MagicMock(spec=SemanticDrift)
    detector.calculate.return_value = similarity
    return DriftAnalyzer(detector)


def test_identical_versions_have_no_drift():
    chunk = MockChunk("Same policy text", 0)

    report = make_analyzer().analyze(
        "policy question",
        [(chunk, None, None, 0.9)],
        [(chunk, None, None, 0.9)],
    )

    assert report.retrieval_overlap == 1.0
    assert report.rank_change == 0.0
    assert report.semantic_change == 0.0
    assert report.composite_drift_score == 0.0


def test_added_chunk_changes_retrieval_and_semantic_drift():
    analyzer = make_analyzer()

    report = analyzer.analyze(
        "policy question",
        [(MockChunk("Existing text", 0), None, None, 0.9)],
        [
            (MockChunk("Existing text", 0), None, None, 0.9),
            (MockChunk("New text", 1), None, None, 0.8),
        ],
    )

    assert report.retrieval_overlap == 0.5
    assert report.semantic_change == 0.5
    assert report.composite_drift_score == 0.375


def test_reordered_chunks_change_rank_only():
    analyzer = make_analyzer()
    analyzer.semantic_detector.calculate.side_effect = (
        lambda old, new: 0.0 if old == new else 1.0
    )
    report = analyzer.analyze(
        "policy question",
        [
            (MockChunk("A", 0), None, None, 0.9),
            (MockChunk("B", 1), None, None, 0.8),
        ],
        [
            (MockChunk("B", 1), None, None, 0.9),
            (MockChunk("A", 0), None, None, 0.8),
        ],
    )

    assert report.retrieval_overlap == 1.0
    assert report.rank_change == 0.5
    assert report.semantic_change == 0.0
    assert report.composite_drift_score == 0.125


def test_boundary_sensitivity_records_removed_and_added_chunks():
    report = make_analyzer(similarity=0.3).analyze(
        "policy question",
        [(MockChunk("The policy says A B", 0), None, None, 0.9)],
        [
            (MockChunk("The policy says A", 0), None, None, 0.9),
            (MockChunk("B", 1), None, None, 0.9),
        ],
    )

    assert report.retrieval_overlap == 0.0
    assert len(report.changes) == 3
