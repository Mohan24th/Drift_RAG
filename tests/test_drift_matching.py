import pytest
from unittest.mock import MagicMock
from app.drift.analyzer import DriftAnalyzer
from app.drift.semantic import SemanticDrift

class MockChunk:
    def __init__(self, text, index):
        self.text = text
        self.chunk_index = index

def test_greedy_matching_threshold():
    mock_detector = MagicMock(spec=SemanticDrift)
    # Similarity = 1 - distance. 0.72 threshold means distance <= 0.28
    mock_detector.calculate.return_value = 0.28
    analyzer = DriftAnalyzer(mock_detector)
    
    # PgRetriever returns (chunk, version, document, score)
    v1 = [(MockChunk("A", 0), None, None, 0.9)]
    v2 = [(MockChunk("B", 0), None, None, 0.9)]
    
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 1.0
    
    mock_detector.calculate.return_value = 0.29
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 0.0

def test_greedy_suboptimality():
    mock_detector = MagicMock(spec=SemanticDrift)
    analyzer = DriftAnalyzer(mock_detector)
    
    v1 = [(MockChunk("A", 0), None, None, 0.9), (MockChunk("D", 1), None, None, 0.9)]
    v2 = [(MockChunk("B", 0), None, None, 0.9), (MockChunk("C", 1), None, None, 0.9)]
    
    def side_effect(t1, t2):
        if "A" in t1 and "B" in t2: return 0.2
        if "A" in t1 and "C" in t2: return 0.25
        if "D" in t1 and "B" in t2: return 0.1
        if "D" in t1 and "C" in t2: return 0.4
        return 1.0
        
    mock_detector.calculate.side_effect = side_effect
    report = analyzer.analyze("q", v1, v2)
    assert report.retrieval_overlap == 1.0
