from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.retrieval.hybrid_retriever import HybridRetriever, tokenize
from app.retrieval.pg_retriever import PgRetriever
from app.drift.retrieval import DriftRetriever


def result(chunk_id, text, score=0.8, version="v1"):
    return (
        SimpleNamespace(id=chunk_id, text=text, chunk_index=0),
        SimpleNamespace(id=version, version_number=1),
        SimpleNamespace(id="doc", name="Policy"),
        score,
    )


def setup_hybrid(vector=None, rows=None, rrf_k=60):
    vector_retriever = MagicMock(spec=PgRetriever)
    vector_retriever.session = MagicMock()
    vector_retriever.retrieve.return_value = vector or []
    vector_retriever.session.execute.return_value.all.return_value = rows or []
    return HybridRetriever(vector_retriever, rrf_k=rrf_k), vector_retriever


def test_tokenize_and_empty_query_handling():
    assert tokenize("Hello, POLICY!") == ["hello", "policy"]
    hybrid, vector = setup_hybrid()
    with pytest.raises(ValueError):
        hybrid.retrieve("  ")
    vector.retrieve.assert_not_called()


def test_empty_corpus_preserves_vector_results():
    expected = result("vec", "some text")
    hybrid, _ = setup_hybrid(vector=[expected])
    results = hybrid.retrieve("text")
    assert len(results) == 1
    assert results[0][0].id == "vec"
    assert results[0][3] == pytest.approx(0.8)
    assert results[0][0].rrf_score == pytest.approx(1 / 61)


def test_bm25_ranking_version_filter_and_output_contract():
    rows = [
        ("a", "alpha beta", 0, "v1", 1, "doc", "Policy"),
        ("b", "beta gamma", 1, "v1", 1, "doc", "Policy"),
    ]
    hybrid, vector = setup_hybrid(rows=rows, rrf_k=60)
    results = hybrid.retrieve("alpha", top_k=1, version_id="v1")
    assert vector.retrieve.call_args.kwargs["version_id"] == "v1"
    assert results[0][0].id == "a"
    assert len(results[0]) == 4
    assert results[0][3] is None
    assert results[0][0].rrf_score == pytest.approx(1 / 61)
    statement = vector.session.execute.call_args.args[0]
    assert statement.compile().params["id_3"] == "v1"


def test_approved_filter_is_applied_for_unscoped_search():
    hybrid, vector = setup_hybrid(rows=[("a", "alpha", 0, "v1", 1, "d", "Doc")])
    hybrid.retrieve("alpha")
    statement = vector.session.execute.call_args.args[0]
    assert statement.compile().params["status_1"] == "APPROVED"


def test_rrf_fuses_deduplicates_and_breaks_ties_by_id():
    vector_results = [result("b", "beta"), result("a", "alpha")]
    rows = [
        ("a", "alpha", 0, "v1", 1, "doc", "Policy"),
        ("c", "gamma", 0, "v1", 1, "doc", "Policy"),
    ]
    hybrid, _ = setup_hybrid(vector=vector_results, rows=rows, rrf_k=10)
    results = hybrid.retrieve("alpha", top_k=3)
    assert [item[0].id for item in results] == ["a", "b", "c"]
    # BM25 ties these two short documents at zero and uses ID as its stable tie-break.
    assert results[0][3] == pytest.approx(0.8)
    assert results[0][0].rrf_score == pytest.approx(1 / 11 + 1 / 12)
    assert results[1][3] == pytest.approx(0.8)
    assert results[1][0].rrf_score == pytest.approx(1 / 11)


def test_drift_retriever_stays_vector_only():
    _hybrid, vector_retriever = setup_hybrid(vector=[result("x", "text")])
    wrapper = DriftRetriever(vector_retriever)
    assert wrapper.retrieve("text", "v1")[0][0].id == "x"
    vector_retriever.retrieve.assert_called_once_with(
        query="text", top_k=3, version_id="v1", allow_unapproved_version=True
    )
