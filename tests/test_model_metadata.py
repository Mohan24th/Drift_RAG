import pytest
from unittest.mock import MagicMock, patch
from app.generation.qa import RAGAnswerer
from app.generation.llm import LLM
from app.retrieval.pg_retriever import PgRetriever

class MockChunk:
    def __init__(self, text, index):
        self.text = text; self.chunk_index = index; self.id = "cid"

class MockVersion:
    def __init__(self, number):
        self.version_number = number; self.id = "vid"

class MockDocument:
    def __init__(self, name):
        self.name = name; self.id = "did"

def test_primary_model_metadata():
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = [
        (MockChunk("Text", 0), MockVersion(1), MockDocument("Doc"), 0.9)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    # Mock LLM.generate to return (answer, model)
    mock_llm.generate.return_value = ("Answer", "primary-model-id")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert response.model_used == "primary-model-id"

def test_fallback_model_metadata():
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = [
        (MockChunk("Text", 0), MockVersion(1), MockDocument("Doc"), 0.9)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = ("Fallback Answer", "fallback-model-id")
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert response.model_used == "fallback-model-id"

def test_no_results_no_model():
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = []
    
    mock_llm = MagicMock(spec=LLM)
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    response = answerer.answer("Question", "ver_1")
    
    assert response.model_used is None
