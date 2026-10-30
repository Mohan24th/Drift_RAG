
from app.drift.analyzer import DriftAnalyzer
from app.ingestion.chunker import Chunk


class FakeSemanticDrift:
    def __init__(self, distances=None):
        self.distances = distances or {}

    def calculate(self, v1_text, v2_text):
        if v1_text == v2_text:
            return 0.0
        return self.distances.get((v1_text, v2_text), 1.0)


def make_chunk(text, index):
    return Chunk(
        chunk_id=f"test-{index}",
        text=text,
        source="policy.txt",
        version="v1",
        chunk_index=index,
    )


def make_analyzer(distances=None):
    return DriftAnalyzer(FakeSemanticDrift(distances))


def test_unchanged_chunks_have_zero_drift():
    chunks = [make_chunk("Annual leave is 20 days.", 0)]

    report = make_analyzer().analyze(
        "annual leave",
        [(chunks[0], 0.95)],
        [(chunks[0], 0.95)],
    )

    assert report.retrieval_overlap == 1.0
    assert report.rank_change == 0.0
    assert report.semantic_change == 0.0
    assert report.changes == []


def test_modified_chunk_contributes_semantic_drift():
    old = make_chunk("Annual leave is 20 days.", 0)
    new = make_chunk("Annual leave is 25 days.", 0)

    analyzer = make_analyzer({
        (old.text, new.text): 0.2,
    })

    report = analyzer.analyze(
        "annual leave",
        [(old, 0.95)],
        [(new, 0.95)],
    )

    assert report.retrieval_overlap == 1.0
    assert report.semantic_change == 0.2
    assert len(report.changes) == 1
    assert report.changes[0].change_type == "CONTENT"


def test_added_chunk_contributes_semantic_drift():
    new = make_chunk("Employees may work remotely.", 0)

    report = make_analyzer().analyze(
        "remote work",
        [],
        [(new, 0.95)],
    )

    assert report.retrieval_overlap == 0.0
    assert report.semantic_change == 1.0
    assert len(report.changes) == 1
    assert report.changes[0].change_type == "ADDED"


def test_removed_chunk_contributes_semantic_drift():
    old = make_chunk("Employees receive 20 leave days.", 0)

    report = make_analyzer().analyze(
        "annual leave",
        [(old, 0.95)],
        [],
    )

    assert report.retrieval_overlap == 0.0
    assert report.semantic_change == 1.0
    assert len(report.changes) == 1
    assert report.changes[0].change_type == "REMOVED"


def test_empty_results_have_zero_semantic_drift():
    report = make_analyzer().analyze("policy question", [], [])

    assert report.retrieval_overlap == 1.0
    assert report.rank_change == 0.0
    assert report.semantic_change == 0.0
    assert report.changes == []
