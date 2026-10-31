import pytest
from unittest.mock import MagicMock
from app.generation.qa import RAGAnswerer
from app.generation.llm import LLM
from app.retrieval.pg_retriever import PgRetriever
from app.generation.models import RAGResponse

class MockChunk:
    def __init__(self, text, index):
        self.text = text
        self.chunk_index = index
        self.id = "chunk_id"

class MockVersion:
    def __init__(self, number):
        self.version_number = number
        self.id = "ver_id"

class MockDocument:
    def __init__(self, name):
        self.name = name
        self.id = "doc_id"

def test_impossible_budget():
    """Verify that when overhead exceeds window, system abstains and does not call LLM."""
    mock_retriever = MagicMock(spec=PgRetriever)
    mock_retriever.retrieve.return_value = [
        (MockChunk("T1", 0), MockVersion(1), MockDocument("D"), 0.9)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    # Force impossible budget: overhead > 8192
    # 4 chars per token. Overhead = 8192 * 4 = 32768 chars.
    # We'll make the question massive.
    huge_question = "A" * 35000
    
    response = answerer.answer(huge_question, "ver_1")
    
    assert "I don't have enough information" in response.answer
    assert response.sources == []
    mock_llm.generate.assert_not_called()

def test_all_chunks_truncated():
    """Verify behavior when all chunks are too large for the remaining budget."""
    mock_retriever = MagicMock(spec=PgRetriever)
    # One massive chunk
    mock_retriever.retrieve.return_value = [
        (MockChunk("A" * 10000, 0), MockVersion(1), MockDocument("D"), 0.9)
    ]
    
    mock_llm = MagicMock(spec=LLM)
    
    answerer = RAGAnswerer(mock_retriever, mock_llm)
    # Tight budget
    answerer.MAX_CONTEXT_TOKENS = 1500
    
    response = answerer.answer("Question", "ver_1")
    
    assert "I don't have enough information" in response.answer
    assert response.sources == []
    mock_llm.generate.assert_not_called()
