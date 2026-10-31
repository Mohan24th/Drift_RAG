import pytest
from app.drift.report import DriftReport
from app.drift.summary import create_summary, calculate_overall_score, classify_drift
from app.drift.analyzer import DriftAnalyzer
from unittest.mock import MagicMock

def test_identical_versions_math():
    # V1: [A], V2: [A]
    # overlap = 1/1 = 1.0
    # rank_change = 0/1 = 0.0
    # semantic_change = (0.0)/1 = 0.0
    report = DriftReport(
        query="test",
        retrieval_overlap=1.0,
        rank_change=0.0,
        semantic_change=0.0,
        changes=[]
    )
    assert report.retrieval_drift == 0.0
    assert report.content_drift == 0.0
    assert report.composite_drift_score == 0.0

def test_single_added_chunk_math():
    # V1: [A], V2: [A, B]
    # overlap = 1/2 = 0.5
    # rank_change = 0.0 (A matches A at rank 1)
    # semantic_change = (0.0 [A match] + 1.0 [B unmatched]) / 2 = 0.5
    report = DriftReport(
        query="test",
        retrieval_overlap=0.5,
        rank_change=0.0,
        semantic_change=0.5,
        changes=[]
    )
    # Retrieval Drift = ( (1-0.5) + 0 ) / 2 = 0.25
    assert report.retrieval_drift == 0.25
    # Content Drift = max(0, 0.5) = 0.5
    assert report.content_drift == 0.5
    # Composite = (0.25 + 0.5) / 2 = 0.375
    assert report.composite_drift_score == 0.375

def test_global_summary_calculation():
    # Report 1: overlap=1.0, semantic=0.0
    # Report 2: overlap=0.5, semantic=0.5
    r1 = DriftReport("q1", 1.0, 0.0, 0.0, [])
    r2 = DriftReport("q2", 0.5, 0.0, 0.5, [])
    
    summary = create_summary([r1, r2])
    
    # avg_retrieval_drift = ((1-1.0) + (1-0.5)) / 2 = (0 + 0.5) / 2 = 0.25
    # avg_content_drift = (0.0 + 0.5) / 2 = 0.25
    # overall = (0.25 + 0.25) / 2 = 0.25
    assert summary.overall_score == 0.25
    assert summary.overall_level == "MEDIUM" # 0.1 <= 0.25 < 0.3

def test_extreme_cases():
    # Both empty
    # Based on analyzer: max_chunks=0 -> overlap=1.0. semantic=0.0
    r_empty = DriftReport("q", 1.0, 0.0, 0.0, [])
    assert r_empty.composite_drift_score == 0.0
    
    # Only V1 populated (1 chunk)
    # overlap = 0/1 = 0.0. semantic = 1.0/1 = 1.0
    r_v1_only = DriftReport("q", 0.0, 0.0, 1.0, [])
    # retrieval_drift = (1-0 + 0)/2 = 0.5
    # content_drift = 1.0
    # composite = (0.5 + 1.0)/2 = 0.75
    assert r_v1_only.composite_drift_score == 0.75
