import pytest
from unittest.mock import MagicMock
from app.drift.analyzer import DriftAnalyzer
from app.drift.semantic import SemanticDrift
from app.drift.report import DriftReport
from app.drift.summary import create_summary

class MockChunk:
    def __init__(self, text, index):
        self.text = text
        self.chunk_index = index

def test_deterministic_math_identical():
    mock_detector = MagicMock(spec=SemanticDrift)
    mock_detector.calculate.return_value = 0.0
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("Text A", 0), None, None, 0.9)]
    v2 = [(MockChunk("Text A", 0), None, None, 0.9)]
    
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 1.0
    assert report.rank_change == 0.0
    assert report.semantic_change == 0.0
    assert report.composite_drift_score == 0.0

def test_deterministic_math_added_chunk():
    mock_detector = MagicMock(spec=SemanticDrift)
    def side_effect(t1, t2):
        return 0.0 if t1 == t2 else 1.0
    mock_detector.calculate.side_effect = side_effect
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("A", 0), None, None, 0.9)]
    v2 = [(MockChunk("A", 0), None, None, 0.9), (MockChunk("B", 1), None, None, 0.8)]
    
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 0.5
    assert report.rank_change == 0.0
    assert report.semantic_change == 0.5
    assert report.composite_drift_score == 0.375

def test_deterministic_math_reordered():
    mock_detector = MagicMock(spec=SemanticDrift)
    def side_effect(t1, t2):
        return 0.0 if t1 == t2 else 1.0
    mock_detector.calculate.side_effect = side_effect
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("A", 0), None, None, 0.9), (MockChunk("B", 1), None, None, 0.8)]
    v2 = [(MockChunk("B", 0), None, None, 0.9), (MockChunk("A", 1), None, None, 0.8)]
    
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 1.0
    # Rank changes: A(0->1), B(1->0). max_rank = 2.
    # (|0-1|/2 + |1-0|/2) / 2 = (0.5 + 0.5) / 2 = 0.5
    assert report.rank_change == 0.5
    assert report.semantic_change == 0.0
    assert report.composite_drift_score == 0.125

def test_greedy_suboptimality_evidence():
    mock_detector = MagicMock(spec=SemanticDrift)
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("A", 0), None, None, 0.9), (MockChunk("D", 1), None, None, 0.9)]
    v2 = [(MockChunk("B", 0), None, None, 0.9), (MockChunk("C", 1), None, None, 0.9)]
    
    def side_effect(t1, t2):
        if "A" in t1 and "B" in t2: return 0.2 # sim 0.8
        if "A" in t1 and "C" in t2: return 0.25 # sim 0.75
        if "D" in t1 and "B" in t2: return 0.1 # sim 0.9
        if "D" in t1 and "C" in t2: return 0.4 # sim 0.6
        return 1.0
    mock_detector.calculate.side_effect = side_effect
    
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 1.0

def test_boundary_sensitivity_simulation():
    mock_detector = MagicMock(spec=SemanticDrift)
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("The policy says A B", 0), None, None, 0.9)]
    v2 = [(MockChunk("The policy says A", 0), None, None, 0.9), (MockChunk("B", 1), None, None, 0.9)]
    
    mock_detector.calculate.return_value = 0.3 # sim 0.7
    report = analyzer.analyze("q", v1, v2)
    
    assert report.retrieval_overlap == 0.0
    assert len(report.changes) == 3 # 1 removed, 2 added
